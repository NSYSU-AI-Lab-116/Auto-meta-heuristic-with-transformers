#include <pybind11/pybind11.h>
#include <pybind11/numpy.h>
#include <Eigen/Dense>
#include <random>
#include <limits>
#include <vector>
#include <chrono>
#include <cmath>

namespace py = pybind11;
using Matrix = Eigen::Matrix<double, Eigen::Dynamic, Eigen::Dynamic, Eigen::RowMajor>;

static Eigen::RowVectorXd levy_flight(int dim)
{
    double beta = 1.5;
    double sigma = std::pow(
        tgamma(1 + beta) * std::sin(M_PI * beta / 2) /
        (tgamma((1 + beta) / 2) * beta * std::pow(2, (beta - 1) / 2)),
        1 / beta
    );
    static thread_local std::mt19937_64 rng(std::chrono::high_resolution_clock::now().time_since_epoch().count());
    std::normal_distribution<double> norm01(0.0, 1.0);
    Eigen::RowVectorXd u(dim), v(dim), step(dim);
    for (int j = 0; j < dim; j++)
    {
        u(j) = 0.01 * norm01(rng) * sigma;
        v(j) = norm01(rng);
        step(j) = u(j) / std::pow(std::abs(v(j)), 1 / beta);
    }
    return step;
}

py::tuple run(int max_iter,int dim,py::function obj_func,int num_hawks,double lb,double ub,py::array_t<double> hawks_in)
{
    auto buf = hawks_in.unchecked<2>();
    Matrix hawks(num_hawks, dim);
    for (int i = 0; i < num_hawks; i++)
    {
        for (int j = 0; j < dim; j++)
            hawks(i, j) = buf(i, j);
    }

    std::mt19937_64 rng(std::chrono::high_resolution_clock::now().time_since_epoch().count());
    std::uniform_real_distribution<double> uni01(0.0, 1.0);

    Eigen::RowVectorXd best_position(dim);
    double best_score = std::numeric_limits<double>::infinity();
    std::vector<double> curve;
    curve.reserve(max_iter);

    for (int t = 0; t < max_iter; t++)
    {
        for (int i = 0; i < num_hawks; i++)
        {
            py::array_t<double> arr({dim}, hawks.data() + i * dim);
            double f = obj_func(arr).cast<double>();
            if (f < best_score)
            {
                best_score = f;
                best_position = hawks.row(i);
            }
        }

        double E0 = 2 * uni01(rng) - 1;
        for (int i = 0; i < num_hawks; i++)
        {
            double E = 2 * E0 * (1 - double(t) / max_iter);
            double r = uni01(rng);
            double J = 2 * (1 - uni01(rng));
            Eigen::RowVectorXd LF = levy_flight(dim);

            if (std::abs(E) >= 1)
            {
                if (r >= 0.5)
                {
                    int idx = rng() % num_hawks;
                    Eigen::RowVectorXd X_rand = hawks.row(idx);
                    hawks.row(i) = X_rand - r * (X_rand - 2 * r * hawks.row(i)).cwiseAbs();
                }
                else
                {
                    Eigen::RowVectorXd mean_hawks = hawks.colwise().mean();
                    hawks.row(i) = (best_position - mean_hawks).array() - r * (lb + r * (ub - lb));
                }
            }
            else
            {
                Eigen::RowVectorXd deltaX = best_position - hawks.row(i);
                if (r >= 0.5 && std::abs(E) >= 0.5)
                    hawks.row(i) = deltaX - E * (J * best_position - hawks.row(i)).cwiseAbs();
                else if (r >= 0.5)
                    hawks.row(i) = best_position - E * deltaX.cwiseAbs();
                else if (std::abs(E) >= 0.5)
                {
                    Eigen::RowVectorXd Y = best_position - E * (J * best_position - hawks.row(i)).cwiseAbs();
                    Eigen::RowVectorXd Z = Y + uni01(rng) * LF;
                    py::array_t<double> aY({dim}, Y.data()), aZ({dim}, Z.data());
                    hawks.row(i) = obj_func(aZ).cast<double>() < obj_func(aY).cast<double>() ? Z : Y;
                }
                else
                {
                    Eigen::RowVectorXd mean_hawks = hawks.colwise().mean();
                    Eigen::RowVectorXd Y = best_position - E * (J * best_position - mean_hawks).cwiseAbs();
                    Eigen::RowVectorXd Z = Y + uni01(rng) * LF;
                    py::array_t<double> aY({dim}, Y.data()), aZ({dim}, Z.data());
                    hawks.row(i) = obj_func(aZ).cast<double>() < obj_func(aY).cast<double>() ? Z : Y;
                }
            }

            for (int j = 0; j < dim; j++)
            {
                if (hawks(i, j) < lb) hawks(i, j) = lb;
                if (hawks(i, j) > ub) hawks(i, j) = ub;
            }
        }

        hawks.row(num_hawks - 1) = best_position;
        curve.push_back(best_score);
    }

    auto out_hawks = py::array_t<double>({num_hawks, dim}, {sizeof(double) * dim, sizeof(double)}, hawks.data());
    auto out_curve = py::array_t<double>(curve.size(), curve.data());
    return py::make_tuple(out_hawks, out_curve);
}

PYBIND11_MODULE(HHO_cpp, m)
{
    m.doc() = "Harris Hawks Optimization core accelerated with C++";
    m.def("run", &run,
          py::arg("max_iter"),
          py::arg("dim"),
          py::arg("obj_function"),
          py::arg("num_hawks"),
          py::arg("lb"),
          py::arg("ub"),
          py::arg("hawks_in"));
}
