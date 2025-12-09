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

# --- 2. DONNÉES HISTORIQUES (La source du "Paradoxe") ---
# Simulation basée sur ton exemple du 29-09-2022
# Remplacer toute la fonction load_database_2022 par ceci :
@st.cache_data
def load_database_2022():
    # On charge le fichier CSV qu'on va mettre dans le projet
    # Assure-toi que ton CSV a les colonnes : Date, Home, Away, S_Dom, S_Ext
    try:
        df = pd.read_csv("data_2022.csv") 
        # Conversion des dates si nécessaire
        # df['Date'] = pd.to_datetime(df['Date'], dayfirst=True) 
        
        # Calcul des metrics (identique au code précédent)
        metrics_list = df.apply(lambda x: extract_metrics(x['S_Dom'], x['S_Ext']), axis=1)
        df_metrics = pd.DataFrame(metrics_list.tolist())
        return pd.concat([df, df_metrics], axis=1)
    except FileNotFoundError:
        st.error("ERREUR: Le fichier data_2022.csv est introuvable.")
        return pd.DataFrame()
    df = pd.DataFrame(data)
    # On calcule les métriques pour chaque match historique
    metrics_list = df.apply(lambda x: extract_metrics(x['S_Dom'], x['S_Ext']), axis=1)
    df_metrics = pd.DataFrame(metrics_list.tolist())
    return pd.concat([df, df_metrics], axis=1)

# --- 3. FIXTURES ACTUELLES (Le Jour J - 15-10-2025) ---
def load_fixtures_2025():
    # Simulation des matchs du jour qui doivent être scannés
    return pd.DataFrame([
        {'Home': 'FBC Melgar', 'Away': 'Alianza Huanuco', 'Heure': '20:00'},
        {'Home': 'AA', 'Away': '8J', 'Heure': '18:00'}, # Correspondance Équipe Dom
        {'Home': 'X3', 'Away': '4P', 'Heure': '21:00'}, # Pas de correspondance directe simple
        {'Home': 'EE', 'Away': 'TH', 'Heure': '19:30'}, # Correspondance Équipe Dom
        {'Home': 'Man City', 'Away': 'Liverpool', 'Heure': '21:00'}, # Hors système
    ])

# --- 4. ALGORITHME DE CORRESPONDANCE "TVA" ---

def scan_matches(history, today):
    results = []
    
    for idx, match_now in today.iterrows():
        # LA RÈGLE D'OR : On cherche l'équipe Domicile dans l'historique Domicile
        # (On pourrait aussi chercher Extérieur vs Extérieur)
        
        # Recherche correspondance Domicile
        match_found = history[history['Home'] == match_now['Home']]
        
        if not match_found.empty:
            historical_data = match_found.iloc[0]
            
            # C'est ici que le Paradoxe des Anniversaires prend son sens
            # On projette que le "Pattern" va se répéter
            results.append({
                'Match': f"{match_now['Home']} vs {match_now['Away']}",
                'Match_Ref': f"{historical_data['Home']} vs {historical_data['Away']} ({historical_data['Date']})",
                'Score_Ref': historical_data['Score_Exact'],
                'Total_Buts': historical_data['Total_Buts'],
                'O25': historical_data['O25'],
                'BTTS': historical_data['BTTS'],
                'Confiance': 'HAUTE' if historical_data['S_Dom'] + historical_data['S_Ext'] < 6 else 'MOYENNE' # Moins de variance sur les petits scores
            })
    
    return pd.DataFrame(results)

# --- 5. INTERFACE DASHBOARD ---

st.title("⚽ TVA &Co | Algorithme des Coïncidences")
st.markdown("### Principe : Répétition Cyclique & Paradoxe des Scores")

col_control, col_display = st.columns([1, 3])

with col_control:
    st.header("Paramètres")
    date_ref = st.date_input("Date Référence (Passé)", pd.to_datetime("2022-09-29"))
    date_target = st.date_input("Date Cible (Futur)", pd.to_datetime("2025-10-15"))
    st.info(f"Intervalle temporel détecté : {(date_target - pd.to_datetime(date_ref)).days} jours")
    
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
                                <div style="font-size:24px; font-weight:bold; color:#e74c3c">{row['BTTS']}</div>
                            </div>
                        </div>
                    </div>
                    <br>
                    """, unsafe_allow_html=True)
    else:
        st.warning("Aucune correspondance cyclique détectée pour cette date. Le système protège votre capital.")

# Section Explicative Mathématique
st.markdown("---")
with st.expander("📚 Voir la logique mathématique (Théorie TVA)"):
    st.write("""
    **Pourquoi ça marche ?**
    Si l'équipe A a produit un résultat X dans une configuration temporelle précise (2022), et que les conditions sont répliquées en 2025, la probabilité d'obtenir le même "Paquet de stats" (Score + O/U + Buts) est supérieure à la probabilité aléatoire.
    
    **Le "Combo" :**
    Nous ne parions pas sur 3 choses différentes. Si le Score Exact est 2-1 :
    1. C'est une Victoire.
    2. C'est un Over 2.5 (Automatique).
    3. C'est "Les deux marquent" (Automatique).
    
    C'est là que réside la **Value**. Un seul événement valide 4 paris.
    """)

st.dataframe(df_hist, use_container_width=True, hide_index=True)
