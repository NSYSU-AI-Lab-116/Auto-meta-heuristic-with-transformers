
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

class Color:
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    RESET = '\033[0m'

class Configs:
    optimizers = {
        #"EDGWO": EDGWOCONTROL,
        #"GWO": GWOCONTROL,
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
        "GA": GACONTROL,
        "SA": SACONTROL,
        "TABU": TSCONTROL
    }
    

