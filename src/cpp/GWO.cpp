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

py::tuple run(int max_iter, int dim, py::function obj_function, int num_wolves, double lb, double ub, py::array_t<double> wolves_in)
{
    Matrix wolves(num_wolves, dim);
    auto buf = wolves_in.unchecked<2>();
    for(int i = 0; i < num_wolves; i++)
    {
        for(int j = 0; j < dim; j++)
            wolves(i, j) = buf(i, j);
    }

    std::mt19937_64 rng(std::chrono::high_resolution_clock::now().time_since_epoch().count());
    std::uniform_real_distribution<double> uni01(0.0, 1.0);

    Matrix alpha(1, dim), beta(1, dim), delta(1, dim);
    double alpha_score = std::numeric_limits<double>::infinity();
    double beta_score = std::numeric_limits<double>::infinity();
    double delta_score = std::numeric_limits<double>::infinity();

    std::vector<double> curve;
    curve.reserve(max_iter);

    for(int t = 0; t < max_iter; ++t)
    {
        for(int i = 0; i < num_wolves; i++)
        {
            py::array_t<double> wolf_arr({dim}, wolves.data() + i * dim);
            double fitness = obj_function(wolf_arr).cast<double>();
            if(fitness < alpha_score)
            {
                delta_score = beta_score; 
                delta = beta;
                beta_score  = alpha_score; 
                beta  = alpha;
                alpha_score = fitness;       
                alpha = wolves.row(i);
            }
            else if(fitness < beta_score)
            {
                delta_score = beta_score; 
                delta = beta;
                beta_score  = fitness;      
                beta  = wolves.row(i);
            }
            else if(fitness < delta_score)
            {
                delta_score = fitness;      
                delta = wolves.row(i);
            }
        }

        double a = 2.0 - t * (2.0 / max_iter);
        for(int i = 0; i < num_wolves; i++)
        {
            double r1 = uni01(rng), r2 = uni01(rng);
            double A1 = 2.0 * a * r1 - a, C1 = 2.0 * r2;
            Matrix D1 = (C1 * alpha - wolves.row(i)).cwiseAbs();
            Matrix X1 = alpha - A1 * D1;

            r1 = uni01(rng); r2 = uni01(rng);
            double A2 = 2.0 * a * r1 - a, C2 = 2.0 * r2;
            Matrix D2 = (C2 * beta - wolves.row(i)).cwiseAbs();
            Matrix X2 = beta - A2 * D2;

            r1 = uni01(rng); r2 = uni01(rng);
            double A3 = 2.0 * a * r1 - a, C3 = 2.0 * r2;
            Matrix D3 = (C3 * delta - wolves.row(i)).cwiseAbs();
            Matrix X3 = delta - A3 * D3;

            Matrix new_pos = (X1 + X2 + X3) / 3.0;
            for(int j = 0; j < dim; j++)
            {
                double v = new_pos(0, j);
                if(v < lb) 
                    v = lb;
                if(v > ub) 
                    v = ub;
                wolves(i, j) = v;
            }
        }
        wolves.row(num_wolves - 1) = alpha;
        curve.push_back(alpha_score);
    }

    auto wolves_out = py::array_t<double>({num_wolves, dim},{sizeof(double) * dim, sizeof(double)},wolves.data());
    auto curve_out = py::array_t<double>(curve.size(), curve.data());
    return py::make_tuple(wolves_out, curve_out);
}

PYBIND11_MODULE(GWO_cpp, m)
{
    m.doc() = "Grey Wolf Optimization core accelerated with C++";
    m.def("run", &run,
          py::arg("max_iter"),
          py::arg("dim"),
          py::arg("obj_function"),
          py::arg("num_wolves"),
          py::arg("lb"),
          py::arg("ub"),
          py::arg("wolves_in")
    );
}
