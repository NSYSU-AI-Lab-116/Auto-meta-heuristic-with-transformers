import numpy as np
from src.meta_heuristic_algos.Config import Configs
from src.meta_heuristic_algos.Optimizer import Optimizers
from src.meta_heuristic_algos.Optimizer import HyperParameters as HyperParameterClass

Color = Configs.Color # Color -> class
DataSet = Configs.DataSet # DataSet -> class
HyperHeuristic = HyperParameterClass.heuristic  # Hyperheuristic optimizer -> class

optimizers = Optimizers.metaheuristic_list # Metaheuristic optimizers -> dict
HyperParameters = HyperParameterClass.Parameters # Hyperheuristic parameters -> dict


class HyperHeuristicTemplate(HyperHeuristic): # inherit from a meta heuristic algorithm
    """ This calss is the ain script of handling the hyperheuristic algorithm
            
            :param obj_function: the objective function to be optimized 
            :param hyper_iteration: number of iterations for the hyperheuristic algorithm
            :param color: the color for output display
    """
    def __init__(self, obj_function,hyper_iteration, color):
        self.hyper_func = HyperEvaluationFunction(obj_function,color)
        self.obj_func = obj_function
        self.color = color
        super().__init__(hyper_iteration,
                        HyperParameters["num_individual"], self.hyper_func)

class HyperEvaluationFunction:
    """ This class is the evaluation function for the hyperheuristic algorithm
        :param obj_function: the objective function to be optimized 
        :param color: the color for output display
    """
    def __init__(self, obj_function, color, f_type="hyperheuristic"):
        self.obj_func = obj_function
        self.dim = len(optimizers) * HyperParameters["num_param_each"]
        self.lb = HyperParameters["lb"]
        self.ub = HyperParameters["ub"]
        self.func = self.evaluate
        self.f_type = f_type
        self.color = color

    def evaluate(self, param_list: list, idx=0, return_curve = False) -> float:
        """ This function is called when this class instance is called
        :param individual: list of parameters
        :param idx: index of the individual
        :return: fitness value
        """

        param_list = np.int8(np.copy(param_list).reshape((len(optimizers),
                                            HyperParameters["num_param_each"]))
        )
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

        split_list = np.int32(param_list[:, 1] / total_split * HyperParameters["meta_iter"])
        split_list[-1] = HyperParameters["meta_iter"] - np.sum(split_list[:-1]) - 1
        population_storage = None
        curve = np.array([])
        global_elite = None
        global_elite_value = np.inf

        for i, iteration in enumerate(split_list):
            if global_elite is not None:
                if population_storage is None:
                    population_storage = np.tile(global_elite,(HyperParameters["num_individual"], 1))
                else:
                    population_storage = population_storage.copy()
                    population_storage[0] = global_elite

            population_storage, tmpcurve = optimizer_list[i](iteration,HyperParameters["num_individual"],self.obj_func).start(population_storage)
            curve = np.concatenate((curve, tmpcurve))

            vals = [self.obj_func(ind) for ind in population_storage]
            best_idx = int(np.argmin(vals))
            best_val = vals[best_idx]
            if best_val < global_elite_value:
                global_elite_value = best_val
                global_elite = population_storage[best_idx].copy()

        #print(f'{self.color}id: {idx} | total: {total_split} | iter: {iteration}{Color.RESET}')
        if return_curve:
            return curve
        return curve[-1]
