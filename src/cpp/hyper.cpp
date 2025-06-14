#include <pybind11/pybind11.h>
#include <pybind11/numpy.h>
#include <Eigen/Dense>
#include <random>
#include <limits>
#include <vector>
#include <chrono>
#include <numeric>
#include <functional>
#include <vector>
#include <iostream>
#include <map>


//functions
#include "DE.cpp"


namespace py = pybind11;
using Matrix = Eigen::Matrix<double, Eigen::Dynamic, Eigen::Dynamic, Eigen::RowMajor>;
using eval_function = std::function<double(Matrix)>;

using OptimizerFunc = std::function<
                            std::pair<Eigen::MatrixXd, std::vector<double>>(
                                int, int, eval_function, int, double, double, Matrix, double, double
                            )
                        >;
std::vector<OptimizerFunc> optimizers = {DE,DE};



class Hyper{
    public:
    Hyper(int hyper_iter, int dim, eval_function obj_func, int num_par, double lb, double ub, int meta_iter){
        this->hyper_iter = hyper_iter;
        this->dim = dim;
        this->obj_func = obj_func;
        this->num_par = num_par;
        this->lb = lb;
        this->ub = ub;
        this->meta_iter = meta_iter;
    }
    py::tuple run()
    {
        std::mt19937_64 rng(std::chrono::high_resolution_clock::now().time_since_epoch().count());
        std::uniform_real_distribution<double> rand_dis(this->lb, this->ub);

        Matrix population(this->num_par, this->dim);
        for (int i = 0; i < this->num_par; ++i) {
            for (int j = 0; j < this->dim; ++j) {
                population(i, j) = rand_dis(rng);
            }
        }
        
        std::vector<double> fitness(num_par, std::numeric_limits<double>::infinity());
        std::vector<double> gbest(dim);
        double gbest_score = std::numeric_limits<double>::infinity();
    
        // compute
        for(int i = 0; i < num_par; ++i) 
        {
            // call obj_func from py
            double fval = this->HyperEvaluation(population);
            fitness[i] = fval;
            if (fval < gbest_score) 
            {
                gbest_score = fval;
                for(int j = 0; j < dim; ++j) gbest[j] = population(i,j);
            }
        }
    
        // main loop
        std::vector<double> curve;
        curve.reserve(hyper_iter);
        for(int iter = 0; iter < hyper_iter; ++iter) 
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
                    if(j == jrand || rand_dis(rng) < Cr)
                        trial(0,j) = donor(0,j);
                    else
                        trial(0,j) = population(i,j);
                }
    
                // clip (not sure whether necessary)
                trial = trial.cwiseMax(lb).cwiseMin(ub);
    
                // eval
                double tf = this->HyperEvaluation(trial);
    
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


    double HyperEvaluation(Matrix param_list, bool return_curve = false) {

        // Filter rows where the second column is greater than 0
        Eigen::Array<bool, Eigen::Dynamic, 1> keep_filter = param_list.col(1).array() > 0;
        if (keep_filter.any()) {
            Eigen::MatrixXi filtered_param_list = param_list(keep_filter, Eigen::all);
            param_list = filtered_param_list;

            // Sort by the first column
            Eigen::VectorXi indices = Eigen::VectorXi::LinSpaced(param_list.rows(), 0, param_list.rows() - 1);
            std::sort(indices.data(), indices.data() + indices.size(), [&](int a, int b) {
                return param_list(a, 0) < param_list(b, 0);
            });
            param_list = param_list(indices, Eigen::all);
        } else {
            return std::numeric_limits<double>::infinity();
        }

        // Calculate total_split
        int total_split = param_list.col(1).sum();
        if (total_split == 0) {
            return std::numeric_limits<double>::infinity();
        }

        // Calculate split_list
        Eigen::VectorXi split_list = (param_list.col(1).array().cast<double>() / total_split * this->meta_iter).cast<int>();
        split_list(split_list.size() - 1) = meta_iter - split_list.head(split_list.size() - 1).sum();

        Eigen::MatrixXd population_storage;
        Eigen::VectorXd global_elite;
        double global_elite_value = std::numeric_limits<double>::infinity();
        Eigen::VectorXd curve;

        for (int i = 0; i < split_list.size(); ++i) {
            int iteration = split_list(i);

            if (global_elite.size() > 0) {
                if (population_storage.size() == 0) {
                    population_storage = global_elite.replicate(this->num_par, 1);
                } else {
                    population_storage.row(0) = global_elite;
                }
            }

            // Run optimizer
            Eigen::MatrixXd tmpcurve;
            std::pair<Matrix, std::vector<double>> result = optimizers[i](iteration, this->dim, this->obj_func, this->num_par, this->lb, this->ub, population_storage, this->F, this->Cr);

            population_storage = result.first;
            tmpcurve = Eigen::Map<Eigen::MatrixXd>(result.second.data(), result.second.size(), 1);
            tmpcurve = tmpcurve.transpose();
            

            // Evaluate population
            Eigen::VectorXd vals(population_storage.rows());
            for (int j = 0; j < population_storage.rows(); ++j) {
                vals(j) = obj_func(population_storage.row(j));
            }

            // Find the best individual
            int best_idx;
            double best_val = vals.minCoeff(&best_idx);
            if (best_val < global_elite_value) {
                global_elite_value = best_val;
                global_elite = population_storage.row(best_idx);
            }

            // Append to curve
            curve.conservativeResize(curve.size() + tmpcurve.size());
            curve.tail(tmpcurve.size()) = tmpcurve;
        }

        if (return_curve) {
            // If return_curve is true, return the sum of the curve as a placeholder
            return curve.sum();
        }
        return global_elite_value;
    }

    private:
    int hyper_iter;
    int dim;
    eval_function obj_func;
    int num_par;
    double lb;
    double ub;
    double Cr = 0.9;
    double F = 0.5;

    int meta_iter;

};



PYBIND11_MODULE(Hyper_cpp, m) 
{
    m.doc() = "Differential Evolution core accelerated with C++";
    py::class_<Hyper>(m, "HyperHeuristic")
        .def(py::init<int, int, py::function, int, double, double, int>(),
             py::arg("hyper_iter"),
             py::arg("dim"),
             py::arg("obj_func"), // This will be a Python function
             py::arg("num_par"),
             py::arg("lb"),
             py::arg("ub"),
             py::arg("meta_iter")
        )
        .def("run", &Hyper::run, "Runs the hyper-heuristic optimization process");
        // If you want to expose HyperEvaluation or other methods, add them here
        // .def("evaluate_hyper_params", &Hyper::HyperEvaluation, "Evaluates a set of hyper-parameters");
}


double cec2022_f12_10D(const Eigen::VectorXd& x) {
    // 定義函數的固定維度
    static const int D = 10;

    // 檢查輸入向量的維度
    if (x.size() != D) {
        std::cerr << "Error: Input vector dimension must be " << D << " for cec2022_f12_10D, but got " << x.size() << std::endl;
        return std::nan(""); // 返回 NaN 表示錯誤
    }

    // CEC 2022 F12 對於 D=10 的固定 Bias 值
    static const double bias = 1200.0;

    // CEC 2022 F12 對於 D=10 的固定偏移向量 o
    // TODO: 您需要將這裡的零向量替換為從 CEC 2022 標準數據檔案中讀取的 D=10 F12 的實際 o 向量數值
    static const Eigen::VectorXd o = Eigen::VectorXd::Zero(D); // <<-- 替換為真實數據!
    /*
    // 範例: 如果 o 的數據是 {o0, o1, ..., o9}
    static const Eigen::VectorXd o = (Eigen::VectorXd(D) << o0, o1, o2, o3, o4, o5, o6, o7, o8, o9).finished();
    */


    // CEC 2022 F12 對於 D=10 的固定旋轉矩陣 M (D x D)
    // TODO: 您需要將這裡的單位矩陣替換為從 CEC 2022 標準數據檔案中讀取的 D=10 F12 的實際 M 矩陣數值
    static const Eigen::MatrixXd M = Eigen::MatrixXd::Identity(D, D); // <<-- 替換為真實數據!
    /*
    // 範例: 如果 M 的數據是一個 D*D 的數組 values[]
    static const Eigen::MatrixXd M = Eigen::Map<const Eigen::MatrixXd>(values, D, D);
    */


    // 步驟 1: 應用偏移 (Shift)
    // z = x - o
    Eigen::VectorXd z = x - o;

    // 步驟 2: 應用旋轉 (Rotate)
    // y = M * z
    Eigen::VectorXd y = M * z;

    // 步驟 3: 計算標準 Ackley 函數在 y 上的值
    // Ackley(y) = -20 * exp(-0.2 * sqrt( (1/D) * sum(y_i^2) )) - exp( (1/D) * sum(cos(2*pi*y_i)) ) + 20 + exp(1)

    // 計算 sum(y_i^2)
    double sum_sq = y.array().square().sum();

    // 計算 sqrt( (1/D) * sum(y_i^2) )
    double term1_sqrt = std::sqrt((1.0 / D) * sum_sq);

    // 計算 sum(cos(2*pi*y_i))
    double sum_cos = (y.array() * (2.0 * M_PI)).cos().sum();

    // 計算 (1/D) * sum(cos(2*pi*y_i))
    double term2_avg_cos = (1.0 / D) * sum_cos;

    // 計算 Ackley 函數的標準部分
    double ackley_val = -20.0 * std::exp(-0.2 * term1_sqrt)
                        - std::exp(term2_avg_cos)
                        + 20.0
                        + std::exp(1.0); // exp(1) 即是常數 e

    // 步驟 4: 加上 Bias
    // F12(x) = Ackley(y) + bias
    double result = ackley_val + bias;

    return result;
}

