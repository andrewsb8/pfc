from src.PFC import PFC_Sim

if __name__ == "__main__":
    pfc = PFC_Sim("config.yaml")
    try:
        pfc._simulate()
    except Exception:
        pfc.log.exception("------ Fatal Error Stack Trace ------")
