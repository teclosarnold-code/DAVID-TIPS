import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# --- CONFIGURATION ---
st.set_page_config(page_title="TVA &Co | Chronologie", layout="wide", page_icon="📅")

# --- STYLE ---
st.markdown("""
    <style>
    .stMetric { background-color: #f8f9fa; border: 1px solid #dee2e6; }
    .css-1544g2n { padding-top: 1rem; }
    h3 { color: #0f5132; }
    </style>
    """, unsafe_allow_html=True)

# --- 1. MOTEUR MATHÉMATIQUE ---
def extract_metrics(score_dom, score_ext):
    total_goals = score_dom + score_ext
    return {
        'Score_Exact': f"{score_dom}-{score_ext}",
        'Total_Buts': total_goals,
        'O15': "OUI" if total_goals > 1.5 else "NON",
        'O25': "OUI" if total_goals > 2.5 else "NON",
        'BTTS': "OUI" if (score_dom > 0 and score_ext > 0) else "NON"
    }

# --- 2. CHARGEMENT BASE 2022 ---
@st.cache_data
def load_database_2022():
    try:
        try: df = pd.read_csv("data_2022.csv", sep=',')
        except: df = pd.read_csv("data_2022.csv", sep=';')
            
        required_cols = ['Home', 'Away', 'S_Dom', 'S_Ext']
        if not all(col in df.columns for col in required_cols): return pd.DataFrame()
            
        metrics_list = df.apply(lambda x: extract_metrics(x['S_Dom'], x['S_Ext']), axis=1)
        df_metrics = pd.DataFrame(metrics_list.tolist())
        return pd.concat([df, df_metrics], axis=1)
    except:
        # DÉMO
        data = [
            {'Date': '29-09-2022', 'Home': 'FBC Melgar', 'Away': 'Binacional', 'S_Dom': 2, 'S_Ext': 1},
            {'Date': '29-09-2022', 'Home': 'AA', 'Away': '1Z', 'S_Dom': 4, 'S_Ext': 1},
            {'Date': '29-09-2022', 'Home': 'Manchester City', 'Away': 'United', 'S_Dom': 6, 'S_Ext': 3},
        ]
        df = pd.DataFrame(data)
        metrics_list = df.apply(lambda x: extract_metrics(x['S_Dom'], x['S_Ext']), axis=1)
        df_metrics = pd.DataFrame(metrics_list.tolist())
        return pd.concat([df, df_metrics], axis=1)

# --- 3. ALGORITHME DE MATCHING ---
def scan_matches(history, match_input):
    results = []
    if history.empty or match_input.empty: return pd.DataFrame()

    for idx, row in match_input.iterrows():
        if pd.isna(row['Home']): continue
        # Nettoyage
        team_home = str(row['Home']).strip()
        
        # Recherche correspondance
        found = history[history['Home'].astype(str).str.strip() == team_home]
        
        if not found.empty:
            hist_data = found.iloc[0]
            results.append({
                'Match': f"{row['Home']} vs {row['Away']}",
                'Match_Ref': f"{hist_data['Home']} vs {hist_data['Away']}",
                'Score_Ref': hist_data['Score_Exact'],
                'Total_Buts': hist_data['Total_Buts'],
                'O25': hist_data['O25'],
                'BTTS': hist_data['BTTS']
            })
    return pd.DataFrame(results)

# --- 4. FONCTION D'AFFICHAGE PAR ONGLET ---
def render_tab_content(label, date_offset, df_history):
    target_date = datetime.now() + timedelta(days=date_offset)
    formatted_date = target_date.strftime("%d-%m-%Y")
    
    st.markdown(f"### 📅 Programme du {formatted_date} ({label})")
    
    col_input, col_res = st.columns([1, 2])
    
    with col_input:
        st.info("✍️ Saisissez les matchs ci-dessous :")
        # Structure vide par défaut
        default_data = [{"Home": "", "Away": ""}]
        if label == "Aujourd'hui":
            default_data = [{"Home": "FBC Melgar", "Away": "Alianza"}] # Exemple
            
        input_df = st.data_editor(
            pd.DataFrame(default_data),
            num_rows="dynamic",
            column_config={
                "Home": st.column_config.TextColumn("Domicile"),
                "Away": st.column_config.TextColumn("Extérieur")
            },
            key=f"editor_{label}" # Clé unique indispensable
        )

    with col_res:
        # Lancer l'analyse
        preds = scan_matches(df_history, input_df)
        
        if not preds.empty:
            st.success(f"🔍 {len(preds)} Correspondances trouvées")
            for i, row in preds.iterrows():
                with st.container(border=True):
                    st.markdown(f"**⚽ {row['Match']}**")
                    st.caption(f"Ref 2022: {row['Match_Ref']}")
                    
                    c1, c2, c3, c4 = st.columns(4)
                    c1.metric("Score", row['Score_Ref'])
                    c2.metric("Buts", row['Total_Buts'])
                    c3.metric("Over 2.5", row['O25'])
                    c4.metric("BTTS", row['BTTS'])
        else:
            st.caption("En attente de saisie ou pas de correspondance.")

# ==========================================
# --- INTERFACE PRINCIPALE ---
# ==========================================

st.title("⚽ TVA &Co | Interface Temporelle")

# Chargement Base
df_base = load_database_2022()

# CRÉATION DES ONGLETS
tab_hier, tab_auj, tab_demain = st.tabs([
    "⏮️ HIER (Résultats)", 
    "🚨 AUJOURD'HUI (Live)", 
    "⏭️ DEMAIN (Pronos)"
])

# CONTENU DES ONGLETS
with tab_hier:
    render_tab_content("Hier", -1, df_base)

with tab_auj:
    render_tab_content("Aujourd'hui", 0, df_base)
    
with tab_demain:
    render_tab_content("Demain", 1, df_base)

# Pied de page
st.divider()
st.caption("Système de scan basé sur la récurrence cyclique S-1 (2022)")
