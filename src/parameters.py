"""
Parametri del modello Calcium Looping basati sul paper
"""

class ModelParameters:
    """Parametri del modello estratti dal paper di Ortiz et al."""
    
    def __init__(self):
        # Parametri deattivazione da Tabella 1
        # Fase cinetica
        self.j_kinetic = 0.676          # costante deattivazione
        self.Xr_kinetic = 0.0296        # conversione residua
        self.X1_kinetic = 0.218        # conversione 1° ciclo
        
        # Fase diffusiva
        self.j_diffusion = 0.871        # costante deattivazione
        self.Xr_diffusion = 0.0408      # conversione residua
        self.X1_diffusion = 0.263       # conversione 1° ciclo
        
        # Costanti cinetiche
        self.ks = 6.7e-10              # costante cinetica (m⁴/mol·s)
        self.Deff = 6.5e-5             # costante diffusione (m³/mol·s)
        
        # Parametri operativi da Tabella 2
        self.f0 = 0.15                 # frazione molare CO2 ingresso
        self.T_carbonator = 650        # temperatura carbonatore (°C)
        self.T_calciner = 950          # temperatura calcinatore (°C)
        self.P = 1.0                   # pressione (bar)
        self.h = 50e-9                 # spessore strato prodotto (m)
        
        # Parametri per test
        self.t_kinetic = 0.3           # tempo fase cinetica (0.3 min = 18 sec)
        self.T0 = 5                    # tempo totale test TGA (5 min = 300 s)
        
        # Parametri per modello di cattura (da Tabella 2 del paper)
        self.mCO2_per_MW = 0.1                # kg/s per MW
        self.Vgas_per_MW = 1.15               # m³/s per MW di gas di combustione
        self.MCaO = 56.08                     # massa molare CaO (g/mol)
        self.MCaCO3 = 100.09                  # massa molare CaCO3 (g/mol)
        self.VM_CaCO3 = 36.9e-6               # volume molare CaCO3 (m³/mol)
        self.rho_CaO = 3340                   # densità CaO (kg/m³)
        self.rho_gas = 1.2                    # densità gas (kg/m³)
        
        # Parametri di equilibrio
        self.f_equilibrium = 0.10             # frazione CO2 equilibrio a 650°C
        
        # Parametri reattore
        self.reactor_area = 100               # area sezione reattore (m²)

        # NUOVE COSTANTI - Masse molari in kg/mol per coerenza
        self.M_CO2_kg = 0.04401               # kg/mol
        self.M_CaO_kg = 0.05608               # kg/mol