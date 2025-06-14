# -*- coding: utf-8 -*-
""" the entry point of the program"""
from concurrent.futures import ProcessPoolExecutor
import os
from datetime import datetime
import argparse
import traceback

import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
import matplotlib.ticker as mticker
import matplotlib as mpl

from src.python.Config import Configs
from src.python.Optimizer import HyperParameters, Optimizers
from src.python.hyperheuristic import HyperHeuristicTemplate, HyperEvaluationFunction

#mpl.rcParams['figure.dpi'] = 1200 # 設定全域 PPI 為 300
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
        self.obj_func = None    
        self.plot_scale = "Value"
        try:
            if Configs.execution_type == "single":
                self.get_args()
            elif Configs.execution_type == "all" :
                self.all_func()
            elif Configs.execution_type == "year":
                self.year_func(Configs.exec_year)
        except Exception as e:
            print(f"{time_now()}: {Color.RED}Runtime Error: {e}{Color.RESET}")
            self.logging(f"Runtime Error: {e}")
            traceback.print_exc()

    def logging(self,msg):
        """ log the data"""
        with open(os.path.join(self.folder_path, self.folder_name, "log.txt"), "a", encoding='utf-8') as f:
            f.write(f'[{time_now()}]: {msg}\n')
            
    def save_output(self, name, data, folder="data"):
        """ save the output"""
        if not os.path.exists(os.path.join(self.folder_path, self.folder_name, folder)):
            os.mkdir(os.path.join(self.folder_path, self.folder_name, folder))
        path = os.path.join(self.folder_path, self.folder_name, folder, name)
        np.save(path, data)
        self.logging(f"Output saved to {path}")

    def all_func(self):
        """ get all the functions from the dataset"""
        funcs_by_year = DataSet().all_funcs
        for f_type, years in funcs_by_year.items():
            for year, names in list(years.items())[::-1]:
                for name in names:
                    try:
                        idx = names[name].index('10')
                        self.dim = names[name][idx]
                        self.create_hyperheuristic_instance(f_type, year, name, names[name][idx])
                    except:
                        self.dim = names[name][0]
                        self.create_hyperheuristic_instance(f_type, year, name, names[name][0])

    def year_func(self, year):
        funcs_by_year = DataSet().all_funcs
        for f_type, years in funcs_by_year.items():
            try:
                names = years[year]
            except:
                raise ValueError("Invalid year")
            for name in names:
                try:
                    idx = names[name].index('10')
                    self.dim = names[name][idx]
                    self.create_hyperheuristic_instance(f_type, year, name, names[name][idx])
                except:
                    self.dim = names[name][0]
                    self.create_hyperheuristic_instance(f_type, year, name, names[name][0])
 
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
            except Exception as e:
                print(f"{Color.RED}Invalid input:{e}{Color.RESET}")
                continue
            
            self.iter = iterations
            self.epochs = epochs
            self.create_hyperheuristic_instance(f_type, year, name, dim)

    def create_hyperheuristic_instance(self, f_type=None, year=None, name=None, dim=None):
        """ create the hyper heuristic"""
        self.f_type = f_type
        self.year = year
        self.name = name
        self.dim = dim
        self.folder_path = os.path.join(os.getcwd(), "research_workspace", "auto-metaheuristic", "exp_result", "all_runner")
        self.folder_name = f"{self.f_type}_{self.year}_{self.name}_{self.dim}D_{self.iter}iter_{self.epochs}Ep"
        print(f"{Color.MAGENTA}DataSet: {self.f_type}-{self.year}-{self.name} - Dimension: {self.dim}{Color.RESET}\n")
        print(f"{Color.MAGENTA}Iter: {self.iter} -  Epoch: {self.epochs}{Color.RESET}\n")
        if not os.path.exists(os.path.join(self.folder_path, self.folder_name)):
            os.mkdir(os.path.join(self.folder_path, self.folder_name))
        self.logging(f"Running DataSet: {self.f_type}-{self.year}-{self.name} - Dimension: {self.dim}")
        
        try:
            self.obj_func = DataSet.get_function(self.f_type, self.year, self.name, int(self.dim))
        except Exception as e:
            print(f"{time_now()}: {Color.RED}Function load Error: {e}{Color.RESET}")
            self.logging(f"Function load error: {e}")

        all_curves = []
        all_history_population = []

        try:
            with ProcessPoolExecutor() as executor:
                futures = [executor.submit(
                    HyperHeuristicTemplate(
                        obj_function=self.obj_func,
                        hyper_iteration=self.iter,
                        color=list(Color.color_set.values())[i%7]).start)\
                            for i in range(self.epochs)]

                for i , future in enumerate(futures):
                    population, curve = future.result()
                    all_curves.append(curve)
                    all_history_population.append(population)


        except Exception as e:
            print(f"{time_now()}: {Color.RED}Runtime rror: {e}{Color.RESET}")
            self.logging(f"Runtime error: {e}")
            traceback.print_exc()

        try:
            for i, (curve, population) in enumerate(zip(all_curves, all_history_population)):
                print(f"{list(Color.color_set.values())[i%7]} Round {i+1} | Best fitness: {curve[-1]}{Color.RESET}")
                print(f"{list(Color.color_set.values())[i%7]} Round {i+1} | Best solution: {population[-1]}{Color.RESET}")
        except Exception as e:
            print(f"{time_now()}: {Color.RED}Result extract error: {e}{Color.RESET}")
            self.logging(f"Result extract error: {e}")
            traceback.print_exc()
            
        all_curves = np.array(all_curves)
        all_history_population = np.array(all_history_population)
        self.save_output("all_curves.npy", all_curves)
        self.save_output("all_history_population.npy", all_history_population)
        
        try:
            self.record_and_analize(all_curves, all_history_population)
        except Exception as e:
            print(f"{time_now()}: {Color.RED}Record and analyze error: {e}{Color.RESET}")
            self.logging(f"Record error: {e}")
            traceback.print_exc()
        self.logging(f"Finished!: DataSet: {self.f_type}-{self.year}-{self.name} - Dimension: {self.dim}")

    def record_and_analize(self, all_curves, all_history_population):
        """ plot the chart"""

        with open(os.path.join(self.folder_path, self.folder_name, "config.txt"), "a", encoding='utf-8') as f:
            f.write(f"Function Type: {self.f_type}\n")
            f.write(f"Year: {self.year}\n")
            f.write(f"Name: {self.name}\n")
            f.write(f"Dimension: {self.dim}\n")
            f.write(f"Iterations: {self.iter}\n")
            f.write(f"Epochs: {self.epochs}\n")
            f.write(f"num_individual: {HyperParameters.Parameters['num_individual']}\n")

        with open(os.path.join(self.folder_path, self.folder_name, "output.txt"), "a", encoding='utf-8') as f:
            for i in range(self.epochs):
                f.write(f"Round {i+1} | Best fitness: {all_curves[i][-1]}\n")
                f.write(f"Round {i+1} | Best solution: {all_history_population[i][-1]}\n")

        try:
            self.plot_scale = "Value"
            all_curves = np.array(all_curves)
            axes = plt
            self.draw_curves(axes, all_curves)
            self.draw_combination(axes, all_curves, all_history_population)
            self.draw_best_solution(axes, all_curves)
            self.draw_hypr_meta_compare(axes, all_curves, all_history_population)
        except Exception as e:
            print(f"{time_now()}: {Color.RED}Plotting error: {e}{Color.RESET}")
            self.logging(f"Plotting error: {e}")
            traceback.print_exc()

    def draw_curves(self, axes, all_curves):
        """ draw the curves"""
        fig, ax = plt.subplots(1,1, figsize=(12, 8))
        for i, curve in enumerate(all_curves):
            ax.plot(list(range(1,len(curve)+1)),curve, label=f"Round {i+1}", color=plt.get_cmap('inferno')(i/10), linestyle='--')
        ax.set_title("Fitnesses with different Rounds")
        ax.set_xlabel("Times of evaluation")
        ax.set_ylabel(f"Fitness {self.plot_scale}")
        ax.grid(True)
        ax.legend(title="Round", bbox_to_anchor=(1.05, 1), loc='upper left')
        ax.xaxis.set_major_locator(mticker.MaxNLocator(integer=True))
        
        plt.tight_layout()
        fig_save_path = os.path.join(self.folder_path, self.folder_name, f'CEC_{self.year}_{self.name}_1.svg')
        plt.savefig(fig_save_path)
        print(f"{Color.GREEN} Curves figure saved to {fig_save_path}{Color.RESET}")
        self.logging(f"Figure saved to {fig_save_path}")

    def draw_combination(self, axes, all_curves, all_history_population):
        """ draw the functoion combination of the best solution"""
        try:
            fig, ax = plt.subplots(1,1, figsize=(12, 8))
            best_population = all_history_population[:,-1]
            population_dataframe = pd.DataFrame(
                {
                    "Epoch": np.repeat(range(1,len(all_curves)+1), 
                                    HyperParameters.Parameters['num_metaheuristic']),
                    "Priority": best_population[:,::2].flatten(),
                    "Weight": best_population[:,1::2].flatten(),
                    "Param_name":np.tile(np.array(
                        list(Optimizers.metaheuristic_list.keys())).flatten(),len(all_curves)),
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
                total_weight = HyperParameters.Parameters['meta_iter']/(group_data['Weight'].sum())
                number_of_bars = len(group_data)
                for index,(df_index, row) in enumerate(group_data.iterrows()):
                    if number_of_bars-1 == index:
                        weight = HyperParameters.Parameters['meta_iter'] - bottom
                    else:
                        weight = row['Weight']*total_weight
                    if row['Param_name'] not in label_register_set:
                        ax.bar(x[i], weight, width, bottom=bottom,
                            color=color_map[row['Param_name']], label=row['Param_name'])
                        label_register_set.add(row['Param_name'])
                    else:
                        ax.bar(x[i], weight, width, bottom=bottom,
                            color=color_map[row['Param_name']])
                    bottom += weight

            ax.set_xticks(x)
            ax.set_xticklabels(groups)
            ax.set_xlabel('Round') 
            ax.set_ylabel('Times of evaluation')
            ax.set_title('Function activation time for each Round')

            handles, labels = ax.get_legend_handles_labels()
            by_label = dict(zip(labels, handles))
            ax.legend(by_label.values(), by_label.keys(), title='Function', bbox_to_anchor=(1.05, 1), loc='upper left')
            
            plt.tight_layout()
            fig_save_path = os.path.join(self.folder_path, self.folder_name, f'CEC_{self.year}_{self.name}_2.svg')
            plt.savefig(fig_save_path)
            
            print(f"{Color.GREEN} Combinations figure saved to {fig_save_path}{Color.RESET}")
            self.logging(f"Figure saved to {fig_save_path}")

        except Exception as e:
            print(f"{time_now()}: {Color.RED}Error in function combination plot: {e}{Color.RESET}")
            self.logging(f"Error in function combination plot: {e}")
            traceback.print_exc()

    def draw_best_solution(self, axes, all_curves):
        fig, ax = plt.subplots(1,1, figsize=(12, 8))
        """ draw the best solution"""
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

            x = list(range(1,len(all_curves)+1))
            
            self.save_output("first_reached.npy", first_reached)
            self.save_output("best_fitness.npy", min_value)

            #draw the convergence speed
            color1 = plt.get_cmap('inferno')(10)
            line1, = ax.plot(x,first_reached, label="80% pos", color=color1)
            ax.set_title("Key value of convergence")
            ax.set_xlabel("Round")
            ax.set_ylabel("Convergence to 80%", color=color1)
            ax.set_ylim(0, self.iter)
            ax.tick_params(axis='y', labelcolor=color1)

            ax.set_zorder(1)

            # draw box of best fitness
            ax2 = ax.twinx()
            color2 = plt.get_cmap('inferno')(200)
            bar1 = ax2.bar(x,max_value,color=color2, alpha=0.8, label="Best fitness")
            ax2.set_ylabel("Fitness", color=color2)
            ax2.tick_params(axis='y', labelcolor=color2)
            ax2.set_ylim(0, max_value.max()*2)
            ax2.set_zorder(0)

            ax.set_frame_on(False)
            ax.grid(True)
            charts = [line1, bar1]
            labels = [chart.get_label() for chart in charts]
            ax.legend(charts, labels, bbox_to_anchor=(1.05, 1), loc='upper left', title="Insight")
            
            plt.tight_layout()
            fig_save_path = os.path.join(self.folder_path, self.folder_name, f'CEC_{self.year}_{self.name}_3.svg')
            plt.savefig(fig_save_path)
            print(f"{Color.GREEN} Fitness figure saved to {fig_save_path}{Color.RESET}")
            self.logging(f"Figure saved to {fig_save_path}")

        except Exception as e:
            print(f"{time_now()}: {Color.RED}Error in convergence speed plot: {e}{Color.RESET}")
            self.logging(f"Error in convergence speed plot: {e}")
            traceback.print_exc()

    def draw_hypr_meta_compare(self, axes, all_curves, all_history_population):
        """ draw the population difference"""
        
        try:
            fig, ax = plt.subplots(1,1, figsize=(12, 8))
            best_population = all_history_population[np.argmin(all_curves[:,-1]),-1]

            hyper_curve = None
            with ProcessPoolExecutor() as executor:
                futures = [executor.submit(
                    HyperEvaluationFunction(
                        self.obj_func, Color.GREEN, "continue").evaluate,
                    best_population, i, True) for i in range(30)]

                for future in futures:
                    curve = future.result()
                    if hyper_curve is None:
                        hyper_curve = curve
                    else:
                        hyper_curve = np.vstack((hyper_curve,curve))
            self.logging(f"Metaheuristic comparison: {hyper_curve}")

            hyper_curve = np.average(hyper_curve,axis=0)
            meta_curve = None
            with ProcessPoolExecutor() as executor:
                
                for idx, (optname, opt) in enumerate(Optimizers.metaheuristic_list.items()):
                    futures = [(executor.submit(
                    opt.run(
                        HyperParameters.Parameters['meta_iter'],
                        self.obj_func.dim,
                        self.obj_func.func,
                        HyperParameters.Parameters['num_individual'],
                        self.obj_func.lb,
                        self.obj_func.ub
                    )))for trial in range(30)]
                    single_curves = None
                    for future in futures:
                        pop , curve = future.result()
                        if single_curves is None:
                            single_curves = curve
                        else:
                            single_curves = np.vstack((single_curves,curve))

                    single_avg = np.average(single_curves,axis=0)
                    if meta_curve is None:
                        meta_curve = single_avg
                    else:
                        meta_curve = np.vstack((meta_curve, single_avg))
                    ax.plot(single_avg,
                            label=f"{optname}", 
                            color=plt.get_cmap('inferno')(idx/10), linestyle='--', marker='o', markersize=1, linewidth=0.5)

            ax.plot(hyper_curve, label="HYPER",
                    color='red', zorder=10, linestyle='--', marker='x', markersize=3, linewidth=0.5)

            self.save_output("hyper_curve.npy", hyper_curve)
            self.save_output("meta_curve.npy", meta_curve)
            
            ax.set_xlabel('Times of evaluation')
            ax.set_ylabel(f'Fitness {self.plot_scale}')
            ax.set_title('Compare of metaheuristic algorithms')
            ax.legend(title="Heuristics", bbox_to_anchor=(1.05, 1), loc='upper left') 
            
            plt.tight_layout()
            fig_save_path = os.path.join(self.folder_path, self.folder_name, f'CEC_{self.year}_{self.name}_4.svg')
            plt.savefig(fig_save_path)
            print(f"{Color.GREEN} meta figure saved to {fig_save_path}{Color.RESET}")
            self.logging(f"Figure saved to {fig_save_path}")
        except Exception as e:
            print(f"{time_now()}: {Color.RED}Error in metaheuristic comparison: {e}{Color.RESET}")
            self.logging(f"Error in metaheuristic comparison: {e}")
            traceback.print_exc()
            
       

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Metaheuristic Algorithm Runner")
    parser.add_argument('--exec', type=str, default='single', choices=['single', 'all', "year"],
                        help="Execution type: single or all")
    parser.add_argument('--year', type=str, default='2022',
                        help="Year of the function to run")
    args = parser.parse_args()
    
    Configs.execution_type = args.exec
    if Configs.execution_type == "year":
        Configs.exec_year = args.year
    MAINCONTROL()

    print(f"{Color.RED}Quitting...{Color.RESET}")
