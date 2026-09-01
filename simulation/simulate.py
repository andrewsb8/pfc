import sys
from src.PFC import PFC_Sim

if __name__ == "__main__":
    config_fname = sys.argv[1]
    pfc = PFC_Sim(config_fname)
    try:
        pfc._simulate()
    except Exception:
        pfc.log.exception("------ Fatal Error Stack Trace ------")
