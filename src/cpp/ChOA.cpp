#include <pybind11/pybind11.h>
#include <pybind11/numpy.h>
#include <Eigen/Dense>
#include <random>
#include <limits>
#include <vector>
#include <chrono>
#include <cmath>

//using namespace std; // error (maybe)
namespace py = pybind11;
using Matrix = Eigen::Matrix<double, Eigen::Dynamic, Eigen::Dynamic, Eigen::RowMajor>;

static Matrix chaotic_mapping(int dim, int iteration = 10)
{
    Matrix x0(1, dim);
    x0.setConstant(0.7);
    for (int it = 0; it < iteration; it++)
    {
        for (int j = 0; j < dim; j++)
        {
            double v = x0(0, j);
            x0(0, j) = 4.0 * v * (1.0 - v);
        }
    }
    return x0;
}

py::tuple run(int max_iter,int dim,py::function obj_function,int num_pop,double lb,double ub,py::array_t<double> pop_in)
{
    Matrix chimps(num_pop, dim);
    auto buf = pop_in.unchecked<2>();
    for (int i = 0; i < num_pop; i++)
    {
        for (int j = 0; j < dim; j++)
            chimps(i, j) = buf(i, j);
    }

    std::mt19937_64 rng(std::chrono::high_resolution_clock::now().time_since_epoch().count());
    std::uniform_real_distribution<double> uni01(0.0, 1.0);

    Matrix attacker(1, dim), chaser(1, dim), barrier(1, dim), driven(1, dim);
    std::vector<double> scores(num_pop, std::numeric_limits<double>::max());

    std::vector<double> curve;
    curve.reserve(max_iter);

    for (int t = 0; t < max_iter; t++)
    {
        double f = 2.5 - (t * (2.5 / max_iter));
        for (int i = 0; i < num_pop; i++)
        {
            py::array_t<double> arr({dim}, chimps.data() + i * dim);
            scores[i] = obj_function(arr).cast<double>();
        }
        std::vector<int> idx(num_pop);
        std::iota(idx.begin(), idx.end(), 0);
        std::sort(idx.begin(), idx.end(), [&](int a, int b){ return scores[a] < scores[b]; });
        attacker = chimps.row(idx[0]);
        chaser = chimps.row(idx[1]);
        barrier = chimps.row(idx[2]);
        driven = chimps.row(idx[3]);

        for (int i = 0; i < num_pop; i++)
        {
            Matrix m = chaotic_mapping(dim);
            double r1 = uni01(rng), r2 = uni01(rng);
            Matrix D1 = (2.0 * r2 * chaser - m.cwiseProduct(chimps.row(i))).cwiseAbs();
            Matrix X1 = attacker - (2.0 * f * r1 - f) * D1;

            r1 = uni01(rng); r2 = uni01(rng);
            Matrix D2 = (2.0 * r2 * chaser - m.cwiseProduct(chimps.row(i))).cwiseAbs();
            Matrix X2 = chaser - (2.0 * f * r1 - f) * D2;

            r1 = uni01(rng); r2 = uni01(rng);
            Matrix D3 = (2.0 * r2 * barrier - m.cwiseProduct(chimps.row(i))).cwiseAbs();
            Matrix X3 = barrier - (2.0 * f * r1 - f) * D3;

            r1 = uni01(rng); r2 = uni01(rng);
            Matrix D4 = (2.0 * r2 * driven - m.cwiseProduct(chimps.row(i))).cwiseAbs();
            Matrix X4 = driven - (2.0 * f * r1 - f) * D4;

            Matrix X_new = (X1 + X2 + X3 + X4) / 4.0;
            for (int j = 0; j < dim; j++)
            {
                double v = X_new(0, j);
                if (v < lb) v = lb;
                if (v > ub) v = ub;
                chimps(i, j) = v;
            }
        }
        chimps.row(num_pop - 1) = attacker;
        curve.push_back(scores[idx[0]]);
    }

    auto pop_out   = py::array_t<double>({num_pop, dim}, {sizeof(double)*dim, sizeof(double)}, chimps.data());
    auto curve_out = py::array_t<double>(curve.size(), curve.data());
    return py::make_tuple(pop_out, curve_out);
}

PYBIND11_MODULE(ChOA_cpp, m) {
    m.doc() = "Chimp Optimization Algorithm core accelerated with C++";
    m.def("run", &run,
          py::arg("max_iter"),
          py::arg("dim"),
          py::arg("obj_function"),
          py::arg("num_pop"),
          py::arg("lb"),
          py::arg("ub"),
          py::arg("pop_in")
    );
}
