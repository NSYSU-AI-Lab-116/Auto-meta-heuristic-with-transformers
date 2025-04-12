"""This script is the main script of handling the hyperheuristic algorithm."""
import numpy as np
from Config import Configs
from Optimizer import Optimizers
from Optimizer import HyperParameters

Color = Configs.Color # Color -> class
DataSet = Configs.DataSet # DataSet -> class
HyperHeuristic = HyperParameters.heuristic  # Hyperheuristic optimizer -> class

optimizers = Optimizers.metaheuristic_list # Metaheuristic optimizers -> dict
HyperParameters = HyperParameters.Parameters # Hyperheuristic parameters -> dict


class HyperHeuristicTemplate(HyperHeuristic): # inherit from a meta heuristic algorithm
    """ This calss is the ain script of handling the hyperheuristic algorithm"""
    def __init__(self, obj_function):
        self.hyper_func = HyperEvaluationFunction(obj_function)
        self.obj_func = obj_function
        super().__init__(HyperParameters["max_iter"],
                         HyperParameters["num_individual"], self.hyper_func)

class HyperEvaluationFunction:
    """ This class is the evaluation function for the hyperheuristic algorithm"""
    def __init__(self, obj_function):
        self.obj_func = obj_function
        self.dim = len(optimizers) * HyperParameters["num_param_each"]
        self.lb = HyperParameters["lb"]
        self.ub = HyperParameters["ub"]
        self.func = self.call
        self.f_type = "hyperheuristic"

    def call(self, individual: list, idx: int) -> float:
        """ This function is called when this class instance is called
        :param individual: list of parameters
        :param idx: index of the individual
        :return: fitness value
        """
        param_list = np.copy(individual).reshape((len(optimizers),
                                               HyperParameters["num_param_each"]))
        return self.evaluate(param_list,idx)

    def evaluate(self,param_list,idx, tid = [0]):
        tid[0] += 1
        """ implement the multiprocess for works"""
        optimizer_list = np.array(list(optimizers.values()),dtype=object)
        keep_filter = param_list[:,1] > 0
        if np.any(keep_filter):
            param_list = param_list[keep_filter]
            if len(param_list.shape) == 1:
                param_list = param_list.reshape(1, -1)
            optimizer_list = optimizer_list[keep_filter]
            if len(param_list) > 1:
                indices = np.lexsort((param_list[:, 0],))
                param_list = param_list[indices]
                optimizer_list = optimizer_list[indices]
        else:
            return np.inf

        total_split = np.sum(param_list[:, 1])
        if total_split == 0:
            return np.inf

        population_storage = None
        curve = np.array([])
        iteration = int(HyperParameters["max_iter"] * param_list[0,1] / total_split )
        population_storage, tmpcurve = optimizer_list[0](iteration,\
            HyperParameters["num_individual"], self.obj_func).start()

        curve = np.concatenate((curve, tmpcurve))

        for i in range(1,len(param_list)):
            iteration = int(HyperParameters["max_iter"] * param_list[i,1] / total_split)
            population_storage, tmpcurve = optimizer_list[i](iteration,\
                HyperParameters["num_individual"],self.obj_func).start(population_storage)
            curve = np.concatenate((curve, tmpcurve))

        #print(Color.YELLOW + "id: " + str(tid[0]) + "total:" +str(total_split) + "iter" + str(iteration) + Color.RESET)
        return curve[-1]
