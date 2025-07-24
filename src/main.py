
"""
File principale per eseguire e testare il modello Calcium Looping.
Aggiornato per funzionare con la logica di calcolo corretta e includere l'analisi dei tassi di reazione.
"""

from model import AdvancedAnalysis, CalciumLoopingModel
import matplotlib.pyplot as plt
import numpy as np
import os

def main():
    """Funzione principale per eseguire l'analisi completa del modello"""
    
    print("=== MODELLO CALCIUM LOOPING - ANALISI BASATA SU ORTIZ ET AL. (2015) ===")
    
    # Crea cartella per i grafici se non esiste
    if not os.path.exists('data'):
        os.makedirs('data')
    
    # Inizializza i modelli
    model = CalciumLoopingModel()
    advanced_analysis = AdvancedAnalysis()
    
    # ========== 1. ANALISI COMPORTAMENTO SORBENTE ==========
    print("\n[FASE 1] Analisi del comportamento multi-ciclo del sorbente...")
    model.multicycle_analysis(max_cycles=25)
    model.plot_multicycle_behavior(save_fig=True)
    print("--> Grafico 'conversion_vs_cycles.png' salvato in /data.")
    
    # ========== 1.1 NUOVA ANALISI: TASSI DI REAZIONE VS CICLI ==========
    print("\n[FASE 1.1] Analisi dei tassi di reazione vs numero di cicli (simile a Fig. 5)...")
    model.plot_reaction_rates_vs_cycles(max_cycles=25, save_fig=True)
    print("--> Grafico 'reaction_rates_vs_cycles.png' salvato in /data.")
    
    # ========== 1.2 CONVERSIONE VS TEMPO PER CICLI MULTIPLI ==========
    print("\n[FASE 1.2] Conversione nel tempo per cicli N=2, 10, 20 (confronto)...")
    model.plot_multiple_cycles_conversion_vs_time([2, 10, 20], max_time_min=20, save_fig=True)
    print("--> Grafico 'conversion_vs_time_multiple_cycles.png' salvato in /data.")
    
    # ========== 2. TEST DI EFFICIENZA SU SINGOLO PUNTO ==========
    print("\n[FASE 2] Test di efficienza di cattura su un singolo punto operativo...")
    conditions = {
        'Ws_per_MW': 200,      # kg/MW
        'F0_FCO2_ratio': 0.01, # Adimensionale
        'FR_FCO2_ratio': 5     # Adimensionale
    }
    
    # MODIFICA: Chiamata e gestione dei nuovi risultati
    result = advanced_analysis.capture_model.capture_efficiency(conditions)
    
    print(f"   Condizioni operative:")
    print(f"     - Inventario solidi (Ws): {conditions['Ws_per_MW']} kg/MW")
    print(f"     - Rapporto makeup (F0/FCO2): {conditions['F0_FCO2_ratio']}")
    print(f"     - Rapporto ricircolo (FR/FCO2): {conditions['FR_FCO2_ratio']}")
    print(f"   Risultati Calcolati:")
    print(f"     - Efficienza di cattura: {result['efficiency']:.3f}")
    print(f"     - Efficienza fase cinetica: {result['efficiency_kinetic']:.3f}")
    print(f"     - Efficienza fase diffusiva: {result['efficiency_diffusion']:.3f}")
    print(f"     - Tempo di residenza (τ): {result['residence_time_min']:.2f} min")
    print(f"     - Conversione media particelle (X_ave): {result['average_conversion']:.4f}")
    print(f"     - Frazione attiva (fa): {result['active_fraction']:.4f}")
    
    # ========== 3. STUDIO PARAMETRICO: EFFICIENZA VS INVENTARIO ==========
    print("\n[FASE 3] Studio parametrico: Efficienza vs Inventario Solidi (simula Fig. 7)...")
    Ws_range = np.linspace(1, 400, 25)
    FR_values = [5, 10, 20]
    F0_FCO2_ratio = 0.01
    advanced_analysis.plot_efficiency_vs_inventory(Ws_range, FR_values, F0_FCO2_ratio)
    
    # ========== 4. STUDIO PARAMETRICO: EFFICIENZA VS TEMPO DI RESIDENZA ==========
    print("\n[FASE 4] Analisi: Efficienza vs Tempo di Residenza (simula Fig. 9)...")
    FR_FCO2_ratio_fixed = 5
    F0_FCO2_ratio_fixed = 0.01
    advanced_analysis.plot_efficiency_vs_residence_time(Ws_range, FR_FCO2_ratio_fixed, F0_FCO2_ratio_fixed)
    
    # ========== 5. OTTIMIZZAZIONE PARAMETRI OPERATIVI ==========
    print("\n[FASE 5] Ottimizzazione parametri operativi tramite heatmap...")
    Ws_opt_range = np.linspace(100, 500, 15)
    FR_opt_range = np.linspace(3, 15, 15)
    
    # MODIFICA: Gestione dei nuovi risultati di ottimizzazione
    best_conditions, _ = advanced_analysis.optimization_study(
        Ws_opt_range, FR_opt_range, 0.01
    )
    
    if best_conditions:
        print("\n   Condizioni ottimali trovate:")
        print(f"     - Ws ottimale: {best_conditions['Ws_per_MW']:.0f} kg/MW")
        print(f"     - FR/FCO2 ottimale: {best_conditions['FR_FCO2_ratio']:.2f}")
        print(f"     - F0/FCO2: {best_conditions['F0_FCO2_ratio']}")
        print(f"     - Efficienza massima: {best_conditions['results']['efficiency']:.3f}")
        print(f"     - Tempo residenza ottimale: {best_conditions['results']['residence_time_min']:.2f} min")
        print(f"     - Frazione attiva ottimale: {best_conditions['results']['active_fraction']:.4f}")
    
    # ========== 6. SUMMARY FINALE E CONFRONTO SCENARI ==========
    print("\n[FASE 6] Summary finale e confronto scenari...")
    
    scenarios = [
        {'name': 'Basso Inv.', 'Ws': 150, 'FR': 7, 'F0': 0.05},
        {'name': 'Alto Inv.', 'Ws': 400, 'FR': 10, 'F0': 0.01},
    ]
    if best_conditions:
         scenarios.append({
             'name': 'Ottimale', 
             'Ws': best_conditions['Ws_per_MW'], 
             'FR': best_conditions['FR_FCO2_ratio'], 
             'F0': 0.01
         })

    print(f"\n{'Scenario':<12} {'Ws':<8} {'FR/F_CO2':<10} {'F0/F_CO2':<10} {'Efficienza':<12} {'τ (min)':<8} {'fa':<8}")
    print("-" * 75)
    
    for scenario in scenarios:
        conditions = {
            'Ws_per_MW': scenario['Ws'],
            'F0_FCO2_ratio': scenario['F0'],
            'FR_FCO2_ratio': scenario['FR']
        }
        
        # MODIFICA: Calcolo e stampa con le nuove chiavi
        result = advanced_analysis.capture_model.capture_efficiency(conditions)
        
        print(f"{scenario['name']:<12} {scenario['Ws']:<8.0f} {scenario['FR']:<10.2f} {scenario['F0']:<10.3f} "
              f"{result['efficiency']:<12.3f} {result['residence_time_min']:<8.2f} {result['active_fraction']:<8.4f}")
    
    # ========== 7. ANALISI DETTAGLIATA DELL'EFFICIENZA PER FASI ==========
    print("\n[FASE 7] Analisi dettagliata del contributo delle fasi cinetica e diffusiva...")
    
    # Analizza come varia il contributo delle due fasi al variare del tempo di residenza
    test_conditions = [
        {'Ws': 100, 'FR': 20, 'F0': 0.01, 'name': 'Basso τ'},
        {'Ws': 200, 'FR': 10, 'F0': 0.01, 'name': 'Medio τ'},
        {'Ws': 400, 'FR': 5, 'F0': 0.01, 'name': 'Alto τ'}
    ]
    
    print(f"\n{'Condizione':<12} {'τ (min)':<10} {'E_totale':<12} {'E_cinetica':<12} {'E_diffusiva':<12} {'% Diffusiva':<12}")
    print("-" * 85)
    
    for test in test_conditions:
        conditions = {
            'Ws_per_MW': test['Ws'],
            'F0_FCO2_ratio': test['F0'],
            'FR_FCO2_ratio': test['FR']
        }
        
        result = advanced_analysis.capture_model.capture_efficiency(conditions)
        
        # Calcola la percentuale di contributo della fase diffusiva
        total_efficiency = result['efficiency']
        diffusion_efficiency = result['efficiency_diffusion']
        diffusion_percentage = (diffusion_efficiency / total_efficiency * 100) if total_efficiency > 0 else 0
        
        print(f"{test['name']:<12} {result['residence_time_min']:<10.2f} {result['efficiency']:<12.3f} "
              f"{result['efficiency_kinetic']:<12.3f} {result['efficiency_diffusion']:<12.3f} {diffusion_percentage:<12.1f}")
    
    print("\n=== CONCLUSIONI CHIAVE ===")
    print("1. I tassi di reazione diminuiscono con il numero di cicli a causa della disattivazione del sorbente")
    print("2. Tempi di residenza più lunghi favoriscono la fase diffusiva, aumentando l'efficienza totale")
    print("3. La fase diffusiva diventa sempre più importante per tempi di residenza elevati")
    print("4. L'ottimizzazione deve bilanciare inventario solidi, flussi di ricircolo e efficienza desiderata")
    
    print("\n=== ANALISI COMPLETATA ===")
    print("I grafici sono stati generati e mostrati a schermo.")
    print("File salvati in /data:")
    print("  - conversion_vs_cycles.png")
    print("  - reaction_rates_vs_cycles.png")

def run_quick_test():
    """Funzione per test rapidi durante lo sviluppo"""
    print("=== TEST RAPIDO ===")
    
    model = CalciumLoopingModel()
    
    # Test solo della nuova funzionalità
    print("Testando plot dei tassi di reazione...")
    model.plot_reaction_rates_vs_cycles(max_cycles=10)
    
    print("Test completato!")

if __name__ == "__main__":
    # Decommentare la linea desiderata:
    main()  # Analisi completa
    # run_quick_test()  # Solo test rapido