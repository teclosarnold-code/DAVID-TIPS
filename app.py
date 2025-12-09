import streamlit as st
import pandas as pd
import numpy as np

# --- CONFIGURATION PRO ---
st.set_page_config(page_title="TVA &Co - Scanner", layout="wide", page_icon="⚽")

# --- STYLE CSS SIMPLIFIÉ ---
st.markdown("""
    <style>
    .stMetric { background-color: #f0f2f6; padding: 10px; border-radius: 5px; }
    </style>
    """, unsafe_allow_html=True)

# --- 1. LE CERVEAU MATHÉMATIQUE ---
def extract_metrics(score_dom, score_ext):
    total_goals = score_dom + score_ext
    return {
        'Score_Exact': f"{score_dom}-{score_ext}",
        'Total_Buts': total_goals,
        'O15': "OUI" if total_goals > 1.5 else "NON",
        'O25': "OUI" if total_goals > 2.5 else "NON",
        'BTTS': "OUI" if (score_dom > 0 and score_ext > 0) else "NON"
    }

# --- 2. DONNÉES HISTORIQUES ---
@st.cache_data
def load_database_2022():
    try:
        # Essaye de lire le fichier, sinon charge la démo
        try:
            df = pd.read_csv("data_2022.csv", sep=',')
        except:
            df = pd.read_csv("data_2022.csv", sep=';')
            
        required_cols = ['Home', 'Away', 'S_Dom', 'S_Ext']
        if not all(col in df.columns for col in required_cols):
            return pd.DataFrame()
            
        metrics_list = df.apply(lambda x: extract_metrics(x['S_Dom'], x['S_Ext']), axis=1)
        df_metrics = pd.DataFrame(metrics_list.tolist())
        return pd.concat([df, df_metrics], axis=1)
    except:
        # DONNÉES DE SECOURS (DÉMO)
        data = [
            {'Date': '29-09-2022', 'Home': 'FBC Melgar', 'Away': 'Binacional', 'S_Dom': 2, 'S_Ext': 1},
            {'Date': '29-09-2022', 'Home': 'AA', 'Away': '1Z', 'S_Dom': 4, 'S_Ext': 1},
            {'Date': '29-09-2022', 'Home': 'BB', 'Away': '2Y', 'S_Dom': 4, 'S_Ext': 1},
        ]
        df = pd.DataFrame(data)
        metrics_list = df.apply(lambda x: extract_metrics(x['S_Dom'], x['S_Ext']), axis=1)
        df_metrics = pd.DataFrame(metrics_list.tolist())
        return pd.concat([df, df_metrics], axis=1)

# --- 3. FIXTURES ACTUELLES ---
def load_fixtures_2025():
    return pd.DataFrame([
        {'Home': 'FBC Melgar', 'Away': 'Alianza Huanuco', 'Heure': '20:00'},
        {'Home': 'AA', 'Away': '8J', 'Heure': '18:00'}, 
        {'Home': 'EE', 'Away': 'TH', 'Heure': '19:30'}, 
        {'Home': 'Man City', 'Away': 'Liverpool', 'Heure': '21:00'},
    ])

# --- 4. ALGORITHME ---
def scan_matches(history, today):
    results = []
    if history.empty: return pd.DataFrame()

    for idx, match_now in today.iterrows():
        match_now_home = str(match_now['Home']).strip()
        match_found = history[history['Home'].astype(str).str.strip() == match_now_home]
        
        if not match_found.empty:
            historical_data = match_found.iloc[0]
            results.append({
                'Match': f"{match_now['Home']} vs {match_now['Away']}",
                'Match_Ref': f"{historical_data['Home']} vs {historical_data['Away']}",
                'Score_Ref': historical_data['Score_Exact'],
                'Total_Buts': historical_data['Total_Buts'],
                'O25': historical_data['O25'],
                'BTTS': historical_data['BTTS'],
            })
    return pd.DataFrame(results)

# --- 5. INTERFACE DASHBOARD (CORRIGÉE) ---

st.title("⚽ TVA &Co | Scanner")
st.markdown("### Algorithme de Coïncidence")

# Paramètres
with st.expander("⚙️ Réglages", expanded=True):
    col_param1, col_param2 = st.columns(2)
    d_ref_input = col_param1.date_input("Date Passé", pd.to_datetime("2022-09-29"))
    d_target_input = col_param2.date_input("Date Futur", pd.to_datetime("2025-10-15"))
    
    date_ref = pd.to_datetime(d_ref_input)
    date_target = pd.to_datetime(d_target_input)
    st.caption(f"Intervalle : {(date_target - date_ref).days} jours")

# Chargement
df_hist = load_database_2022()
df_today = load_fixtures_2025()
predictions = scan_matches(df_hist, df_today)

# Affichage des Résultats
st.divider()

if not predictions.empty:
    st.success(f"🧬 {len(predictions)} Correspondances trouvées")
    
    for index, row in predictions.iterrows():
        # Utilisation de st.container avec bordure (plus stable que le HTML pur)
        with st.container(border=True):
            col_titre, col_ref = st.columns([2, 1])
            col_titre.subheader(f"⚽ {row['Match']}")
            col_ref.text(f"Réf: {row['Match_Ref']}")
            
            # Les stats en colonnes natives (Pas de risque de syntaxe)
            c1, c2, c3, c4 = st.columns(4)
            c1.metric(label="SCORE EXACT", value=row['Score_Ref'])
            c2.metric(label="TOTAL BUTS", value=row['Total_Buts'])
            c3.metric(label="OVER 2.5", value=row['O25'])
            c4.metric(label="LES 2 MARQUENT", value=row['BTTS'])
            
            if row['O25'] == "OUI" and row['BTTS'] == "OUI":
                st.info("💡 CONSEIL: Le Combo (Buts + Score) est statistiquement aligné.")

else:
    st.warning("Aucune correspondance exacte trouvée pour ces équipes.")
    st.info("Le système utilise les données de démonstration si le fichier CSV est absent.")
