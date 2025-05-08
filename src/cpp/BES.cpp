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

py::tuple run(int max_iter, int dim, py::function obj_function, int num_par, double lb, double ub, py::array_t<double> pop_in, double w = 0.7, double c1 = 1.5, double c2 = 1.5)
{
    Matrix particles(num_par, dim);
    auto buf = pop_in.unchecked<2>();
    for (int i = 0; i < num_par; i++)
    {
        for (int j = 0; j < dim; j++)
            particles(i, j) = buf(i, j);
    }
    std::mt19937_64 rng(std::chrono::high_resolution_clock::now().time_since_epoch().count());
    std::uniform_real_distribution<double> uni_pos(lb, ub);

    Matrix best_position(num_par, dim);
    std::vector<double> best_energy(num_par, std::numeric_limits<double>::infinity());
    Matrix gbest_position(1, dim);
    for (int j = 0; j < dim; j++)
        gbest_position(0, j) = uni_pos(rng);
    double gbest_energy = std::numeric_limits<double>::infinity();

    std::vector<double> energy(num_par);
    std::vector<double> curve;
    curve.reserve(max_iter);

    for (int t = 0; t < max_iter; t++)
    {
        for (int i = 0; i < num_par; i++)
        {
            py::array_t<double> arr({dim}, particles.data() + i * dim);
            double fitness = obj_function(arr).cast<double>();
            energy[i] = fitness;
            if (fitness < best_energy[i])
            {
                best_energy[i] = fitness;
                best_position.row(i) = particles.row(i);
            }
            if (fitness < gbest_energy)
            {
                gbest_energy = fitness;
                gbest_position = particles.row(i);
            }
        }
        for (int i = 0; i < num_par; i++)
        {
            Eigen::RowVectorXd r1(dim), r2(dim);
            for (int j = 0; j < dim; j++)
            {
                r1(j) = std::uniform_real_distribution<double>(0.0, 1.0)(rng);
                r2(j) = std::uniform_real_distribution<double>(0.0, 1.0)(rng);
            }
            Eigen::RowVectorXd velocity = w * particles.row(i) + c1 * r1.cwiseProduct(best_position.row(i) - particles.row(i)) + c2 * r2.cwiseProduct(gbest_position - particles.row(i));
            particles.row(i) += velocity;
            for (int j = 0; j < dim; j++)
            {
                double v = particles(i, j);
                if (v < lb) v = lb;
                if (v > ub) v = ub;
                particles(i, j) = v;
            }
        }
        particles.row(num_par - 1) = gbest_position;
        curve.push_back(gbest_energy);
    }

    auto pop_out = py::array_t<double>({num_par, dim}, {sizeof(double) * dim, sizeof(double)}, particles.data());
    auto curve_out = py::array_t<double>(curve.size(), curve.data());
    return py::make_tuple(pop_out, curve_out);
}

PYBIND11_MODULE(BES_cpp, m)
{
    m.doc() = "bald eagle search core accelerated with C++";
    m.def("run", &run,
        py::arg("max_iter"),
        py::arg("dim"),
        py::arg("obj_function"),
        py::arg("num_par"),
        py::arg("lb"),
        py::arg("ub"),
        py::arg("pop_in"),
        py::arg("w") = 0.7,
        py::arg("c1") = 1.5,
        py::arg("c2") = 1.5
    );
}
