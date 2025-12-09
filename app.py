import streamlit as st
import pandas as pd
import numpy as np

# --- CONFIGURATION PRO ---
st.set_page_config(page_title="TVA &Co - Scanner de Coïncidence", layout="wide", page_icon="🎲")

# --- CSS TYPE "TERMINAL DE TRADING" ---
st.markdown("""
    <style>
    .main { background-color: #0e1117; color: white; }
    .stMetric { background-color: #262730; padding: 10px; border-radius: 5px; border: 1px solid #444; }
    .combo-box { border: 2px solid #00ff00; padding: 15px; border-radius: 10px; background-color: #002b00; }
    .title-text { color: #00ff00; font-family: 'Courier New', monospace; }
    </style>
    """, unsafe_allow_html=True)

# --- 1. LE CERVEAU MATHÉMATIQUE (Extraction des Metrics) ---

def extract_metrics(score_dom, score_ext):
    """
    Décompose un score en toutes ses composantes pour vérifier la théorie du paquet complet.
    """
    total_goals = score_dom + score_ext
    return {
        'Score_Exact': f"{score_dom}-{score_ext}",
        'Total_Buts': total_goals,
        'O15': "OUI" if total_goals > 1.5 else "NON",
        'O25': "OUI" if total_goals > 2.5 else "NON",
        'U25': "OUI" if total_goals < 2.5 else "NON",
        'U35': "OUI" if total_goals < 3.5 else "NON",
        'BTTS': "OUI" if (score_dom > 0 and score_ext > 0) else "NON" # Les deux marquent
    }

# --- 2. DONNÉES HISTORIQUES (Chargement CSV) ---
@st.cache_data
def load_database_2022():
    # On charge le fichier CSV
    try:
        # Essaye de lire avec séparateur virgule, sinon point-virgule (selon ton excel)
        try:
            df = pd.read_csv("data_2022.csv", sep=',')
        except:
            df = pd.read_csv("data_2022.csv", sep=';')

        # Vérification minimale des colonnes
        required_cols = ['Home', 'Away', 'S_Dom', 'S_Ext']
        if not all(col in df.columns for col in required_cols):
            st.error(f"Le fichier CSV doit contenir les colonnes : {required_cols}")
            return pd.DataFrame()
        
        # Calcul des metrics
        metrics_list = df.apply(lambda x: extract_metrics(x['S_Dom'], x['S_Ext']), axis=1)
        df_metrics = pd.DataFrame(metrics_list.tolist())
        return pd.concat([df, df_metrics], axis=1)

    except FileNotFoundError:
        # Si pas de CSV, on charge les données démo pour que l'app ne plante pas
        st.warning("⚠️ Fichier 'data_2022.csv' non trouvé. Chargement des données de DÉMONSTRATION.")
        data = [
            {'Date': '29-09-2022', 'Home': 'FBC Melgar', 'Away': 'Binacional', 'S_Dom': 2, 'S_Ext': 1},
            {'Date': '29-09-2022', 'Home': 'AA', 'Away': '1Z', 'S_Dom': 4, 'S_Ext': 1},
            {'Date': '29-09-2022', 'Home': 'BB', 'Away': '2Y', 'S_Dom': 4, 'S_Ext': 1},
            {'Date': '29-09-2022', 'Home': 'CC', 'Away': '3X', 'S_Dom': 0, 'S_Ext': 1},
        ]
        df = pd.DataFrame(data)
        metrics_list = df.apply(lambda x: extract_metrics(x['S_Dom'], x['S_Ext']), axis=1)
        df_metrics = pd.DataFrame(metrics_list.tolist())
        return pd.concat([df, df_metrics], axis=1)

# --- 3. FIXTURES ACTUELLES (Le Jour J - 15-10-2025) ---
def load_fixtures_2025():
    # Simulation des matchs du jour qui doivent être scannés
    return pd.DataFrame([
        {'Home': 'FBC Melgar', 'Away': 'Alianza Huanuco', 'Heure': '20:00'},
        {'Home': 'AA', 'Away': '8J', 'Heure': '18:00'}, 
        {'Home': 'EE', 'Away': 'TH', 'Heure': '19:30'}, 
        {'Home': 'Man City', 'Away': 'Liverpool', 'Heure': '21:00'},
    ])

# --- 4. ALGORITHME DE CORRESPONDANCE "TVA" ---

def scan_matches(history, today):
    results = []
    if history.empty:
        return pd.DataFrame()

    for idx, match_now in today.iterrows():
        # Recherche correspondance Domicile (Home vs Home)
        # On nettoie les espaces éventuels pour éviter les erreurs bêtes
        match_now_home = str(match_now['Home']).strip()
        
        # On filtre
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

# --- 5. INTERFACE DASHBOARD ---

st.title("⚽ TVA &Co | Algorithme des Coïncidences")
st.markdown("### Principe : Répétition Cyclique & Paradoxe des Scores")

col_control, col_display = st.columns([1, 3])

with col_control:
    st.header("Paramètres")
    # CORRECTION DE L'ERREUR ICI : On force les dates
    d_ref_input = st.date_input("Date Référence (Passé)", pd.to_datetime("2022-09-29"))
    d_target_input = st.date_input("Date Cible (Futur)", pd.to_datetime("2025-10-15"))
    
    # Conversion explicite pour éviter le TypeError
    date_ref = pd.to_datetime(d_ref_input)
    date_target = pd.to_datetime(d_target_input)
    
    delta_days = (date_target - date_ref).days
    st.info(f"Intervalle temporel détecté : {delta_days} jours")
    
    filter_goals = st.slider("Filtrer par nbr de buts min.", 0, 5, 1)

# Chargement données
df_hist = load_database_2022()
df_today = load_fixtures_2025()
predictions = scan_matches(df_hist, df_today)

with col_display:
    if not predictions.empty:
        st.write(f"🧬 **{len(predictions)} Correspondances trouvées** sur la base du principe cyclique.")
        
        for index, row in predictions.iterrows():
            if row['Total_Buts'] >= filter_goals:
                # Affichage style "Ticket de pari"
                with st.container():
                    st.markdown(f"""
                    <div class="combo-box">
                        <h3 style="margin:0">{row['Match']}</h3>
                        <p style="color:#aaa; font-size:12px">Réf: {row['Match_Ref']}</p>
                        <hr style="border-color:#004400">
                        <div style="display:flex; justify-content:space-around; text-align:center;">
                            <div>
                                <div style="font-size:12px; color:#aaa">SCORE EXACT</div>
                                <div style="font-size:24px; font-weight:bold; color:#fff">{row['Score_Ref']}</div>
                            </div>
                            <div>
                                <div style="font-size:12px; color:#aaa">TOTAL BUTS</div>
                                <div style="font-size:24px; font-weight:bold; color:#f1c40f">{row['Total_Buts']}</div>
                            </div>
                             <div>
                                <div style="font-size:12px; color:#aaa">OVER 2.5</div>
                                <div style="font-size:24px; font-weight:bold; color:#3498db">{row['O25']}</div>
                            </div>
                            <div>
                                <div style="font-size:12px; color:#aaa">LES 2 MARQUENT</div>
                                
