import numpy as np
import matplotlib.pyplot as plt

import concurrent.futures
import time

from ConfigClass import Configs
from ConfigClass import Color

from DataSet import DataSet
from tqdm import tqdm

class MAINCONTROL:
    def __init__(self, MAX_ITER, NUM_WOLVES, f_type, year, name, DIM):
        self.MAX_ITER = MAX_ITER
        self.NUM_WOLVES = NUM_WOLVES
        self.f_type = f_type
        self.year = year
        self.name = name    
        self.DIM = DIM

    def Worker(self, obj, EPOCH, idx):
        Result= None
        bar = tqdm(range(EPOCH), position=idx, leave=True, dynamic_ncols=True)
        for i in bar:
            bar.set_description(f"{obj.__name__:<16}-Epoch {i}/{EPOCH}")
            tmp = (1/(obj.Start()[-1])) if self.f_type == "GENE" or self.f_type == "DM" else obj.Start()[-1]
            Result = (Result * i + tmp)/ (i+1) if Result is not None else tmp
        print()

        return Result

    def Multi_Start(self, EPOCH):
        results = []
        print(f"{Color.GREEN}Starting Optimizers with parellel computing{Color.RESET}")
        with concurrent.futures.ProcessPoolExecutor() as executor:
            future_to_optimizer = {}

            #分發任務
            for idx, optimizer in enumerate(Configs.optimizers):
                opt = Configs.optimizers[optimizer](self.MAX_ITER, self.NUM_WOLVES, DataSet.get_function(self.f_type, self.year, self.name, self.DIM))
                #print(f"{Color.BLUE}\n\nStarting {opt.__name__} with {EPOCH} EPOCH{Color.RESET}")
                exer = executor.submit(self.Worker, opt, EPOCH, idx)

                future_to_optimizer[exer] = optimizer

            #全部完成後回收執行續
            for future in concurrent.futures.as_completed(future_to_optimizer):
                optimizer = future_to_optimizer[future]
                try:
                    result = future.result()
                    results.append((optimizer, result))
                except Exception as e:
                    print(f"{Color.RED}Error in {optimizer}:\n{e}{Color.RESET}")

        for optimizer, result in results:
            print(f"{Color.GREEN}{optimizer} completed{Color.RESET}")
            plt.plot(result, label=optimizer)

        print(f"{Color.GREEN}All Optimizers Completed, plotting the chart{Color.RESET}")
        plt.xlabel("Iterations")
        if self.f_type == "GENE" or self.f_type == "DM":
            plt.ylabel("Accuracy")
            plt.title(f"{self.name}-{self.DIM}D-{self.NUM_WOLVES}N-{EPOCH} EPOCH")
        else:
            
            plt.ylabel("Fitness Value (Log10)")
            plt.title(f"CEC{self.year}-{self.name}-{self.DIM}D-{self.NUM_WOLVES}N-{EPOCH} EPOCH")
        plt.legend()
        plt.show()


    def Single_Start(self, EPOCH):

        for idx, optimizer in enumerate(Configs.optimizers):
            print(f"{Color.MAGENTA}Starting {optimizer} works for {EPOCH} Epochs{Color.RESET}")
            obj = Configs.optimizers[optimizer](self.MAX_ITER, self.NUM_WOLVES,
                                                DataSet.get_function(I=self.f_type, II=self.year, III=self.name, dim=self.DIM))
            Result = self.Worker(obj, EPOCH, idx)
            print(f"{Color.GREEN}{optimizer} completed{Color.RESET}\n\n")
            plt.plot(Result, label=optimizer)
        
        print(f"{Color.GREEN}All Optimizers Completed, plotting the chart{Color.RESET}")
        plt.xlabel("Iterations")
        if self.f_type == "GENE":
            plt.ylabel("Accuracy")
            plt.title(f"{self.name}-{self.DIM}D-{self.NUM_WOLVES}N-{EPOCH} EPOCH")
        else:
            
            plt.ylabel("Fitness Value (Log10)")
            plt.title(f"CEC{self.year}-{self.name}-{self.DIM}D-{self.NUM_WOLVES}N-{EPOCH} EPOCH")
        plt.legend()
        plt.show()


if __name__ == '__main__':


    funcs_by_year = DataSet().all_funcs
    qc = ['q','Q','quit','Quit']
    f_type = None
    year = None
    name = None
    dim = None
    while f_type not in qc and  year not in qc and  name not in qc and  dim not in qc:
        
        f_type = input(f"Enter the Dataset param ({' / '.join(funcs_by_year)}): ") # DataSet
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

            name = input(f"Name param ({' / '.join(funcs_by_year[f_type][year])}): ").upper() # Function Name
            if name not in funcs_by_year[f_type][year]:
                print("Invalid param\n\n")
                continue
    
            dim = input(f"Dim param ({' / '.join(funcs_by_year[f_type][year][name])}): ") # Dimension
            if dim not in funcs_by_year[f_type][year][name]:
                print("Invalid param\n\n")
                continue

        elif(f_type == "GENE"):
            print(f"Name param:\n{'\n'.join(funcs_by_year[f_type])}")
            name = input(f"Enter the index: ")
            name = list(funcs_by_year['GENE'].keys())[int(name)-1]
            dim = funcs_by_year[f_type][name]
            print(f"Selected: {name} - Dimension: {dim}")
            
        elif f_type =="DM":
            name = "train_data"
            dim = 8
            
        else:
            print("Invalid function type")
            continue
        


        print(f"{Color.MAGENTA}DataSet: {f_type}-{year}-{name} - Dimension: {dim}{Color.RESET}\n")
        try: 
            ITER = int(input(f"{Color.BLUE}Input Ierations(500): {Color.RESET}"))
            EPOCH = int(input(f"{Color.BLUE}Input Epochs(10): {Color.RESET}")) 
            process = input(f"{Color.BLUE}Use multi process? (Y/N): {Color.RESET}")
        except:
            print(f"{Color.RED}Invalid input{Color.RESET}")
            continue
        if process=='Y' or process=='y':
            try:
                MAINCONTROL(MAX_ITER=ITER, NUM_WOLVES=30, f_type=f_type,year=year, name=name, DIM=int(dim)).Multi_Start(EPOCH)
                
            except Exception as e:
                print(f"{Color.RED}Error running with multiprocess: {e}{Color.RESET}")
                print(f"{Color.RED}Try to run with single process{Color.RESET}")
                MAINCONTROL(MAX_ITER=ITER, NUM_WOLVES=30, f_type=f_type,year=year, name=name, DIM=int(dim)).Single_Start(EPOCH)
        else:
            MAINCONTROL(MAX_ITER=ITER, NUM_WOLVES=30, f_type=f_type,year=year, name=name, DIM=int(dim)).Single_Start(EPOCH)


    print(f"{Color.RED}Quitting...{Color.RESET}")