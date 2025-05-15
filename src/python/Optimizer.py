""" optimizer configuration file"""
MODULE_TYPE="cpp"
if MODULE_TYPE == "python":
    from src.python.algos.EDGWO import EDGWOCONTROL
    from src.python.algos.GWO import GWOCONTROL
    from src.python.algos.CHGWOSCA import CHGWOSCACONTROL
    from src.python.algos.REEGWO import REEGWOCONTROL
    from src.python.algos.MSGWO import MSGWOCONTROL
    from src.python.algos.PSO import PSOCONTROL
    from src.python.algos.BES import BESCONTROL
    from src.python.algos.HHO import HHOCONTROL
    from src.python.algos.ChOA import ChOACONTROL
    from src.python.algos.SCSO import SCSOCONTROL
    from src.python.algos.REINEDGWO import REINEDGWOCONTROL
    from src.python.algos.DE import DECONTROL
    from src.python.algos.GA import GACONTROL
    from src.python.algos.SA import SACONTROL
    from src.python.algos.TABU import TSCONTROL
elif MODULE_TYPE == "cpp":
    from src.cpp.build import DE_cpp
    #from src.cpp.build import GWO_cpp
    #from src.cpp.build import PSO_cpp
    #from src.cpp.build import HHO_cpp
    #from src.cpp.build import ChOA_cpp
    #from src.cpp.build import SCSO_cpp
    #from src.cpp.build import BES_cpp
    #from src.cpp.build import REINEDGWO_cpp
    #from src.cpp.build import MSGWO_cpp
    #from src.cpp.build import EDGWO_cpp
    #from src.cpp.build import CHGWOSCA_cpp
    #from src.cpp.build import REEGWO_cpp

class Optimizers:
    """ This class stores all the metaheuristic algorithms"""
    metaheuristic_list = {
        #"EDGWO": EDGWOCONTROL,
        #"GWO": GWOCONTROL,
        #"CHGWOSCA": CHGWOSCACONTROL,
        #"REEGWO": REEGWOCONTROL,
        #"MSGWO": MSGWOCONTROL,
        #"BES": BESCONTROL,
        #"ChOA": ChOACONTROL,  # issue: UnboundLocalError: cannot access local variable 'sorted_indices' where it is not associated with a value
        #"PSO" :PSOCONTROL,
        #"HHO" :HHOCONTROL,
        #"SCSO":SCSOCONTROL,
        #"REINEDGWO": REINEDGWOCONTROL,
        "DE": DE_cpp,
        #"GA": GACONTROL,
        #"SA": SACONTROL, # issue: type nd.numpyfloat64 has no attribute 'len()'
        #"TABU": TSCONTROL # issue: type nd.numpyfloat64 has no attribute 'len()'
    }

class HyperParameters :
    """ This stores the configs for the heuristic algorithm"""
    heuristic = DE_cpp  #Hyperheuristic algorithm

    # heurictic and hyperheuristic parameters
    Parameters = {
        "meta_iter": 500,
        "hyper_iter": 500,
        "epoch": 6,
        "f_type": "continue",
        "num_metaheuristic": len(Optimizers.metaheuristic_list),
        "num_individual": 20,
        "num_param_each": 2,
        "ub": 10,
        "lb": 0
    }
