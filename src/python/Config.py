# Trial for importing the optimizers directly
import opfunu as of
class Configs:
    """ This class is the main configuration of the project"""
    execution_type = "all" # ["single", "all", "year"]
    exec_year = "0000"
    class Color:
        """stores the color codes for the console"""
        color_set = {
            "RED" : '\033[31m',
            "GREEN" : '\033[32m',
            "YELLOW" : '\033[33m',
            "BLUE" : '\033[34m',
            "MAGENTA" : '\033[35m',
            "CYAN" : '\033[36m',
            "WHITE" : '\033[37m',
        }
        
        RED = color_set["RED"]
        GREEN = color_set["GREEN"]
        YELLOW = color_set["YELLOW"]
        BLUE = color_set["BLUE"]
        MAGENTA = color_set["MAGENTA"]
        CYAN = color_set["CYAN"]
        WHITE = color_set["WHITE"]
        RESET = '\033[0m'

    class DataSet:
        """        This class handle the dataset """
        NN_K = 12
        param_UB = 10
        param_LB = -10
        def __init__(self):
            self.all_funcs= {"CEC":self.get_cec_data_dict()}

        @staticmethod
        def get_function(f_type, func_year, func_name, dim):
            """ Get functions by type, year, name and dimension"""
            if f_type == "CEC":
                return Configs.CECFUNC(func_year, func_name, dim).get_function_info()
            raise ValueError("Function not found")


        def get_cec_data_dict(self):
            """ Make up all the CEC func to a dict from opfunu"""

            cec_dict = {}
            years = of.cec_based.__dict__
            for year in years.keys():
                year_dict = {}
                if(year[0]=='c' and year!='cec'):
                    functions = years[year].__dict__
                    for func in functions.keys():
                        func_list=[]
                        if(func[0]=='F'):
                            dimensions = functions[func]
                            diml = dimensions().dim_supported
                            if not isinstance(diml, list):
                                continue
                            for dim in diml:
                                func_list.append(str(dim))
                            if len(func_list)>0:
                                year_dict.update({func[0:-4:1]:func_list})
                    if len(year_dict)>0:
                        cec_dict.update({year[-4:]:year_dict})
            return cec_dict

    class CECFUNC:
        """ ths clas handle the function get of the Opfunu library"""
        def __init__(self,year,function_name,dim):
            self.dim = dim
            self.year = year
            self.function_name = function_name
            self.source = of.get_functions_by_classname(function_name+year)[0](ndim = self.dim)
            if self.source is None:
                raise ValueError("Function not found")


        def get_function_info(self):
            """ get the function info"""
            return Configs.FunctionStruct(
                self.source.evaluate,self.dim,self.source.lb.tolist(),
                self.source.ub.tolist(),"continue",self.year,self.function_name)

    class FunctionStruct:
        """ this class is the function struct of the function"""
        def __init__(self,func,dim,lb,ub,function_type,year,function_name):
            self.func = func
            self.dim = dim
            self.lb = lb
            self.ub = ub
            self.f_type =  function_type
            self.year = year
            self.name = function_name



if __name__ == '__main__':
    c = Configs.DataSet()
    print(c.get_cec_data_dict())
    f = c.get_function("CEC", "2022", "F1", 2)
    print(f.func([1, 2]))
