#include <pybind11/pybind11.h>
#include <pybind11/numpy.h>
#include <Eigen/Dense>
#include <random>
#include <limits>
#include <vector>
#include <chrono>

//using namespace std; // error (maybe)
namespace py = pybind11;
using Matrix = Eigen::Matrix<double, Eigen::Dynamic, Eigen::Dynamic, Eigen::RowMajor>;
py::tuple run(py::array_t<double> pop_in, py::function obj_func, double F, double Cr, int max_iter)
{
    // numpy -> Eigen
    auto buf = pop_in.unchecked<2>();
    int num_par = buf.shape(0), dim = buf.shape(1);
    Matrix population(num_par, dim);
    for(int i = 0; i < num_par; i++)
    {
        for(int j = 0; j < dim; j++)
            population(i,j) = buf(i,j);
    }
    
    // random engine
    std::mt19937_64 rng(std::chrono::high_resolution_clock::now().time_since_epoch().count());
    std::uniform_real_distribution<double> uni01(0.0, 1.0);

    // init
    std::vector<double> fitness(num_par, std::numeric_limits<double>::infinity());
    std::vector<double> gbest(dim);
    double gbest_score = std::numeric_limits<double>::infinity();

    // compute
    for(int i = 0; i < num_par; ++i) 
    {
        // call obj_func from py
        double fval = obj_func(py::array_t<double>({dim}, population.data() + i*dim)).cast<double>();
        fitness[i] = fval;
        if (fval < gbest_score) 
        {
            gbest_score = fval;
            for(int j = 0; j < dim; ++j) gbest[j] = population(i,j);
        }
    }

    // main loop
    std::vector<double> curve;
    curve.reserve(max_iter);
    for(int iter = 0; iter < max_iter; ++iter) 
    {
        for(int i = 0; i < num_par; ++i) 
        {
            std::vector<int> idxs;
            idxs.reserve(num_par-1);
            for(int t = 0; t < num_par; ++t)
            {
                if(t != i)
                    idxs.push_back(t);
            }
            std::shuffle(idxs.begin(), idxs.end(), rng);
            auto a = population.row(idxs[0]);
            auto b = population.row(idxs[1]);
            auto c = population.row(idxs[2]);

            // donor vector
            Matrix donor = a + F * (b - c);

            // crossover -> trial
            Matrix trial(1, dim);
            int jrand = std::uniform_int_distribution<int>(0, dim-1)(rng);
            for(int j = 0; j < dim; ++j) 
            {
                if(j == jrand || uni01(rng) < Cr)
                    trial(0,j) = donor(0,j);
                else
                    trial(0,j) = population(i,j);
            }

            // clip (not sure whether necessary)
            //trial = trial.cwiseMax(lb).cwiseMin(ub);

            // eval
            py::array_t<double> trial_arr({dim}, trial.data());
            double tf = obj_func(trial_arr).cast<double>();

            // choose
            if(tf < fitness[i]) 
            {
                for(int j = 0; j < dim; ++j)
                    population(i,j) = trial(0,j);
                fitness[i] = tf;
                if(tf < gbest_score) 
                {
                    gbest_score = tf;
                    for(int j = 0; j < dim; ++j)
                        gbest[j] = trial(0,j);
                }
            }
        }
        curve.push_back(gbest_score);
    }

    auto pop_out= py::array_t<double>({num_par, dim},{sizeof(double)*dim, sizeof(double)},population.data());
    auto curve_out = py::array_t<double>(curve.size(), curve.data());
    return py::make_tuple(pop_out, curve_out);
}
PYBIND11_MODULE(DE_cpp, m) 
{
    m.doc() = "Differential Evolution core accelerated with C++";
    m.def("run", &run,
          py::arg("pop_in"),
          py::arg("obj_func"),
          py::arg("F"),
          py::arg("Cr"),
          py::arg("max_iter"));
}
