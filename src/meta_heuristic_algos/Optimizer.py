
from optimizers.EDGWO import EDGWOCONTROL
from optimizers.GWO import GWOCONTROL
from optimizers.CHGWOSCA import CHGWOSCACONTROL
from optimizers.REEGWO import REEGWOCONTROL
from optimizers.MSGWO import MSGWOCONTROL
from optimizers.PSO import PSOCONTROL
from optimizers.BES import BESCONTROL
from optimizers.HHO import HHOCONTROL
from optimizers.ChOA import ChOACONTROL
from optimizers.SCSO import SCSOCONTROL
from optimizers.REINEDGWO import REINEDGWOCONTROL
from optimizers.DE import DECONTROL
from optimizers.GA import GACONTROL
from optimizers.SA import SACONTROL
from optimizers.TABU import TSCONTROL

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
    """ This stores the configs for the hyperheuristic algorithm"""
    heuristic = DECONTROL
    Parameters = {
        "max_iter": 500,
        "epoch": 10,
        "dim": None,
        "num_individual": 30,
        "num_param_each": 2,
        "ub": [10,10]*2,
        "lb": [0,0]*2,
    }
