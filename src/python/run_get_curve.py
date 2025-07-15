import re
import numpy as np
from src.python.Optimizer import Optimizers
from src.python.Config import Configs
import os

year = "2022"

optimizers = Optimizers.metaheuristic_list

DataSet = Configs.DataSet
function = DataSet.get_function("CEC", year, "F9", 10)


def parse_output_file(file_path):
    """
    解析輸出文件，提取每輪的最佳適應度和解決方案
    
    Returns:
        tuple: (fitness_list, solutions_list)
    """
    fitness_list = []
    solutions_list = []
    
    with open(file_path, 'r') as file:
        content = file.read()

    rounds = re.findall(r'Round (\d+) \| Best fitness: ([\d.]+).*?Round \1 \| Best solution: \[(.*?)\]', content, re.DOTALL)
    
    for round_num, fitness, solution_str in rounds:
        fitness_list.append(float(fitness))
        
        solution_str = re.sub(r'\s+', ' ', solution_str.strip())
        solution_values = []
        
        for value in solution_str.split():
            try:
                solution_values.append(float(value))
            except ValueError:
                continue
        
        solutions_list.append(solution_values)
    
    return fitness_list, solutions_list

file_path = '/home/alvin/Hyper-heurisitc-J3C2025/research_workspace/auto-metaheuristic/exp_result/all_runner/CEC_2022_F9_10D_1500iter_6Ep/output.txt'
fitness_list, solutions_list = parse_output_file(file_path)

print("Fitness values:")
for i, fitness in enumerate(fitness_list, 1):
    print(f"Round {i}: {fitness}")

print("\nSolutions:")
for i, solution in enumerate(solutions_list, 1):
    print(f"Round {i}: {solution}")
    print(f"Length: {len(solution)}")


def evaluate(param_list: list, idx=0, return_curve = False):
        """ This function is called when this class instance is called
        :param individual: list of parameters
        :param idx: index of the individual
        :return: fitness value
        """

        param_list = np.int8(np.copy(param_list).reshape((9,2)))
        optimizer_list = np.array(list(optimizers.values()), dtype=object)
        optimizer_names = np.array(list(optimizers.keys()), dtype=object)
        keep_filter = param_list[:, 1] > 0

        if np.any(keep_filter):
            param_list = param_list[keep_filter]
            if len(param_list.shape) == 1:
                param_list = param_list.reshape(1, -1)
            optimizer_list = optimizer_list[keep_filter]
            optimizer_names = optimizer_names[keep_filter]
            if len(param_list) > 1:
                indices = np.lexsort((param_list[:, 0],))
                param_list = param_list[indices]
                optimizer_list = optimizer_list[indices]
                optimizer_names = optimizer_names[indices]
        else:
            return np.inf

        total_split = np.sum(param_list[:, 1])
        if total_split == 0:
            return np.inf

        split_list = np.int32(param_list[:, 1] / total_split * 500)
        split_list[-1] = 500 - np.sum(split_list[:-1])
        population_storage = None
        best_population = None
        curve = np.array([])
        global_elite = None
        global_elite_value = np.inf

        for i, iteration in enumerate(split_list):
            if global_elite is not None:
                if population_storage is None:
                    population_storage = np.tile(global_elite,(20, 1))
                else:
                    population_storage = population_storage.copy()
                    population_storage[0] = global_elite

            population_storage, tmpcurve, best_population, best_fitness = optimizer_list[i](iteration,20,function).start(population_storage)
            curve = np.concatenate((curve, tmpcurve))

            vals = [function.func(ind) for ind in population_storage]
            best_idx = int(np.argmin(vals))
            best_val = vals[best_idx]
            if best_val < global_elite_value:
                global_elite_value = best_val
                global_elite = population_storage[best_idx].copy()
        
        return curve
    
    
for i, param in enumerate(solutions_list):
    curve = np.zeros(500)
    for i in range(5):
        curve += evaluate(param, i)
    curve /= 5
    np.save(f"{os.getcwd()}/research_workspace/auto-metaheuristic/exp_result/hh_result/data/{year}_curve_" + str(i+1) + ".npy", curve)