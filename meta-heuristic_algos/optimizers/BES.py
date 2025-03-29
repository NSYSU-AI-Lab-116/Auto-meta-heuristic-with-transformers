import numpy as np
import matplotlib.pyplot as plt
from DataSet import DataSet

class BES:
    def __init__(self, obj_function, dim, lb, ub, num_par, max_iter, f_type, w=0.7, c1=1.5, c2=1.5):
        self.obj_function = obj_function
        self.dim = dim
        self.lb = np.array(lb)
        self.ub = np.array(ub)
        self.num_par = num_par
        self.max_iter = max_iter
        self.w = w
        self.c1 = c1
        self.c2 = c2
        self.f_type = f_type

        if self.f_type == "d":
            self.ub = np.append(self.ub[:], DataSet.NN_K)
            self.lb = np.append(self.lb[:], 1)
            self.dim+=1

        # 初始化
        self.particles = np.random.uniform(self.lb, self.ub, (self.num_par, self.dim))
        self.best_position = np.zeros((self.num_par, self.dim))  # 最佳位置

        self.energy = np.ones(self.num_par)  # 初始設定為1
        self.best_energy = np.full(self.num_par, np.inf)  # 最佳能量
        
        self.gbest_position = np.random.uniform(self.lb, self.ub, self.dim) # 最佳解(全局)
        self.gbest_energy = np.inf


    def optimize(self):
        convergence_curve = []

        for t in range(self.max_iter):
            for i in range(self.num_par):

                fitness = self.obj_function(self.particles[i])

                self.energy[i] = fitness 

                # 最佳位置
                if self.energy[i] < self.best_energy[i]:
                    self.best_energy[i] = self.energy[i]
                    self.best_position[i] = self.particles[i].copy()

                # 全局最佳
                if self.energy[i] < self.gbest_energy:
                    self.gbest_energy = self.energy[i]
                    self.gbest_position = self.particles[i].copy()
                
            for i in range(self.num_par):
                r1 = np.random.rand(self.dim)
                r2 = np.random.rand(self.dim)

                # 更新速度
                velocity = self.w * self.particles[i] + self.c1 * r1 * (self.best_position[i] - self.particles[i]) + self.c2 * r2 * (self.gbest_position - self.particles[i])

                # 更新位置
                self.particles[i] = self.particles[i] + velocity

                # 邊界處理
                if self.f_type == "d":
                    self.particles[i][-1] = np.clip(self.particles[i][-1], 1, DataSet.NN_K)
                    self.particles[i][:-1] = np.clip(self.particles[i][:-1], DataSet.param_LB, DataSet.param_UB)
                else:
                    self.particles[i] = np.clip(self.particles[i], self.lb, self.ub)

            convergence_curve.append(self.gbest_energy)

        return self.gbest_position, self.gbest_energy, convergence_curve, self.particles
    

class BESCONTROL:
    __name__ = "BES"
    def __init__(self,MAX_ITER, NUM_WOLVES,FUNCTION):
        self.MAX_ITER = MAX_ITER
        self.NUM_PARTICLES = NUM_WOLVES

        
        self.UB = FUNCTION.ub
        self.LB = FUNCTION.lb
        self.DIM= FUNCTION.dim
        self.f = FUNCTION.func
        self.f_type = FUNCTION.f_type

    def Start(self):
        bes = BES(obj_function=self.f, dim=self.DIM, lb=self.LB, ub=self.UB, 
                    num_par=self.NUM_PARTICLES, max_iter=self.MAX_ITER, f_type=self.f_type)
        best_position, best_value, curve, particles = bes.optimize()
        
        """ print("Best solution found:", best_position)
        print("Best fitness:", best_value) """
        if self.f_type == "d":
            return (particles, np.array(curve))
        else:
            return (particles, np.log10(curve))




if __name__ == '__main__':

    funcs_by_year =  DataSet.funcs_years

    # 設定參數
    MAX_ITER = 500
    NUM_PARTICLES = 30
    DIM = 10

    # CEC 函式呼叫方法  
    for year in funcs_by_year['CEC']:
        for func_name in funcs_by_year['CEC'][year]:
            function = DataSet.get_function(year,func_name,DIM)  # 取得CEC Year年度，維度為 DIM 之 F1 函式的資訊
            UB = function.ub
            LB = function.lb
            f = function.func # 取得函式
            # 計算函式值 f([多個維度組成的陣列])   -> 例如 f([x,y])

    
            # 執行 BES
            bes = BES(obj_function=f, dim=DIM, lb=LB, ub=UB, num_par=NUM_PARTICLES, max_iter=MAX_ITER)
            best_position, best_value, curve, particles  = bes.optimize()

            print(f"[CEC {year}-{func_name}] Best solution found:", best_position)
            print(f"[CEC {year}-{func_name}] Best fitness:", best_value)

            # 繪製收斂曲線
            plt.plot(np.log10(curve))
            plt.xlabel("Iterations")
            plt.ylabel("Fitness Value (Log10)")
            plt.title(f"BES Convergence {year}-{func_name}-{DIM}D")
            plt.show()
