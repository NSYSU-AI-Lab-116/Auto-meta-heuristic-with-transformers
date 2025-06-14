#include <pybind11/pybind11.h>
#include <pybind11/numpy.h>
#include <Eigen/Dense>
#include <random>
#include <limits>
#include <vector>
#include <chrono>
#include <iostream>

//using namespace std; // error (maybe)
namespace py = pybind11;
using Matrix = Eigen::Matrix<double, Eigen::Dynamic, Eigen::Dynamic, Eigen::RowMajor>;

py::tuple run(int max_iter,int dim,py::function obj_func,int num_pop,double lb,double ub,py::array_t<double> cats_in)
{
    auto buf = cats_in.unchecked<2>();
    Matrix cats(num_pop, dim);
    for(int i = 0; i < num_pop; i++)
    {
        for(int j = 0; j < dim; j++)
            cats(i, j) = buf(i, j);
    }

    std::mt19937_64 rng(std::chrono::high_resolution_clock::now().time_since_epoch().count());
    std::uniform_real_distribution<double> uni(0.0, 1.0);

    Eigen::RowVectorXd best_cat(dim);
    double best_score = std::numeric_limits<double>::infinity();

    for(int i = 0; i < num_pop; i++)
    {
        py::array_t<double> arr({dim}, cats.data() + i*dim);
        double f = obj_func(arr).cast<double>();
        if(f < best_score)
        {
            best_score = f;
            best_cat = cats.row(i);
        }
    }

    std::vector<double> curve;
    curve.reserve(max_iter);

    for(int t = 0; t < max_iter; t++)
    {
        for(int i = 0; i < num_pop; i++)
        {
            py::array_t<double> arr({dim}, cats.data() + i*dim);
            double f = obj_func(arr).cast<double>();
            if(f < best_score)
            {
                best_score = f;
                best_cat = cats.row(i);
            }
        }
        double rG = 2 - 2.0 * t / max_iter;
        double R  = 2 * rG * uni(rng) - rG;

        for(int i = 0; i < num_pop; i++)
        {
            double r     = rG * uni(rng);
            double theta = std::uniform_real_distribution<double>(-M_PI, M_PI)(rng);
            Eigen::RowVectorXd new_pos(dim);
            if(std::abs(R) <= 1)
                new_pos = best_cat - r * uni(rng) * (best_cat - cats.row(i)) * std::cos(theta);
            else
                new_pos = r * (best_cat - uni(rng) * cats.row(i));

            for(int j = 0; j < dim; j++)
            {
                if(new_pos(j) < lb) 
                    new_pos(j) = lb;
                if(new_pos(j) > ub) 
                    new_pos(j) = ub;
            }
            cats.row(i) = new_pos;
        }

        cats.row(num_pop - 1) = best_cat;
        curve.push_back(best_score);
    }

    auto cats_out = py::array_t<double>({num_pop, dim}, {sizeof(double)*dim, sizeof(double)}, cats.data());
    auto curve_out = py::array_t<double>(curve.size(), curve.data());
    return py::make_tuple(cats_out, curve_out);
}

PYBIND11_MODULE(SCSO_cpp, m)
{
    m.doc() = "Sand Cat Swarm Optimization core accelerated with C++";
    m.def("run", &run,
          py::arg("max_iter"),
          py::arg("dim"),
          py::arg("obj_func"),
          py::arg("num_pop"),
          py::arg("lb"),
          py::arg("ub"),
          py::arg("cats_in"));
}
