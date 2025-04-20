# -*- coding: utf-8 -*-
""" the entry point of the program"""
from matplotlib import pyplot as plt
from src.meta_heuristic_algos.Config import Configs
from src.meta_heuristic_algos.Optimizer import HyperParameters
from src.meta_heuristic_algos.hyperheuristic import HyperHeuristicTemplate

import os
import multiprocessing as mp
from concurrent.futures import ProcessPoolExecutor, as_completed
import numpy as np

Color = Configs.Color
DataSet = Configs.DataSet

def _run_epoch(args):
    epoch_idx, f_type, year, name, dim, iterations = args

    np.random.seed(os.getpid())

    obj_func = DataSet.get_function(f_type, year, name, int(dim))
    population, curve = HyperHeuristicTemplate(
        obj_function=obj_func,
        hyper_iteration=iterations,
    ).start()

    return epoch_idx, population, curve

class MAINCONTROL:
    """ This class is the main control of the program"""
    def __init__(self):
        self.f_type, self.year, self.name, self.dim, self.iter, self.epochs = self.get_args()
        self.create_hyperheuristic_instance()

    def get_args(self):
        """ get the args from the user"""

        funcs_by_year = DataSet().all_funcs
        qc = ['q','Q','quit','Quit']
        f_type = None
        year = None
        name = None
        dim = None
        while f_type not in qc and  year not in qc and  name not in qc and  dim not in qc:

            f_type = "CEC"
            year = None
            name = None
            dim = None

            if f_type not in funcs_by_year:
                print("Invalid function type")
                continue

            if f_type == "CEC":
                year = input(f"Year param ({' / '.join(funcs_by_year[f_type])}): ") # Year
                if year not in funcs_by_year[f_type]:
                    print("Invalid param")
                    continue

                name = input(f"Name param \
                             ({' / '.join(funcs_by_year[f_type][year])}): ").upper() # Function Name
                if name not in funcs_by_year[f_type][year]:
                    print("Invalid param\n\n")
                    continue

                dim = input(f"Dim param \
                    ({' / '.join(funcs_by_year[f_type][year][name])}): ") # Dimension
                if dim not in funcs_by_year[f_type][year][name]:
                    print("Invalid param\n\n")
                    continue

            else:
                print("Invalid function type")
                continue

            print(f"{Color.MAGENTA}DataSet: \
                {f_type}-{year}-{name} - Dimension: {dim}{Color.RESET}\n")
            try:
                iterations = int(input(f"{Color.BLUE}Input Ierations(500): {Color.RESET}"))
                epochs = int(input(f"{Color.BLUE}Input Epochs(10): {Color.RESET}"))
                if iterations <= 0 or epochs <= 0:
                    raise ValueError("Iterations and epochs must be positive integers.")

            except ValueError as e:
                print(f"{Color.RED}Invalid input:{e}{Color.RESET}")
                continue
            except Exception as e:
                print(f"{Color.RED}Invalid input:{e}{Color.RESET}")
                continue

            return f_type, year, name, dim, iterations, epochs
        return None

    def create_hyperheuristic_instance(self):
        """ create the hyper heuristic"""
        HyperParameters.Parameters["epoch"] = self.epochs
        HyperParameters.Parameters["num_individual"] = 30

        # tasks for parallel processing
        tasks = [
            (e, self.f_type, self.year, self.name, self.dim, self.iter)
            for e in range(self.epochs)]

        curves = [None] * self.epochs
        best_pop, best_fit = None, np.inf

        with ProcessPoolExecutor(max_workers=Configs.executer_num) as pool:
            for future in as_completed(pool.submit(_run_epoch, t) for t in tasks):
                epoch_idx, pop, curve = future.result()
                curves[epoch_idx] = curve
                if curve[-1] < best_fit:
                    best_fit, best_pop = curve[-1], pop
                print(f"{Color.CYAN}[Epoch {epoch_idx}] fitness={curve[-1]}{Color.RESET}")
        
        print(f"{Color.YELLOW}Global best fitness: {best_fit}{Color.RESET}")

        for curve in curves:
            plt.plot(curve)
        plt.title(f"Best solution: {best_pop}")
        plt.xlabel("Iterations")
        plt.ylabel("Fitness")
        plt.show()



if __name__ == '__main__':
    mp.set_start_method("spawn", force=True) # prevent from error between running on Linux/Windows
    MAINCONTROL()
    print(f"{Color.RED}Quitting...{Color.RESET}")
