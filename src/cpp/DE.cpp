#include <pybind11/pybind11.h>
#include <pybind11/numpy.h>
#include <Eigen/Dense>
#include <random>
#include <limits>
#include <vector>
#include <chrono>
#include <iostream>
#include <map>
#include <functional>

//using namespace std; // error (maybe)
namespace py = pybind11;
using Matrix = Eigen::Matrix<double, Eigen::Dynamic, Eigen::Dynamic, Eigen::RowMajor>;
using eval_function = std::function<double(Matrix)>;

std::pair<Matrix, std::vector<double>> DE(int max_iter, int dim, eval_function obj_func, int num_par, double lb, double ub, Matrix population, double F, double Cr)
{   
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
        double fval = obj_func(population);
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
        if (dim !=10){
            std::cout << "iter: " << iter << std::endl;
        }
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
            trial = trial.cwiseMax(lb).cwiseMin(ub);

            // eval
            double tf = obj_func(trial);

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

    return std::make_pair(population, curve);
}
PYBIND11_MODULE(DE_cpp, m) 
{
    m.doc() = "Differential Evolution core accelerated with C++";
    m.def("run", &DE,
        py::arg("max_iter"),
        py::arg("dim"),
        py::arg("obj_func"),
        py::arg("num_par"),
        py::arg("lb"),
        py::arg("ub"),
        py::arg("pop_in"),
        py::arg("F") = 0.5,
        py::arg("Cr") = 0.9
    );
}
