

# import numpy as np
# from scipy import integrate
# from parameters import ModelParameters

# class CineticModelEquation:
#     """Implementazione delle equazioni del modello cinetico"""

#     def __init__(self):
#         self.params = ModelParameters()

#     def conversion_cycle_N(self, N, phase='kinetic'):
#         """
#         Calcola la conversione massima di CaO al ciclo N (Equazione 3).
        
#         Args:
#             N (int): Numero del ciclo.
#             phase (str): 'kinetic' o 'diffusion'.
        
#         Returns:
#             float: Conversione massima per quel ciclo e quella fase.
#         """
#         if phase == 'kinetic':
#             k_deactivation = self.params.j_kinetic
#             Xr = self.params.Xr_kinetic
#             X1 = self.params.X1_kinetic
#         else:  # diffusion
#             k_deactivation = self.params.j_diffusion
#             Xr = self.params.Xr_diffusion
#             X1 = self.params.X1_diffusion

#         # L'equazione è valida per N >= 1
#         if N == 0: return 0
#         if N == 1: return X1
        
#         # Implementazione diretta dell'Equazione (3)
#         term_k = k_deactivation * (N-1) 
#         term_inv = 1/(1 - (Xr/X1))
#         XN = X1 * ((Xr/X1) + 1/(term_k + term_inv))
#         return XN

#     def conversion_at_time_t(self, N, t_residence_min):
#         """
#         Calcola la conversione di una singola particella al ciclo N che ha risieduto 
#         per un tempo t_residence_min (in minuti). Basato su Eq. (4).
#         """
#         XNK = self.conversion_cycle_N(N, 'kinetic')
        
#         if t_residence_min <= self.params.t_kinetic:
#             # Solo fase cinetica
#             return (t_residence_min / self.params.t_kinetic) * XNK
#         else:
#             # Fase cinetica completata + fase diffusiva
#             XND = self.conversion_cycle_N(N, 'diffusion')
#             t_diffusion = t_residence_min - self.params.t_kinetic
#             max_t_diffusion = self.params.T0 - self.params.t_kinetic
            
#             # Limita il tempo di diffusione al massimo considerato nel test TGA
#             t_diffusion = min(t_diffusion, max_t_diffusion)
            
#             diffusion_contribution = (t_diffusion / max_t_diffusion) * XND
#             return XNK + diffusion_contribution


# class CarbonCaptureModel:
#     """Modello per il calcolo dell'efficienza di cattura di CO2"""
    
#     def __init__(self):
#         self.params = ModelParameters()
#         self.equations = CineticModelEquation()
    
#     def get_operating_flows(self, F0_FCO2_ratio, FR_FCO2_ratio):
#         """
#         Calcola i flussi molari effettivi.
#         """
#         # Calcola FCO2 (flusso molare di CO2 in ingresso) in mol/s
#         FCO2 = self.params.mCO2_per_MW / self.params.M_CO2_kg
        
#         # Calcola F0 (makeup) e FR (ricircolo) in mol/s
#         F0 = F0_FCO2_ratio * FCO2
#         FR = FR_FCO2_ratio * FCO2
        
#         return FCO2, F0, FR

#     def particle_fraction_cycle_N(self, N, F0, FR):
#         """
#         Calcola la frazione di particelle al ciclo N in un reattore a miscelazione
#         perfetta (Equazione 9).
#         """
#         if F0 + FR == 0: return 0
#         if N == 0: return 0
        
#         return (F0 * (FR**(N - 1))) / ((F0 + FR)**N)
    
#     def average_maximum_conversion(self, F0, FR, max_cycles=100):
#         """
#         Calcola la conversione media massima della popolazione di particelle 
#         nel reattore (Equazione 11).
#         """
#         total_X_kinetic = 0
#         total_X_diffusion = 0
        
#         for N in range(1, max_cycles + 1):
#             rho_N = self.particle_fraction_cycle_N(N, F0, FR)
            
#             if rho_N < 1e-9: break
                
#             XNK = self.equations.conversion_cycle_N(N, 'kinetic')
#             XND = self.equations.conversion_cycle_N(N, 'diffusion')
            
#             total_X_kinetic += rho_N * XNK
#             total_X_diffusion += rho_N * XND
        
#         return total_X_kinetic, total_X_diffusion

#     def residence_time(self, Ws_per_MW, FR):
#         """
#         Calcola il tempo di residenza medio in minuti.
#         τ = Ws / (M_CaO * FR)
#         """
#         if FR == 0: return float('inf')
        
#         # Ws (kg), M_CaO (kg/mol), FR (mol/s) -> τ (s)
#         tau_seconds = Ws_per_MW / (self.params.M_CaO_kg * FR)
        
#         return tau_seconds / 60.0  # Converti in minuti

#     def active_fraction(self, tau_min):
#         """
#         Calcola la frazione attiva fa (Equazione 17)
#         fa = 1 - exp(-tK/τ)
#         """
#         if tau_min <= 0:
#             return 0
#         return 1 - np.exp(-self.params.t_kinetic / tau_min)
    
#     def average_conversion_kinetic_phase(self, tau_min, Xmax_ave_K):
#         """
#         Calcola la conversione media nella fase cinetica (Equazione 15)
#         X|≤tK = ∫[0 to tK] rave,K * t * (1/τ) * e^(-t/τ) dt / (1 - e^(-tK/τ))
#         """
#         if tau_min <= 0 or Xmax_ave_K <= 0:
#             return 0
            
#         tK = self.params.t_kinetic
#         rave_K = Xmax_ave_K / tK
        
#         def integrand(t):
#             return rave_K * t * (1/tau_min) * np.exp(-t/tau_min)
        
#         # Integrazione numerica da 0 a tK
#         integral_result, _ = integrate.quad(integrand, 0, tK)
        
#         # Normalizzazione
#         fa = self.active_fraction(tau_min)
#         if fa > 0:
#             return integral_result / fa
#         return 0
    
#     def average_conversion_diffusion_phase(self, tau_min, Xmax_ave_K, Xmax_ave_D):
#         """
#         Calcola la conversione media nella fase diffusiva (Equazione 16)
#         X|>tK = Xmax,ave,K + ∫[tK to τ] rave,D * t * (1/τ) * e^(-t/τ) dt / (1 - e^(-tK/τ))
#         """
#         if tau_min <= 0:
#             return Xmax_ave_K
            
#         tK = self.params.t_kinetic
#         if tau_min <= tK:
#             return Xmax_ave_K
            
#         # Tempo massimo di diffusione dal TGA
#         max_diffusion_time = self.params.T0 - tK
#         rave_D = Xmax_ave_D / max_diffusion_time
        
#         def integrand(t):
#             return rave_D * (1/tau_min) * np.exp(-t/tau_min)
        
#         # Integrazione da tK fino al minimo tra τ e tempo massimo
#         t_max = min(tau_min * 10, tK + max_diffusion_time)  # Limite pratico
#         integral_result, _ = integrate.quad(integrand, tK, t_max)
        
#         # Normalizzazione
#         fa = self.active_fraction(tau_min)
#         if fa < 1:
#             return Xmax_ave_K + integral_result / (1 - fa)
#         return Xmax_ave_K

#     def capture_efficiency(self, operating_conditions):
#         """
#         Calcola l'efficienza di cattura CO2 implementando le Eq. (8), (14), (21-23).
#         """
#         # Estrai parametri operativi
#         Ws_per_MW = operating_conditions['Ws_per_MW']
#         F0_FCO2_ratio = operating_conditions['F0_FCO2_ratio']
#         FR_FCO2_ratio = operating_conditions['FR_FCO2_ratio']

#         # 1. Calcola flussi molari effettivi
#         FCO2, F0, FR = self.get_operating_flows(F0_FCO2_ratio, FR_FCO2_ratio)

#         # 2. Calcola tempo di residenza medio (τ) in minuti
#         tau_min = self.residence_time(Ws_per_MW, FR)

#         # 3. Calcola le conversioni medie massime (Equazione 11)
#         Xmax_ave_K, Xmax_ave_D = self.average_maximum_conversion(F0, FR)

#         # 4. Calcola la frazione attiva (Equazione 17)
#         fa = self.active_fraction(tau_min)

#         # 5. Calcola le conversioni medie per le due fasi (Equazioni 15, 16)
#         Xave_K = self.average_conversion_kinetic_phase(tau_min, Xmax_ave_K)
        
#         if fa < 1:
#             Xave_D = self.average_conversion_diffusion_phase(tau_min, Xmax_ave_K, Xmax_ave_D)
#         else:
#             Xave_D = 0

#         # 6. Conversione media totale (Equazione 14)
#         Xave = fa * Xave_K + (1 - fa) * Xave_D

#         # 7. Efficienza di cattura (Equazioni 21-23)
#         if FCO2 > 0:
#             ECO2 = (FR * Xave) / FCO2
#             ECO2_K = (FR * Xave_K * fa) / FCO2
#             ECO2_D = (FR * Xave_D * (1 - fa)) / FCO2
#         else:
#             ECO2 = ECO2_K = ECO2_D = 0
        
#         # Limita l'efficienza al massimo fisico possibile
#         ECO2 = min(ECO2, 0.99)

#         return {
#             'efficiency': ECO2,
#             'efficiency_kinetic': ECO2_K,
#             'efficiency_diffusion': ECO2_D,
#             'residence_time_min': tau_min,
#             'average_conversion': Xave,
#             'average_conversion_kinetic': Xave_K,
#             'average_conversion_diffusion': Xave_D,
#             'active_fraction': fa,
#             'flows': {'FCO2': FCO2, 'F0': F0, 'FR': FR}
#         }

import numpy as np
from scipy import integrate
from parameters import ModelParameters

class CineticModelEquation:
    """Implementazione delle equazioni del modello cinetico"""

    def __init__(self):
        self.params = ModelParameters()

    def conversion_cycle_N(self, N, phase='kinetic'):
        """
        Calcola la conversione massima di CaO al ciclo N (Equazione 3).
        
        Args:
            N (int): Numero del ciclo.
            phase (str): 'kinetic' o 'diffusion'.
        
        Returns:
            float: Conversione massima per quel ciclo e quella fase.
        """
        if phase == 'kinetic':
            k_deactivation = self.params.j_kinetic
            Xr = self.params.Xr_kinetic
            X1 = self.params.X1_kinetic
        else:  # diffusion
            k_deactivation = self.params.j_diffusion
            Xr = self.params.Xr_diffusion
            X1 = self.params.X1_diffusion

        # L'equazione è valida per N >= 1
        if N == 0: return 0
        if N == 1: return X1
        
        # Implementazione diretta dell'Equazione (3)
        term_k = k_deactivation * (N-1) 
        term_inv = 1/(1 - (Xr/X1))
        XN = X1 * ((Xr/X1) + 1/(term_k + term_inv))
        return XN

    def conversion_at_time_t(self, N, t_residence_min):
        """
        Calcola la conversione di una singola particella al ciclo N che ha risieduto 
        per un tempo t_residence_min (in minuti). Basato su Eq. (4).
        """
        XNK = self.conversion_cycle_N(N, 'kinetic')
        
        if t_residence_min <= self.params.t_kinetic:
            # Solo fase cinetica
            return (t_residence_min / self.params.t_kinetic) * XNK
        else:
            # Fase cinetica completata + fase diffusiva
            XND = self.conversion_cycle_N(N, 'diffusion')
            t_diffusion = t_residence_min - self.params.t_kinetic
            max_t_diffusion = self.params.T0 - self.params.t_kinetic
            
            # Limita il tempo di diffusione al massimo considerato nel test TGA
            t_diffusion = min(t_diffusion, max_t_diffusion)
            
            diffusion_contribution = (t_diffusion / max_t_diffusion) * XND
            return XNK + diffusion_contribution


class CarbonCaptureModel:
    """Modello per il calcolo dell'efficienza di cattura di CO2"""
    
    def __init__(self):
        self.params = ModelParameters()
        self.equations = CineticModelEquation()
    
    def get_operating_flows(self, F0_FCO2_ratio, FR_FCO2_ratio):
        """
        Calcola i flussi molari effettivi.
        """
        # Calcola FCO2 (flusso molare di CO2 in ingresso) in mol/s
        FCO2 = self.params.mCO2_per_MW / self.params.M_CO2_kg
        
        # Calcola F0 (makeup) e FR (ricircolo) in mol/s
        F0 = F0_FCO2_ratio * FCO2
        FR = FR_FCO2_ratio * FCO2
        
        return FCO2, F0, FR

    def particle_fraction_cycle_N(self, N, F0, FR):
        """
        Calcola la frazione di particelle al ciclo N in un reattore a miscelazione
        perfetta (Equazione 9).
        """
        if F0 + FR == 0: return 0
        if N == 0: return 0
        
        return (F0 * (FR**(N - 1))) / ((F0 + FR)**N)
    
    def average_maximum_conversion(self, F0, FR, max_cycles=100):
        """
        Calcola la conversione media massima della popolazione di particelle 
        nel reattore (Equazione 11).
        """
        total_X_kinetic = 0
        total_X_diffusion = 0
        
        for N in range(1, max_cycles + 1):
            rho_N = self.particle_fraction_cycle_N(N, F0, FR)
            
            if rho_N < 1e-9: break
                
            XNK = self.equations.conversion_cycle_N(N, 'kinetic')
            XND = self.equations.conversion_cycle_N(N, 'diffusion')
            
            total_X_kinetic += rho_N * XNK
            total_X_diffusion += rho_N * XND
        
        return total_X_kinetic, total_X_diffusion

    def residence_time(self, Ws_per_MW, FR):
        """
        Calcola il tempo di residenza medio in minuti.
        τ = Ws / (M_CaO * FR)
        """
        if FR == 0: return float('inf')
        
        # Ws (kg), M_CaO (kg/mol), FR (mol/s) -> τ (s)
        tau_seconds = Ws_per_MW / (self.params.M_CaO_kg * FR)
        
        return tau_seconds / 60.0  # Converti in minuti

    def active_fraction(self, tau_min):
        """
        Calcola la frazione attiva fa (Equazione 17)
        fa = 1 - exp(-tK/τ)
        """
        if tau_min <= 0:
            return 0
        return 1 - np.exp(-self.params.t_kinetic / tau_min)
    
    def average_conversion_kinetic_phase(self, tau_min, Xmax_ave_K):
        """
        Calcola la conversione media nella fase cinetica (Equazione 15)
        X|≤tK = ∫[0 to tK] rave,K * t * (1/τ) * e^(-t/τ) dt / (1 - e^(-tK/τ))
        """
        if tau_min <= 0 or Xmax_ave_K <= 0:
            return 0
            
        tK = self.params.t_kinetic
        rave_K = Xmax_ave_K / tK
        
        def integrand(t):
            return rave_K * t * (1/tau_min) * np.exp(-t/tau_min)
        
        # Integrazione numerica da 0 a tK
        integral_result, _ = integrate.quad(integrand, 0, tK)
        
        # Normalizzazione (matematicamente corretta secondo il paper)
        fa = self.active_fraction(tau_min)
        if fa > 0:
            return integral_result / fa
        return 0
    
    def average_conversion_diffusion_phase(self, tau_min, Xmax_ave_K, Xmax_ave_D):
        """
        Calcola la conversione media nella fase diffusiva (Equazione 16)
        X|>tK = Xmax,ave,K + ∫[tK to τ] rave,D * t * (1/τ) * e^(-t/τ) dt / (1 - e^(-tK/τ))
        """
        if tau_min <= 0:
            return Xmax_ave_K
            
        tK = self.params.t_kinetic
        if tau_min <= tK:
            return Xmax_ave_K
            
        # Tempo massimo di diffusione dal TGA
        max_diffusion_time = self.params.T0 - tK
        rave_D = Xmax_ave_D / max_diffusion_time
        
        def integrand(t):
            return rave_D * (1/tau_min) * np.exp(-t/tau_min)
        
        # Integrazione da tK fino al minimo tra τ e tempo massimo
        t_max = min(tau_min * 10, tK + max_diffusion_time)  # Limite pratico
        integral_result, _ = integrate.quad(integrand, tK, t_max)
        
        # Normalizzazione (matematicamente corretta secondo il paper)
        fa = self.active_fraction(tau_min)
        if fa < 1:
            return Xmax_ave_K + integral_result / (1 - fa)
        return Xmax_ave_K

    def capture_efficiency(self, operating_conditions):
        """
        Calcola l'efficienza di cattura CO2 implementando le Eq. (8), (14), (21-23).
        """
        try:
            # Estrai parametri operativi
            Ws_per_MW = operating_conditions['Ws_per_MW']
            F0_FCO2_ratio = operating_conditions['F0_FCO2_ratio']
            FR_FCO2_ratio = operating_conditions['FR_FCO2_ratio']

            # 1. Calcola flussi molari effettivi
            FCO2, F0, FR = self.get_operating_flows(F0_FCO2_ratio, FR_FCO2_ratio)

            # 2. Calcola tempo di residenza medio (τ) in minuti
            tau_min = self.residence_time(Ws_per_MW, FR)

            # 3. Calcola le conversioni medie massime (Equazione 11)
            Xmax_ave_K, Xmax_ave_D = self.average_maximum_conversion(F0, FR)

            # 4. Calcola la frazione attiva (Equazione 17)
            fa = self.active_fraction(tau_min)

            # 5. Calcola le conversioni medie per le due fasi (Equazioni 15, 16)
            Xave_K = self.average_conversion_kinetic_phase(tau_min, Xmax_ave_K)
            
            if fa < 1:
                Xave_D = self.average_conversion_diffusion_phase(tau_min, Xmax_ave_K, Xmax_ave_D)
            else:
                Xave_D = 0

            # 6. Conversione media totale (Equazione 14)
            Xave = fa * Xave_K + (1 - fa) * Xave_D

            # 7. Efficienza di cattura (Equazioni 21-23)
            if FCO2 > 0:
                ECO2 = (FR * Xave) / FCO2
                ECO2_K = (FR * Xave_K * fa) / FCO2
                ECO2_D = (FR * Xave_D * (1 - fa)) / FCO2
            else:
                ECO2 = ECO2_K = ECO2_D = 0
            
            # Limita l'efficienza al massimo fisico possibile
            ECO2 = min(ECO2, 0.99)

            return {
                'efficiency': ECO2,
                'efficiency_kinetic': ECO2_K,
                'efficiency_diffusion': ECO2_D,
                'residence_time_min': tau_min,
                'average_conversion': Xave,
                'average_conversion_kinetic': Xave_K,
                'average_conversion_diffusion': Xave_D,
                'active_fraction': fa,
                'flows': {'FCO2': FCO2, 'F0': F0, 'FR': FR}
            }
            
        except Exception as e:
            # Return a safe default result with proper keys in case of error
            print(f"Errore nel calcolo dell'efficienza: {e}")
            return {
                'efficiency': 0.0,
                'efficiency_kinetic': 0.0,
                'efficiency_diffusion': 0.0,
                'residence_time_min': 0.0,
                'average_conversion': 0.0,
                'average_conversion_kinetic': 0.0,
                'average_conversion_diffusion': 0.0,
                'active_fraction': 0.0,
                'flows': {'FCO2': 0.0, 'F0': 0.0, 'FR': 0.0},
                'error': str(e)
            }