from src.PFC import PFC_Sim

if __name__ == "__main__":
    pfc = PFC_Sim("config.yaml")
    pfc._simulate()
