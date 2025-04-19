# -*- coding: utf-8 -*-
""" the entry point of the program"""
from concurrent.futures import ProcessPoolExecutor
import os
from datetime import datetime
from matplotlib import pyplot as plt
import numpy as np
import pandas as pd

from src.meta_heuristic_algos.Config import Configs
from src.meta_heuristic_algos.Optimizer import HyperParameters, Optimizers
from src.meta_heuristic_algos.hyperheuristic import HyperHeuristicTemplate

Color = Configs.Color
DataSet = Configs.DataSet

time_now = lambda :datetime.now().strftime("%Y-%m-%d %H:%M:%S")

class MAINCONTROL:
    """ This class is the main control of the program"""
    def __init__(self):
        self.folder_name = ""
        self.folder_path = ""
        self.f_type = ""
        self.year = ""
        self.name = ""
        self.dim = 0
        self.epochs = HyperParameters.Parameters["epoch"]
        self.iter = HyperParameters.Parameters["hyper_iter"]
        if Configs.execution_type == "single":
            self.f_type, self.year, self.name, self.dim, self.iter, self.epochs = self.get_args()
            #self.f_type, self.year, self.name, self.dim, self.iter, self.epochs = "CEC", "2022", "F12", 2, 500, 10
            HyperParameters.Parameters["epoch"] = self.epochs
            self.folder_path = os.path.join(os.getcwd(), "research_workspace", "auto-metaheuristic", "exp_result", "all_runner")
            self.folder_name = f"{self.f_type}_{self.year}_{self.name}_{self.dim}D_{self.iter}iter_{self.epochs}Ep"
            os.system(f'mkdir {os.getcwd()}/research_workspace/auto-metaheuristic/exp_result/all_runner/{self.folder_name}')
            self.create_hyperheuristic_instance()
        elif Configs.execution_type == "all":
            self.all_func()

    def logging(self,msg):
        """ log the data"""
        with open(os.path.join(self.folder_path, self.folder_name, "log.txt"), "a") as f:
            f.write(f'[{time_now()}]: {msg}\n')

    def all_func(self):
        """ get all the functions from the dataset"""
        funcs_by_year = DataSet().all_funcs
        for f_type in funcs_by_year:
            for year in list(funcs_by_year[f_type].keys())[-1:-6:-1]:
                for name in funcs_by_year[f_type][year]:
                    self.f_type = f_type
                    self.year = year
                    self.name = name
                    try:
                        self.dim = funcs_by_year[f_type][year][name][1]
                    except:
                        self.dim = funcs_by_year[f_type][year][name][0]
                    
                    self.folder_path = os.path.join(os.getcwd(), "research_workspace", "auto-metaheuristic", "exp_result", "all_runner")
                    self.folder_name = f"{self.f_type}_{self.year}_{self.name}_{self.dim}D_{self.iter}iter_{self.epochs}Ep"
                    print(f"{Color.MAGENTA}DataSet: {self.f_type}-{self.year}-{self.name} - Dimension: {self.dim}{Color.RESET}\n")
                    print(f"{Color.MAGENTA}Iter: {self.iter} -  Epoch: {self.epochs}{Color.RESET}\n")
                    os.system(f'mkdir {os.getcwd()}/research_workspace/auto-metaheuristic/exp_result/all_runner/{self.folder_name}')
                    self.logging(f"Running DataSet: {self.f_type}-{self.year}-{self.name} - Dimension: {self.dim}")
                    try:
                        self.create_hyperheuristic_instance()
                        self.logging(f"Finished!: DataSet: {self.f_type}-{self.year}-{self.name} - Dimension: {self.dim}")
                    except Exception as e:
                        print(f"{time_now()}: {Color.RED}Error: {e}{Color.RESET}")
                        self.logging(f"Runtime Error: {e}")
 
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
        try:
            obj_func = DataSet.get_function(self.f_type, self.year, self.name, int(self.dim))
        except Exception as e:
            print(f"{time_now()}: {Color.RED}Function load Error: {e}{Color.RESET}")
            self.logging(f"Function load error: {e}")

        all_curves = []
        all_history_population = []

        try:
            with ProcessPoolExecutor() as executor:
                futures = [executor.submit(HyperHeuristicTemplate(obj_function=obj_func,\
                            hyper_iteration=self.iter,color=list(Color.color_set.values())[i%7]).start)\
                            for i in range(self.epochs)]

                for i , future in enumerate(futures):
                    population, curve = future.result()
                    all_curves.append(curve)
                    all_history_population.append(population)
                    
                
        except Exception as e:
            print(f"{time_now()}: {Color.RED}Runtime rror: {e}{Color.RESET}")
            self.logging(f"Runtime error: {e}")

        try:
            for i, (curve, population) in enumerate(zip(all_curves, all_history_population)):
                print(f"{list(Color.color_set.values())[i%7]} Epoch {i+1} | Best fitness: {curve[-1]}{Color.RESET}")
                print(f"{list(Color.color_set.values())[i%7]} Epoch {i+1} | Best solution: {population[-1]}{Color.RESET}")
        except Exception as e:
            print(f"{time_now()}: {Color.RED}Result extract error: {e}{Color.RESET}")
            self.logging(f"Result extract error: {e}")

        try:
            self.record_and_analize(all_curves, all_history_population)
        except Exception as e:
            print(f"{time_now()}: {Color.RED}Record and analyze error: {e}{Color.RESET}")
            self.logging(f"Record error: {e}")

    def record_and_analize(self, all_curves, all_history_population):
        """ plot the chart"""

        with open(os.path.join(self.folder_path, self.folder_name, "config.txt"), "a") as f:
            f.write(f"Function Type: {self.f_type}\n")
            f.write(f"Year: {self.year}\n")
            f.write(f"Name: {self.name}\n")
            f.write(f"Dimension: {self.dim}\n")
            f.write(f"Iterations: {self.iter}\n")
            f.write(f"Epochs: {self.epochs}\n")

        with open(os.path.join(self.folder_path, self.folder_name, "output.txt"), "a") as f:
            for i in range(self.epochs):
                f.write(f"Epoch {i+1} | Best fitness: {all_curves[i][-1]}\n")
                f.write(f"Epoch {i+1} | Best solution: {all_history_population[i][-1]}\n")

        fig, axes = plt.subplots(nrows=2, ncols=2, figsize=(12, 10))

        #################################################
        # plotting the curves(fitnesses in each iter) with different epochs

        for i, curve in enumerate(all_curves):
            axes[0, 0].plot(curve, label=f"Epoch {i+1}", color=plt.get_cmap('inferno')(i/10))
        axes[0, 0].set_title("Fitnesses with different Epoch")
        axes[0, 0].set_xlabel("Epoch")
        axes[0, 0].set_ylabel("Fitness")
        axes[0, 0].grid(True)
        axes[0, 0].legend(title="Epochs", loc="upper right")
        #################################################



        #################################################
        #plotting the best solution with different epochs
        best_population = np.array(all_history_population)[:,-1]
        population_dataframe = pd.DataFrame(
            {
                "Epoch": np.repeat(range(len(all_curves)), HyperParameters.Parameters['num_metaheuristic']),
                "Priority": best_population[:,::2].flatten(),
                "Weight": best_population[:,1::2].flatten(),
                "Param_name":np.tile(np.array(list(Optimizers.metaheuristic_list.keys())).flatten(),len(all_curves)),
            }
        )

        groups = population_dataframe['Epoch'].unique()
        unique_categories = population_dataframe['Param_name'].unique()
        colors = plt.get_cmap('viridis', len(unique_categories))
        color_map = {category: colors(i) for i, category in enumerate(unique_categories)}

        x = range(len(groups))
        width = 0.8

        label_register_set = set()
        for i, group in enumerate(groups):
            group_data = population_dataframe[population_dataframe['Epoch'] == group].sort_values(by='Priority')
            bottom = 0
            #total_weight = self.iter/(group_data['Weight'].sum())
            for index, row in group_data.iterrows():
                if row['Param_name'] not in label_register_set:
                    axes[0, 1].bar(x[i], row['Weight'], width, bottom=bottom,
                        color=color_map[row['Param_name']], label=row['Param_name'])
                    label_register_set.add(row['Param_name'])
                else:
                    axes[0, 1].bar(x[i], row['Weight'], width, bottom=bottom,
                        color=color_map[row['Param_name']])                
                bottom += row['Weight']

        axes[0, 1].set_xticks(x)
        axes[0, 1].set_xticklabels(groups)
        axes[0, 1].set_xlabel('Trial')
        axes[0, 1].set_ylabel('Time')
        axes[0, 1].set_title('Function activation time for each Trial')

        handles, labels = axes[0, 1].get_legend_handles_labels()
        by_label = dict(zip(labels, handles))
        axes[0, 1].legend(by_label.values(), by_label.keys(), title='Function', bbox_to_anchor=(1, 1))
        ###################################################################

        ###################################################################
        # plot the convergence speed
        try:
            min_value = np.min(all_curves, axis=1)
            max_value = np.max(all_curves, axis=1)
            eighty_percent_point = min_value + 0.15 * (max_value - min_value)
            first_reached = np.zeros(len(all_curves))
            for e,curve in enumerate(all_curves):
                for i, point in enumerate(curve):
                    if point <= eighty_percent_point[e]:
                        first_reached[e] = i
                        break
            
            axes[1, 0].plot([f"{i}" for i in range(len(all_curves))],first_reached, label="Convergence Speed", color=plt.get_cmap('inferno')(50))
            axes[1, 0].set_title("Convergence Speed")
            axes[1, 0].set_xlabel("Epoch")
            axes[1, 0].set_ylabel("Convergence to 80%")
            axes[1, 0].grid(True)
        except Exception as e:
            print(f"{time_now()}: {Color.RED}Error in convergence speed plot: {e}{Color.RESET}")
            self.logging(f"Error in convergence speed plot: {e}")

        ###################################################################
        plt.tight_layout()
        fig_save_path = os.path.join(self.folder_path, self.folder_name, "figure.png")
        plt.savefig(fig_save_path)
        print(f"{Color.GREEN}Figure saved to {fig_save_path}{Color.RESET}")
        self.logging(f"Figure saved to {fig_save_path}")


if __name__ == '__main__':

    MAINCONTROL()

    print(f"{Color.RED}Quitting...{Color.RESET}")
