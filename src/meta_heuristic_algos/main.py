# -*- coding: utf-8 -*-
""" the entry point of the program"""
from concurrent.futures import ProcessPoolExecutor
from matplotlib import pyplot as plt
import numpy as np
import pandas as pd

from src.meta_heuristic_algos.Config import Configs
from src.meta_heuristic_algos.Optimizer import HyperParameters, Optimizers
from src.meta_heuristic_algos.hyperheuristic import HyperHeuristicTemplate

Color = Configs.Color
DataSet = Configs.DataSet

class MAINCONTROL:
    """ This class is the main control of the program"""
    def __init__(self):
        #self.f_type, self.year, self.name, self.dim, self.iter, self.epochs = self.get_args()
        self.f_type, self.year, self.name, self.dim, self.iter, self.epochs = "CEC", "2022", "F12", 2, 300, 10
        HyperParameters.Parameters["epoch"] = self.epochs
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
        
        obj_func = DataSet.get_function(self.f_type, self.year, self.name, int(self.dim))

        all_curves = []
        all_history_population = []

        with ProcessPoolExecutor(max_workers=12) as executor:
            futures = [executor.submit(HyperHeuristicTemplate(obj_function=obj_func,\
                        hyper_iteration=self.iter,color=list(Color.color_set.values())[i%7]).start)\
                        for i in range(self.epochs)]

            for i , future in enumerate(futures):
                population, curve = future.result()
                print(f"{Color.YELLOW} Epoch {i} | Best solution: {population[-1]}{Color.RESET}")
                all_curves.append(curve)
                all_history_population.append(population)


        for i, (curve, population) in enumerate(zip(all_curves, all_history_population)):
            print(f"{list(Color.color_set.values())[i%7]} Epoch {i+1} | Best fitness: {curve[-1]}{Color.RESET}")
            print(f"{list(Color.color_set.values())[i%7]} Epoch {i+1} | Best solution: {population[-1]}{Color.RESET}")

        self.plot_chart(all_curves, all_history_population)


    def plot_chart(self, all_curves: list, all_history_population: list):
        """ plot the chart"""
        fig, axes = plt.subplots(nrows=2, ncols=2, figsize=(12, 10))

        #################################################
        # plotting the curves(fitnesses in each iter) with different epochs
        plt.colormaps
        for i, curve in enumerate(all_curves):
            axes[0, 0].plot(curve, label=f"Epoch {i+1}", color=plt.get_cmap('managua')(i/10))
        axes[0, 0].set_title("Fitnesses with different Epoch")
        axes[0, 0].set_xlabel("Epoch")
        axes[0, 0].set_ylabel("Fitness")
        axes[0, 0].grid(True)
        axes[0, 0].legend(title="Epochs", loc="upper right")
        #################################################



        #################################################
        #plotting the best solution with different epochs
        best_population = np.array(all_history_population,dtype=np.float32)[:,-1]
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
            group_data = population_dataframe[population_dataframe['Epoch'] == group]\
                .sort_values(by='Priority')
            bottom = 0
            total_weight = 500/group_data['Weight'].sum()
            for index, row in group_data.iterrows():
                if row['Param_name'] not in label_register_set:
                    axes[0, 1].bar(x[i], row['Weight']*total_weight, width, bottom=bottom,
                        color=color_map[row['Param_name']], label=row['Param_name'])
                else:
                    axes[0, 1].bar(x[i], row['Weight'], width, bottom=bottom,
                        color=color_map[row['Param_name']])
                label_register_set.add(row['Param_name'])
                bottom += row['Weight']
        axes[0, 1].plot(x, all_curves[:,-1], color='black', linestyle='--', label='Best fitness')
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
            eighty_percent_point = np.multiply(np.min(all_curves,axis=1) , 1.2)
            first_reached = np.zeros(len(all_curves))
            for e,curve in enumerate(all_curves):
                for i, point in enumerate(curve):
                    if point <= eighty_percent_point[e]:
                        first_reached[e] = i
                        break
            
            axes[1, 0].plot([f"Epoch-{i}" for i in range(len(all_curves))],first_reached, label="Convergence Speed", color=plt.get_cmap('inferno')(50))
            axes[1, 0].set_title("Convergence Speed")
            axes[1, 0].set_xlabel("Epoch")
            axes[1, 0].set_ylabel("Convergence to 80%")
            axes[1, 0].grid(True)
        except Exception as e:
            print(f"{Color.RED}Error in convergence speed plot: {e}{Color.RESET}")

        ###################################################################
        plt.tight_layout()
        plt.show()

if __name__ == '__main__':

    MAINCONTROL()

    print(f"{Color.RED}Quitting...{Color.RESET}")
