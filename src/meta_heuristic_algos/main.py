# -*- coding: utf-8 -*-
""" the entry point of the program"""
from matplotlib import pyplot as plt
from src.meta_heuristic_algos.Config import Configs
from src.meta_heuristic_algos.optimizer import HyperParameters
from src.meta_heuristic_algos.hyperheuristic import HyperHeuristicTemplate

Color = Configs.Color
DataSet = Configs.DataSet

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
        obj_func = DataSet.get_function(self.f_type, self.year, self.name, int(self.dim))
        curves = []
        for epoch in range(self.epochs):
            population, curve = HyperHeuristicTemplate(obj_function=obj_func,
                                                       hyper_iteration = self.iter).start()
            print(f"{Color.YELLOW}Best solution: {population}{Color.RESET}")
            curves.append(curve)

        for curve in curves:
            plt.plot(curve)
        plt.title(f"Best solution: {population}")
        plt.xlabel("Iterations")
        plt.ylabel("Fitness")
        plt.show()



if __name__ == '__main__':
    MAINCONTROL()

    print(f"{Color.RED}Quitting...{Color.RESET}")
