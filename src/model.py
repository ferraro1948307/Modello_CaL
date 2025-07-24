
"""
Modello principale per il processo Calcium Looping.
Adattato per funzionare con le equazioni corrette.
"""

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from equations import CarbonCaptureModel, CineticModelEquation
from parameters import ModelParameters

class CalciumLoopingModel:
    """Modello completo del processo Calcium Looping"""
    
    def __init__(self):
        self.equations = CineticModelEquation()
        self.params = ModelParameters()
        self.results = {}
    
    def multicycle_analysis(self, max_cycles=20):
        """
        Analizza il comportamento multi-ciclo del sorbente.
        (Nessuna modifica necessaria qui)
        """
        cycles = np.arange(1, max_cycles + 1)
        
        conversions_kinetic = [self.equations.conversion_cycle_N(N, 'kinetic') for N in cycles]
        conversions_diffusion = [self.equations.conversion_cycle_N(N, 'diffusion') for N in cycles]
        
        # Salva risultati
        self.results['cycles'] = cycles
        self.results['conversion_kinetic'] = np.array(conversions_kinetic)
        self.results['conversion_diffusion'] = np.array(conversions_diffusion)

        print("HERE:")
        print(self.results['conversion_kinetic'])
        
        return self.results
    
    def reaction_rate_analysis(self, max_cycles=20):
        """
        Calcola i tassi di reazione per le fasi cinetiche e diffusive vs numero di cicli.
        Implementa l'analisi mostrata in Figura 5 del paper.
        """
        cycles = np.arange(1, max_cycles + 1)
        
        # Calcola i tassi di reazione per ogni ciclo
        rates_kinetic = []
        rates_diffusion = []
        
        for N in cycles:
            # Tasso di reazione cinetica: rNK = XNK / tK
            XNK = self.equations.conversion_cycle_N(N, 'kinetic')
            rNK = XNK / self.params.t_kinetic if self.params.t_kinetic > 0 else 0
            rates_kinetic.append(rNK)
            
            # Tasso di reazione diffusiva: rND = XND / (T0 - tK)
            XND = self.equations.conversion_cycle_N(N, 'diffusion')
            diffusion_time = self.params.T0 - self.params.t_kinetic
            rND = XND / diffusion_time if diffusion_time > 0 else 0
            rates_diffusion.append(rND)
        
        # Salva risultati
        self.results['reaction_rate_cycles'] = cycles
        self.results['reaction_rate_kinetic'] = np.array(rates_kinetic)
        self.results['reaction_rate_diffusion'] = np.array(rates_diffusion)
        
        return {
            'cycles': cycles,
            'rates_kinetic': np.array(rates_kinetic),
            'rates_diffusion': np.array(rates_diffusion)
        }
    
    def plot_reaction_rates_vs_cycles(self, max_cycles=20, save_fig=False):
        """
        Crea grafico dei tassi di reazione vs numero di cicli (simile a Fig. 5 del paper).
        Y-axis: Tasso di reazione (min^-1)
        X-axis: Numero di cicli (N)
        """
        # Esegui l'analisi se non già fatta
        if 'reaction_rate_cycles' not in self.results:
            self.reaction_rate_analysis(max_cycles)
        
        plt.figure(figsize=(12, 8))
        
        # Plot tasso di reazione cinetica
        plt.plot(self.results['reaction_rate_cycles'], self.results['reaction_rate_kinetic'], 
                 'o-', color='red', linewidth=2.5, markersize=8, 
                 label='Tasso Reazione Cinetica (r$_{NK}$)', markerfacecolor='white', markeredgewidth=2)
        
        # Plot tasso di reazione diffusiva
        plt.plot(self.results['reaction_rate_cycles'], self.results['reaction_rate_diffusion'], 
                 's-', color='blue', linewidth=2.5, markersize=8,
                 label='Tasso Reazione Diffusiva (r$_{ND}$)', markerfacecolor='white', markeredgewidth=2)
        
        plt.xlabel('Numero di Cicli (N)', fontsize=14)
        plt.ylabel('Tasso di Reazione (min$^{-1}$)', fontsize=14)
        plt.title('Tassi di Reazione Cinetica e Diffusiva vs Numero di Cicli', fontsize=16)
        plt.legend(fontsize=12, loc='upper right')
        plt.grid(True, alpha=0.3, linestyle='--')
        plt.xlim(1, max_cycles)
        plt.ylim(bottom=0)
        
        # Aggiungi annotazioni per evidenziare il comportamento
        if len(self.results['reaction_rate_kinetic']) > 1:
            # Trova il punto dove il tasso cinetico si stabilizza
            kinetic_final = self.results['reaction_rate_kinetic'][-1]
            plt.axhline(y=kinetic_final, color='red', linestyle=':', alpha=0.7, 
                       label=f'r$_{{NK}}$ residuale ≈ {kinetic_final:.4f}')
        
        if len(self.results['reaction_rate_diffusion']) > 1:
            # Trova il punto dove il tasso diffusivo si stabilizza
            diffusion_final = self.results['reaction_rate_diffusion'][-1]
            plt.axhline(y=diffusion_final, color='blue', linestyle=':', alpha=0.7,
                       label=f'r$_{{ND}}$ residuale ≈ {diffusion_final:.4f}')
        
        plt.legend(fontsize=11, loc='upper right')
        plt.tight_layout()
        
        if save_fig:
            plt.savefig('data/reaction_rates_vs_cycles.png', dpi=300, bbox_inches='tight')
        
        plt.show()
        
        # Stampa statistiche
        print("\n=== ANALISI TASSI DI REAZIONE ===")
        print(f"Tasso cinetico primo ciclo: {self.results['reaction_rate_kinetic'][0]:.4f} min⁻¹")
        print(f"Tasso cinetico ultimo ciclo: {self.results['reaction_rate_kinetic'][-1]:.4f} min⁻¹")
        print(f"Riduzione tasso cinetico: {(1 - self.results['reaction_rate_kinetic'][-1]/self.results['reaction_rate_kinetic'][0])*100:.1f}%")
        print(f"\nTasso diffusivo primo ciclo: {self.results['reaction_rate_diffusion'][0]:.4f} min⁻¹")
        print(f"Tasso diffusivo ultimo ciclo: {self.results['reaction_rate_diffusion'][-1]:.4f} min⁻¹")
        print(f"Riduzione tasso diffusivo: {(1 - self.results['reaction_rate_diffusion'][-1]/self.results['reaction_rate_diffusion'][0])*100:.1f}%")
    
    def plot_multicycle_behavior(self, save_fig=False):
        """
        Crea grafico conversione vs numero di cicli (Fig. 3 del paper).
        (Nessuna modifica necessaria qui)
        """
        if 'cycles' not in self.results:
            self.multicycle_analysis()
        
        plt.figure(figsize=(10, 6))
        
        plt.plot(self.results['cycles'], self.results['conversion_kinetic'], 
                 'o-', color='red', linewidth=2, markersize=6, 
                 label='Fase Cinetica (X$_{NK}$)')
        
        plt.plot(self.results['cycles'], self.results['conversion_diffusion'], 
                 's-', color='blue', linewidth=2, markersize=6,
                 label='Fase Diffusiva (X$_{ND}$)')

        plt.plot(self.results['cycles'], self.results['conversion_kinetic'] + self.results['conversion_diffusion'],
                 '^-', color='black', linewidth=2, markersize=6, linestyle='--',
                 label='Conversione Totale Massima (X$_{N,max}$)')
        
        plt.xlabel('Numero di Cicli (N)', fontsize=12)
        plt.ylabel('Conversione CaO', fontsize=12)
        plt.title('Conversione Massima CaO vs Numero di Cicli', fontsize=14)
        plt.legend(fontsize=11)
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        
        if save_fig:
            plt.savefig('data/conversion_vs_cycles.png', dpi=300, bbox_inches='tight')
        
        plt.show()

    def conversion_vs_time_for_cycle_N(self, N, max_time_min=30, time_points=100):
        """
        Mostra l'evoluzione della conversione nel tempo per un ciclo specifico N.
        Utile per visualizzare le fasi cinetiche e diffusive.
        """
        time_array = np.linspace(0, max_time_min, time_points)
        conversions = [self.equations.conversion_at_time_t(N, t) for t in time_array]
        
        plt.figure(figsize=(10, 6))
        plt.plot(time_array, conversions, 'b-', linewidth=2.5, label=f'Ciclo N={N}')
        
        # Aggiungi linea verticale per il tempo di transizione cinetica-diffusiva
        plt.axvline(x=self.params.t_kinetic, color='red', linestyle='--', alpha=0.7,
                   label=f'Fine fase cinetica (t = {self.params.t_kinetic} min)')
        
        # Aggiungi linee orizzontali per le conversioni massime
        XNK = self.equations.conversion_cycle_N(N, 'kinetic')
        XND = self.equations.conversion_cycle_N(N, 'diffusion')
        plt.axhline(y=XNK, color='orange', linestyle=':', alpha=0.7,
                   label=f'X$_{{NK}}$ = {XNK:.3f}')
        plt.axhline(y=XNK+XND, color='green', linestyle=':', alpha=0.7,
                   label=f'X$_{{NK}}$ + X$_{{ND}}$ = {XNK+XND:.3f}')
        
        plt.xlabel('Tempo di Residenza (min)', fontsize=12)
        plt.ylabel('Conversione CaO', fontsize=12)
        plt.title(f'Evoluzione della Conversione nel Tempo - Ciclo {N}', fontsize=14)
        plt.legend(fontsize=11)
        plt.grid(True, alpha=0.3)
        plt.xlim(0, max_time_min)
        plt.ylim(0, max(conversions)*1.1)
        plt.tight_layout()
        plt.show()

    def plot_multiple_cycles_conversion_vs_time(self, cycle_list, max_time_min=30, time_points=100, save_fig=False):
        """
        Mostra l'evoluzione della conversione nel tempo per più cicli sullo stesso grafico.
        
        Args:
            cycle_list (list): Lista dei cicli da plottare (es. [2, 10, 20])
            max_time_min (float): Tempo massimo in minuti
            time_points (int): Numero di punti per la discretizzazione temporale
            save_fig (bool): Se salvare il grafico
        """
        plt.figure(figsize=(12, 8))
        
        colors = ['blue', 'red', 'green', 'orange', 'purple', 'brown']
        time_array = np.linspace(0, max_time_min, time_points)
        
        max_conversion = 0
        
        # Plot delle curve per ogni ciclo
        for i, N in enumerate(cycle_list):
            conversions = [self.equations.conversion_at_time_t(N, t) for t in time_array]
            color = colors[i % len(colors)]
            
            plt.plot(time_array, conversions, '-', color=color, linewidth=3, 
                    label=f'Ciclo N={N}', markersize=6)
            
            max_conversion = max(max_conversion, max(conversions))
        
        # Aggiungi linea verticale per il tempo di transizione cinetica-diffusiva
        plt.axvline(x=self.params.t_kinetic, color='black', linestyle='--', alpha=0.8, linewidth=2,
                   label=f'Fine fase cinetica (t = {self.params.t_kinetic} min)')
        
        # Aggiungi regioni per evidenziare le fasi
        plt.axvspan(0, self.params.t_kinetic, alpha=0.1, color='red', label='Fase Cinetica')
        plt.axvspan(self.params.t_kinetic, max_time_min, alpha=0.1, color='blue', label='Fase Diffusiva')
        
        plt.xlabel('Tempo di Residenza (min)', fontsize=14)
        plt.ylabel('Conversione CaO', fontsize=14)
        plt.title('Evoluzione della Conversione nel Tempo per Diversi Cicli', fontsize=16)
        
        # Legenda ordinata per importanza
        handles, labels = plt.gca().get_legend_handles_labels()
        # Riordina per mettere prima i cicli, poi le fasi
        cycle_handles = [h for h, l in zip(handles, labels) if 'Ciclo N=' in l]
        cycle_labels = [l for l in labels if 'Ciclo N=' in l]
        other_handles = [h for h, l in zip(handles, labels) if 'Ciclo N=' not in l]
        other_labels = [l for l in labels if 'Ciclo N=' not in l]
        
        plt.legend(cycle_handles + other_handles, cycle_labels + other_labels, 
                  fontsize=12, loc='lower right')
        
        plt.grid(True, alpha=0.3, linestyle='-', linewidth=0.5)
        plt.xlim(0, max_time_min)
        plt.ylim(0, max_conversion * 1.1)
        plt.tight_layout()
        
        if save_fig:
            plt.savefig('data/conversion_vs_time_multiple_cycles.png', dpi=300, bbox_inches='tight')
        
        plt.show()
        
        # Print summary statistics for each cycle
        print("\n   Summary delle curve mostrate:")
        print(f"   {'Ciclo':<8} {'X_NK':<10} {'X_ND':<10} {'X_totale':<12} {'X@t_K':<12}")
        print("   " + "-" * 55)
        
        for N in cycle_list:
            XNK = self.equations.conversion_cycle_N(N, 'kinetic')
            XND = self.equations.conversion_cycle_N(N, 'diffusion')
            X_total = XNK + XND
            X_at_tK = self.equations.conversion_at_time_t(N, self.params.t_kinetic)
            
            print(f"   N={N:<6} {XNK:<10.4f} {XND:<10.4f} {X_total:<12.4f} {X_at_tK:<12.4f}")

class AdvancedAnalysis:
    """Analisi avanzate del sistema di cattura"""
    
    def __init__(self):
        self.capture_model = CarbonCaptureModel()
        self.params = ModelParameters()
    
    def parametric_study(self, Ws_range, FR_FCO2_ratio, F0_FCO2_ratio):
        """
        MODIFICATO: Studio parametrico che utilizza la nuova funzione di efficienza.
        """
        results = {
            'Ws_per_MW': [],
            'residence_time_min': [],
            'efficiency': [],
            'average_conversion': []
        }
        
        for Ws in Ws_range:
            conditions = {
                'Ws_per_MW': Ws,
                'F0_FCO2_ratio': F0_FCO2_ratio,
                'FR_FCO2_ratio': FR_FCO2_ratio
            }
            
            result = self.capture_model.capture_efficiency(conditions)
            
            results['Ws_per_MW'].append(Ws)
            results['residence_time_min'].append(result['residence_time_min'])
            results['efficiency'].append(result['efficiency'])
            results['average_conversion'].append(result['average_conversion'])
        
        return results
    
    def plot_efficiency_vs_inventory(self, Ws_range, FR_values, F0_FCO2_ratio):
        """
        MODIFICATO: Grafico efficienza vs inventario solidi (come Fig. 7 e 8).
        Utilizza i nuovi risultati.
        """
        plt.figure(figsize=(12, 8))
        colors = ['red', 'blue', 'green']
        
        for i, FR_FCO2_ratio in enumerate(FR_values):
            # USA LA NUOVA FUNZIONE DI STUDIO PARAMETRICO
            results = self.parametric_study(Ws_range, FR_FCO2_ratio, F0_FCO2_ratio)
            
            plt.plot(results['Ws_per_MW'], results['efficiency'], 
                     'o-', color=colors[i % len(colors)], linewidth=2.5, markersize=7,
                     label=f'FR/FCO2 = {FR_FCO2_ratio}')
        
        plt.xlabel('Inventario Solidi Ws (kg/MW)', fontsize=12)
        plt.ylabel('Efficienza di Cattura CO2', fontsize=12)
        plt.title(f'Efficienza di Cattura vs Inventario Solidi\n(F0/FCO2 = {F0_FCO2_ratio})', fontsize=14)
        plt.legend()
        plt.grid(True, which='both', linestyle='--', linewidth=0.5)
        plt.ylim(0, 1)
        plt.xlim(left=0)
        plt.tight_layout()
        plt.show()

    def plot_efficiency_vs_residence_time(self, Ws_range, FR_FCO2_ratio, F0_FCO2_ratio):
        """
        MODIFICATO: Grafico efficienza vs tempo di residenza (come Fig. 9).
        Ora mostra solo l'efficienza totale, che è il risultato robusto del modello.
        """
        results = self.parametric_study(Ws_range, FR_FCO2_ratio, F0_FCO2_ratio)
        
        fig, ax1 = plt.subplots(figsize=(12, 7))
        
        color = 'tab:blue'
        ax1.set_xlabel('Tempo di Residenza τ (min)', fontsize=12)
        ax1.set_ylabel('Efficienza di Cattura CO2', fontsize=12, color=color)
        ax1.plot(results['residence_time_min'], results['efficiency'], 'o-', color=color, linewidth=2.5)
        ax1.tick_params(axis='y', labelcolor=color)
        ax1.set_ylim(0, 1)
        ax1.grid(True, linestyle='--', linewidth=0.5)

        # Aggiungo un secondo asse y per mostrare la conversione media
        ax2 = ax1.twinx()
        color = 'tab:red'
        ax2.set_ylabel('Conversione Media Particelle (X_ave)', fontsize=12, color=color)
        ax2.plot(results['residence_time_min'], results['average_conversion'], 's--', color=color, linewidth=2)
        ax2.tick_params(axis='y', labelcolor=color)
        ax2.set_ylim(bottom=0)

        plt.title(f'Efficienza vs Tempo di Residenza\n(FR/FCO2={FR_FCO2_ratio}, F0/FCO2={F0_FCO2_ratio})', fontsize=14)
        fig.tight_layout()
        plt.show()

    def optimization_study(self, Ws_range, FR_range, F0_FCO2_ratio):
        """
        MODIFICATO: Trova condizioni operative ottimali usando i nuovi risultati.
        """
        best_efficiency = 0
        best_conditions = None
        
        results_matrix = np.zeros((len(Ws_range), len(FR_range)))
        
        for i, Ws in enumerate(Ws_range):
            for j, FR in enumerate(FR_range):
                conditions = {
                    'Ws_per_MW': Ws,
                    'F0_FCO2_ratio': F0_FCO2_ratio,
                    'FR_FCO2_ratio': FR
                }
                
                result = self.capture_model.capture_efficiency(conditions)
                efficiency = result['efficiency']
                results_matrix[i, j] = efficiency
                
                if efficiency > best_efficiency:
                    best_efficiency = efficiency
                    best_conditions = conditions.copy()
                    best_conditions['results'] = result # Salva tutti i risultati del punto ottimale
        
        # Plot heatmap
        plt.figure(figsize=(10, 8))
        im = plt.imshow(results_matrix, cmap='viridis', aspect='auto', origin='lower',
                        extent=[FR_range.min(), FR_range.max(), Ws_range.min(), Ws_range.max()])
        
        plt.colorbar(im, label='Efficienza di Cattura CO2')
        plt.xlabel('Rapporto Ricircolo (FR/FCO2)')
        plt.ylabel('Inventario Solidi Ws (kg/MW)')
        plt.title('Mappa di Ottimizzazione Efficienza di Cattura')
        
        # Aggiungi punto di ottimo
        if best_conditions:
            plt.plot(best_conditions['FR_FCO2_ratio'], best_conditions['Ws_per_MW'], 'r*', 
                     markersize=15, label=f'Ottimo ({best_efficiency:.3f})')
            plt.legend()
            
        plt.tight_layout()
        plt.show()
        
        return best_conditions, results_matrix