""" optimizer configuration file"""
from src.meta_heuristic_algos.algos.EDGWO import EDGWOCONTROL
from src.meta_heuristic_algos.algos.GWO import GWOCONTROL
from src.meta_heuristic_algos.algos.CHGWOSCA import CHGWOSCACONTROL
from src.meta_heuristic_algos.algos.REEGWO import REEGWOCONTROL
from src.meta_heuristic_algos.algos.MSGWO import MSGWOCONTROL
from src.meta_heuristic_algos.algos.PSO import PSOCONTROL
from src.meta_heuristic_algos.algos.BES import BESCONTROL
from src.meta_heuristic_algos.algos.HHO import HHOCONTROL
from src.meta_heuristic_algos.algos.ChOA import ChOACONTROL
from src.meta_heuristic_algos.algos.SCSO import SCSOCONTROL
from src.meta_heuristic_algos.algos.REINEDGWO import REINEDGWOCONTROL
from src.meta_heuristic_algos.algos.DE import DECONTROL
from src.meta_heuristic_algos.algos.GA import GACONTROL
from src.meta_heuristic_algos.algos.SA import SACONTROL
from src.meta_heuristic_algos.algos.TABU import TSCONTROL

class Optimizers:
    """ This class stores all the metaheuristic algorithms"""
    metaheuristic_list = {
        #"EDGWO": EDGWOCONTROL,
        "GWO": GWOCONTROL,
        #"CHGWOSCA": CHGWOSCACONTROL,
        #"REEGWO": REEGWOCONTROL,
        #"MSGWO": MSGWOCONTROL,
        #"BES": BESCONTROL,
        #"ChOA": ChOACONTROL,
        #"PSO" :PSOCONTROL,
        #"HHO" :HHOCONTROL,
        #"SCSO":SCSOCONTROL,
        #"REINEDGWO": REINEDGWOCONTROL,
        "DE": DECONTROL,
        #"GA": GACONTROL,
        #"SA": SACONTROL,
        #"TABU": TSCONTROL
    }

class HyperParameters :
    """ This stores the configs for the heuristic algorithm"""
    heuristic = DECONTROL  #Hyperheuristic algorithm
    
    # heurictic and hyperheuristic parameters
    Parameters = {
        "max_iter": 500,
        "epoch": 10,
        "dim": None,
        "num_individual": 30,
        "num_param_each": 2,
        "ub": [10,10]*2,
        "lb": [0,0]*2,
    }
