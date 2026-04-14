import pandas as pd
import sqlite3
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.lines import Line2D

def build_triple_shock_dataset():
    """Generates the macroeconomic dataset simulating three major global shocks."""
    conn = sqlite3.connect('macro_project.db')
    dates = pd.date_range(start='2019-01-01', end='2026-04-01', freq='MS')
    countries = ['Lebanon', 'Egypt', 'Turkey', 'Germany', 'USA']
    data_list = []
    np.random.seed(42)

    for country in countries:
        # Sensitivity settings (Vulnerability to import shocks)
        if country == 'Lebanon': sens, base_inf = 1.4, 60.0
        elif country == 'Egypt': sens, base_inf = 0.7, 25.0
        elif country == 'Turkey': sens, base_inf = 0.9, 40.0
        elif country == 'Germany': sens, base_inf = 0.2, 4.0
        else: sens, base_inf = 0.1, 2.5
        
        oil, food = 60.0, base_inf
        
        for date in dates:
            # Base Noise
            oil += 0.3 + np.random.uniform(-3, 3)
            food += (sens * 0.3) + np.random.uniform(-0.5, 0.5)
            
            # --- SHOCK 1: COVID-19 (2020) ---
            # Oil crashes, Food rises due to supply chain
            if pd.Timestamp('2020-03-01') <= date <= pd.Timestamp('2020-12-01'):
                oil -= 5.0 
                food += (sens * 5.0)
                
            # --- SHOCK 2: UKRAINE-RUSSIA (2022) ---
            # Both spike aggressively
            if pd.Timestamp('2022-02-01') <= date <= pd.Timestamp('2022-12-01'):
                oil += 8.0
                food += (sens * 15.0)

            # --- SHOCK 3: MIDDLE EAST ESCALATION (2026) ---
            # The current massive spike
            if date >= pd.Timestamp('2026-03-01'):
                oil += 20.0
                food += (sens * 40.0)

            data_list.append([date, country, max(0, food), max(15, oil)])

    df = pd.DataFrame(data_list, columns=['date', 'country', 'food_inflation_pct', 'brent_price'])
    df.to_sql('analytical_master', conn, if_exists='replace', index=False)
    return df, countries

def plot_triple_shock_grid(df, countries):
    """Renders a boardroom-ready 5-panel grid with an isolated legend and safe-spacing."""
    plt.style.use('seaborn-v0_8-whitegrid')
    fig, axes = plt.subplots(nrows=3, ncols=2, figsize=(16, 20))
    axes = axes.flatten()

    for i, country in enumerate(countries):
        ax1 = axes[i]
        subset = df[df['country'] == country].sort_values('date')
        
        # OIL LINE (Primary Y-Axis)
        ax1.plot(subset['date'], subset['brent_price'], color='#1f77b4', linewidth=1.5, alpha=0.7)
        ax1.set_title(f"{country.upper()}", fontsize=15, fontweight='bold', pad=25)
        ax1.set_ylabel("Oil Price ($/bbl)", fontsize=11, fontweight='semibold')
        
        # FOOD LINE (Secondary Y-Axis)
        ax2 = ax1.twinx()
        ax2.plot(subset['date'], subset['food_inflation_pct'], color='#d62728', linewidth=2)
        ax2.set_ylabel("Food Inflation (%)", fontsize=11, fontweight='semibold', rotation=270, labelpad=20)
        
        # --- SHADING THE THREE ERAS ---
        # COVID
        ax1.axvspan(pd.Timestamp('2020-03-01'), pd.Timestamp('2020-12-01'), color='gray', alpha=0.1)
        # Ukraine
        ax1.axvspan(pd.Timestamp('2022-02-01'), pd.Timestamp('2022-12-01'), color='blue', alpha=0.1)
        # 2026 Conflict
        ax1.axvspan(pd.Timestamp('2026-03-01'), pd.Timestamp('2026-04-13'), color='gold', alpha=0.2)
        
    # 1. Delete the empty 6th plot to create a clean space for the legend
    fig.delaxes(axes[5])
    
    # 2. Angle the X-axis dates to prevent horizontal overlap
    for ax in axes[:5]: 
        ax.tick_params(axis='x', rotation=45)

    # 3. Add the Main Title
    fig.suptitle("PROJECT: GLOBAL MACRO SHOCK COMPARISON (2019-2026)\nCOVID-19 vs. Ukraine Conflict vs. 2026 War Shock", 
                 fontsize=22, fontweight='bold', y=0.98)

    # 4. THE FIX: Force tight_layout to reserve the top 8% of the canvas for the title
    plt.tight_layout(rect=[0, 0, 1, 0.92])
    
    # 5. Add vertical and horizontal breathing room between the individual graphs
    plt.subplots_adjust(hspace=0.6, wspace=0.3)

    # 6. Add the Shared Legend in the empty space
    legend_elements = [
        Line2D([0], [0], color='#1f77b4', lw=2, label='Oil Price ($)'),
        Line2D([0], [0], color='#d62728', lw=2, label='Food Inflation (%)'),
        Line2D([0], [0], color='gray', alpha=0.2, lw=8, label='COVID-19 Shock'),
        Line2D([0], [0], color='blue', alpha=0.2, lw=8, label='Ukraine Conflict'),
        Line2D([0], [0], color='gold', alpha=0.3, lw=8, label='2026 War Shock')
    ]
    
    fig.legend(handles=legend_elements, loc='lower right', bbox_to_anchor=(0.90, 0.12), 
               fontsize=13, frameon=True, shadow=True, facecolor='white')

    plt.show()

# --- EXECUTION ---
if __name__ == "__main__":
    final_df, country_list = build_triple_shock_dataset()
    plot_triple_shock_grid(final_df, country_list)
    print("Dataset 'analytical_master' successfully generated and saved to SQLite database.")
