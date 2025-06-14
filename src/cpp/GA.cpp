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

py::tuple run(int max_iter,int dim,py::function obj_function,int pop_size,double lb,double ub,py::array_t<double> pop_in,double mutation_rate=0.01)
{
    Matrix population(pop_size, dim);
    std::mt19937_64 rng(std::chrono::high_resolution_clock::now().time_since_epoch().count());
    std::uniform_real_distribution<double> uni01(0.0, 1.0);
    std::uniform_real_distribution<double> uniInit(0.0, 1.0);
    std::normal_distribution<double> normDist(0.0, 0.1);

    auto buf = pop_in.unchecked<2>();
    for (int i = 0; i < pop_size; i++)
    {
        for (int j = 0; j < dim; j++)
            population(i, j) = buf(i, j);
    }

    std::vector<double> fitness(pop_size);
    for (int i = 0; i < pop_size; i++)
    {
        py::array_t<double> arr({dim}, population.data() + i * dim);
        fitness[i] = obj_function(arr).cast<double>();
    }
    int best_idx = std::min_element(fitness.begin(), fitness.end()) - fitness.begin();
    Eigen::RowVectorXd gbest = population.row(best_idx);
    double gbest_score = fitness[best_idx];

    std::vector<double> curve;
    curve.reserve(max_iter);

    for (int iter = 0; iter < max_iter; iter++)
    {
        Matrix new_pop(pop_size, dim);
        std::vector<double> new_fit;
        new_fit.reserve(pop_size);

        new_pop.row(0) = gbest;
        new_fit.push_back(gbest_score);

        int idx = 1;
        while (idx < pop_size)
        {
            int s1 = rng() % pop_size;
            int s2 = rng() % pop_size;
            int s3 = rng() % pop_size;
            int sel = s1;
            if (fitness[s2] < fitness[sel]) sel = s2;
            if (fitness[s3] < fitness[sel]) sel = s3;
            Eigen::RowVectorXd mother = population.row(sel);

            s1 = rng() % pop_size;
            s2 = rng() % pop_size;
            s3 = rng() % pop_size;
            sel = s1;
            if (fitness[s2] < fitness[sel]) sel = s2;
            if (fitness[s3] < fitness[sel]) sel = s3;
            Eigen::RowVectorXd father = population.row(sel);

            Eigen::RowVectorXd child(dim);
            for (int j = 0; j < dim; j++)
            {
                child(j) = (uni01(rng) < 0.5 ? mother(j) : father(j));
                if (uni01(rng) < mutation_rate)
                    child(j) += normDist(rng);

                if (child(j) < lb) 
                    child(j) = lb;
                if (child(j) > ub) 
                    child(j) = ub;
            }

            double child_f = obj_function(py::array_t<double>({dim}, child.data())).cast<double>();
            new_pop.row(idx) = child;
            new_fit.push_back(child_f);
            idx++;
        }

        population = new_pop;
        fitness = new_fit;

        int cur_best = std::min_element(fitness.begin(), fitness.end()) - fitness.begin();
        if (fitness[cur_best] < gbest_score)
        {
            gbest_score = fitness[cur_best];
            gbest = population.row(cur_best);
        }
        population.row(pop_size - 1) = gbest;
        curve.push_back(gbest_score);
    }

    auto pop_out = py::array_t<double>({pop_size, dim}, {sizeof(double) * dim, sizeof(double)}, population.data());
    auto curve_out = py::array_t<double>(curve.size(), curve.data());
    return py::make_tuple(pop_out, curve_out);
}
PYBIND11_MODULE(GA_cpp, m)
{
    m.doc() = "Genetic Algorithm core accelerated with C++";
    m.def("run", &run,
          py::arg("max_iter"),
          py::arg("dim"),
          py::arg("obj_function"),
          py::arg("pop_size"),
          py::arg("lb"),
          py::arg("ub"),
          py::arg("pop_in"),
          py::arg("mutation_rate") = 0.01);
}