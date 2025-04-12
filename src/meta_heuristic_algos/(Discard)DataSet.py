import opfunu as of
import scipy.io as sio
import numpy as np
from sklearn.neighbors import KNeighborsClassifier as KNN
from sklearn.model_selection import train_test_split

class DataSet:
    funcs_years= {
        "CEC":{
            "2021": ["F3", "F4", "F6", "F7", "F8", "F9", "F10"],
            "2022": ["F2", "F6", "F7", "F8", "F9", "F10", "F11", "F12"]
        },
        "gene":{
            
        },
        "DM":{
            
        }
    }
    NN_K = 12
    param_UB = 10
    param_LB = -10

    def __init__(self):

        self.all_funcs= {"CEC":self.get_CEC_data_dict(),
                        "GENE":self.get_GENE_data_dict(),
                        "DM":{}
                        }

    def get_function(I,II,III,dim):
        if I == "CEC":
            return CECFUNC(II,III,dim).get_function_info()
        else:
            raise ValueError("Function not found")
        """ elif I == "GENE":
            return GENEFUNC(III,dim).get_function_info()
        elif I == "DM":
            return DMFUNC(III,dim).get_function_info() """
        


    def get_CEC_data_dict(self):
        CEC_DICT = {}
        directI = of.cec_based.__dict__
        for year in directI.keys():
            year_dict = {}
            if(year[0]=='c' and year!='cec'):
                directII = directI[year].__dict__
                for func in directII.keys():
                    func_list=[]
                    if(func[0]=='F'):
                        directIII = directII[func]
                        diml = directIII().dim_supported
                        if type(diml) is not list:
                            continue
                        for dim in diml:
                            func_list.append(str(dim))
                        
                        if len(func_list)>0:
                            year_dict.update({func[0:-4:1]:func_list})
                if len(year_dict)>0:
                    CEC_DICT.update({year[-4:]:year_dict})
        return CEC_DICT
    
    def get_GENE_data_dict(self):
        return {
            "1.  ALLAML":7129,
            "2.  colon":2000,
            "3.  Leukemia_1":5327,
            "4.  Leukemia_2":7129,
            "5.  Leukemia_3":11225,
            "6.  Leukemia":3312,
            "7.  lung_discrete":325,
            "8.  lung":3312,
            "9.  lymphoma":4026,
        }
        

class CECFUNC:
    def __init__(self,year,function_name,dim):
        self.dim = dim
        self.source = of.get_functions_by_classname(function_name+year)[0](ndim = self.dim)
        if self.source is None:
            raise ValueError("Function not found")    
    
    def get_function_info(self):
        return function_struct(self.func,self.dim,self.source.lb.tolist(),self.source.ub.tolist(),"continue")

    def func(self,x):
        F = self.source.evaluate(x)
        return F
    
class GENEFUNC:
    def __init__(self,name,dim):
        self.name = name[4:]
        self.dim = dim
        self.data = sio.loadmat(f'_geneData/{self.name}.mat')['X']
        self.labels = sio.loadmat(f'_geneData/{self.name}.mat')['Y']
        train_test_split(self.data, self.labels, test_size=0.2, random_state=42)
        self.X_train, self.X_test = self.data[:int(len(self.data)*0.8)], self.data[int(len(self.data)*0.8):]
        self.Y_train, self.Y_test = self.labels[:int(len(self.labels)*0.8)], self.labels[int(len(self.labels)*0.8):]
        self.Y_test = self.Y_test.ravel()
        self.Y_train = self.Y_train.ravel()

    def get_function_info(self):
        return function_struct(self.func,self.dim,np.max(self.data,axis=0),np.min(self.data,axis=0),"d")
    
    def func(self,x):
        """ 
        間單來說就是優化每個特徵的參數，
        然後把這個參數帶入到資料後用KNN分類器，
        計算準確率來當作適應函數
        """
        weights = x[:-1]
        k = int(round(x[-1]))

        k = max(1, min(20, k))

        X_train_weighted = self.X_train * weights
        X_test_weighted = self.X_test * weights

        if np.isnan(weights).any():
            print(weights)
            raise ValueError("Weights contain NaN values")
        elif np.isnan(k).any():
            print(k)
            raise ValueError("k contains NaN values")
        elif np.isnan(X_train_weighted).any():
            print(X_train_weighted)
            raise ValueError("X_train_weighted contains NaN values")
        

        knn = KNN(n_neighbors=k)
        knn.fit(X_train_weighted, self.Y_train)
        
        accuracy = knn.score(X_test_weighted, self.Y_test)
        return 1/accuracy  




class DMFUNC:
    def __init__(self,name,dim):
        self.name = name[4:]
        self.dim = dim
        raw = np.loadtxt(f'_geneData/DM/test_data.csv', delimiter=',',dtype='str')[1:]
        #print(raw)
        self.data = raw[:,:-1].astype(np.float64)
        self.labels = raw[:, -1:].astype(np.int8)
        
        train_test_split(self.data, self.labels, test_size=0.2, random_state=42)
        self.X_train, self.X_test = self.data[:int(len(self.data)*0.8)], self.data[int(len(self.data)*0.8):]
        self.Y_train, self.Y_test = self.labels[:int(len(self.labels)*0.8)], self.labels[int(len(self.labels)*0.8):]
        self.Y_test = self.Y_test.ravel()
        self.Y_train = self.Y_train.ravel()

    def get_function_info(self):
        return function_struct(self.func,self.dim,np.max(self.data,axis=0),np.min(self.data,axis=0),"d")
    
    def func(self,x):
        weights = x[:-1]
        k = int(round(x[-1]))

        k = max(1, min(20, k))

        X_train_weighted = self.X_train * weights
        X_test_weighted = self.X_test * weights

        if np.isnan(weights).any():
            print(weights)
            raise ValueError("Weights contain NaN values")
        elif np.isnan(k).any():
            print(k)
            raise ValueError("k contains NaN values")
        elif np.isnan(X_train_weighted).any():
            print(X_train_weighted)
            raise ValueError("X_train_weighted contains NaN values")

        knn = KNN(n_neighbors=k)
        knn.fit(X_train_weighted, self.Y_train)

        accuracy = knn.score(X_test_weighted, self.Y_test)
        return 1/accuracy




class function_struct:
    def __init__(self,func,dim,lb,ub,function_type):
        self.func = func
        self.dim = dim
        self.lb = lb
        self.ub = ub
        self.f_type =  function_type


DataSet().get_GENE_data_dict