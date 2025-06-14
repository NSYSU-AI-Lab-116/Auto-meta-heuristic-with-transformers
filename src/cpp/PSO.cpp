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

py::tuple run(int max_iter, int dim, py::function obj_function, int num_par, double lb, double ub, py::array_t<double> pop_in)
{
    auto buf = pop_in.unchecked<2>();
    Matrix particles(num_par, dim);
    for (int i = 0; i < num_par; i++)
    {
        for (int j = 0; j < dim; j++)
            particles(i, j) = buf(i, j);
    }

    Matrix velocities(num_par, dim);
    {
        std::mt19937_64 rng(std::chrono::high_resolution_clock::now().time_since_epoch().count());
        double range = std::abs(ub - lb);
        std::uniform_real_distribution<double> uni_v(-range, range);
        for (int i = 0; i < num_par; i++)
        {
            for (int j = 0; j < dim; j++)
                velocities(i, j) = uni_v(rng);
        }
    }

    std::vector<double> pbest_scores(num_par, std::numeric_limits<double>::infinity());
    Matrix pbest = particles;
    Matrix gbest(1, dim);
    double gbest_score = std::numeric_limits<double>::infinity();

    std::mt19937_64 rng(std::chrono::high_resolution_clock::now().time_since_epoch().count());
    std::uniform_real_distribution<double> uni01(0.0, 1.0);

    std::vector<double> curve;
    curve.reserve(max_iter);

    for (int t = 0; t < max_iter; t++)
    {
        double w = 0.9 - (double(t) / max_iter) * 0.5;
        for (int i = 0; i < num_par; i++)
        {
            py::array_t<double> arr({dim}, particles.data() + i * dim);
            double fitness = obj_function(arr).cast<double>();
            if (fitness < pbest_scores[i])
            {
                pbest_scores[i] = fitness;
                pbest.row(i) = particles.row(i);
            }
            if (fitness < gbest_score)
            {
                gbest_score = fitness;
                gbest = particles.row(i);
            }
        }

        for (int i = 0; i < num_par; i++)
        {
            Matrix r1(1, dim), r2(1, dim);
            for (int j = 0; j < dim; j++)
            {
                r1(0, j) = uni01(rng);
                r2(0, j) = uni01(rng);
            }
            Matrix cognitive = 2.0 * r1.cwiseProduct(pbest.row(i) - particles.row(i));
            Matrix social    = 2.0 * r2.cwiseProduct(gbest - particles.row(i));
            velocities.row(i) = w * velocities.row(i) + cognitive + social;

            particles.row(i) += velocities.row(i);
            for (int j = 0; j < dim; j++)
            {
                double v = particles(i, j);
                if (v < lb) 
                    v = lb;
                if (v > ub) 
                    v = ub;
                particles(i, j) = v;
            }
        }

        particles.row(num_par - 1) = gbest;
        curve.push_back(gbest_score);
    }

    auto pop_out   = py::array_t<double>({num_par, dim}, {sizeof(double) * dim, sizeof(double)}, particles.data());
    auto curve_out = py::array_t<double>(curve.size(), curve.data());
    return py::make_tuple(pop_out, curve_out);
}

PYBIND11_MODULE(PSO_cpp, m)
{
    m.doc() = "Particle Swarm Optimization core accelerated with C++";
    m.def("run", &run,
          py::arg("max_iter"),
          py::arg("dim"),
          py::arg("obj_function"),
          py::arg("num_par"),
          py::arg("lb"),
          py::arg("ub"),
          py::arg("pop_in")
    );
}
