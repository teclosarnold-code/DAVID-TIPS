import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# --- CONFIGURATION ---
st.set_page_config(page_title="TVA &Co | FULL AUTO", layout="wide", page_icon="🤖")

st.markdown("""
    <style>
    .big-card { background-color: #111827; padding: 20px; border-radius: 12px; border: 1px solid #374151; margin-bottom: 15px; }
    .team-name { font-size: 22px; font-weight: bold; color: #fff; }
    .vs { color: #6b7280; margin: 0 10px; }
    .prediction-box { background-color: #064e3b; padding: 10px; border-radius: 8px; margin-top: 10px; }
    .no-match { color: #ef4444; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# =========================================================
# 1. LE CERVEAU (CHARGEMENT DES DEUX MONDES)
# =========================================================

@st.cache_data
def load_data():
    # CHARGEMENT DU PASSÉ (2022)
    try:
        df_past = pd.read_csv("history_2022.csv") # Ton fichier habituel
        # Standardisation des colonnes
        # On suppose que ton fichier a: Date, Home, Away, S_Dom, S_Ext
        df_past.columns = [c.lower() for c in df_past.columns] 
        # On renforce la détection de la date
        df_past['date'] = pd.to_datetime(df_past['date'], dayfirst=True, errors='coerce')
    except:
        df_past = pd.DataFrame()

    # CHARGEMENT DU FUTUR (CALENDRIER 2025)
    # C'est le fichier que tu télécharges une fois pour toute la saison
    try:
        df_future = pd.read_csv("calendrier_2025.csv") 
        # Il doit contenir au moins: Date, Home, Away
        df_future.columns = [c.lower() for c in df_future.columns]
        df_future['date'] = pd.to_datetime(df_future['date'], dayfirst=True, errors='coerce')
    except:
        df_future = pd.DataFrame()
        
    return df_past, df_future

# =========================================================
# 2. LE CALCULATEUR TEMPOREL (LA SORCELLERIE)
# =========================================================

def get_predictions_automatic(df_p, df_f, offset_days):
    # 1. QUEL JOUR SOMMES-NOUS ? (Heure de l'ordinateur + décalage voulu)
    target_date_real = datetime.now() + timedelta(days=offset_days)
    target_date_str = target_date_real.strftime('%Y-%m-%d')
    
    # 2. QUI JOUE A CETTE DATE DANS LE CALENDRIER 2025 ?
    if df_f.empty: return "NO_CALENDAR", []
    
    todays_matches = df_f[df_f['date'] == target_date_str]
    
    if todays_matches.empty: return "NO_MATCHES", []
    
    results = []
    
    # 3. LE MAPPING (LA BOUCLE)
    # Pour chaque match prévu aujourd'hui...
    for idx, match in todays_matches.iterrows():
        team_home = str(match['home']).strip()
        team_away = str(match['away']).strip()
        
        # ... On cherche le jumeau en 2022
        # Note: Ici on applique ta logique de "Même équipe".
        # Si tu veux appliquer une logique de "Date précise en 2022", tu modifies ici.
        
        # Recherche dans l'historique global ou sur une date précise calculée ?
        # Dans ta logique "Automatique", on cherche si l'équipe a une "Signature" cette saison là.
        
        # Exemple : On cherche le match aller ou le match à date équivalente
        # Pour simplifier l'automatisme : On cherche le dernier match identique Domicile vs Extérieur en 2022
        history_match = df_p[
            (df_p['home'].str.lower() == team_home.lower()) & 
            (df_p['away'].str.lower() == team_away.lower())
        ]
        
        if not history_match.empty:
            ref = history_match.iloc[0]
            s_d = int(ref['s_dom']) if 's_dom' in ref else 0
            s_e = int(ref['s_ext']) if 's_ext' in ref else 0
            total = s_d + s_e
            
            results.append({
                'Home': team_home,
                'Away': team_away,
                'Ref_Date': ref['date'].strftime('%d-%m-%Y') if pd.notnull(ref['date']) else "2022",
                'Score': f"{s_d}-{s_e}",
                'O25': "OUI" if total > 2.5 else "NON",
                'BTTS': "OUI" if s_d > 0 and s_e > 0 else "NON"
            })
            
    return "OK", results

# =========================================================
# 3. L'INTERFACE (ZÉRO CLIC)
# =========================================================

st.title("🤖 TVA &Co | PILOTE AUTOMATIQUE")

# Chargement silencieux
df_history, df_calendar = load_data()

# Vérification des fichiers
if df_history.empty:
    st.error("❌ ERREUR CRITIQUE : Fichier 'history_2022.csv' manquant.")
    st.stop()
if df_calendar.empty:
    st.error("❌ ERREUR CRITIQUE : Fichier 'calendrier_2025.csv' manquant.")
    st.info("💡 Solution : Téléchargez le calendrier complet de la saison 2025 sur Flashscore/Web et nommez-le 'calendrier_2025.csv'.")
    st.stop()

# BARRE DE TEMPS AUTOMATIQUE
st.subheader(f"📅 Analyse Automatique du {datetime.now().strftime('%d-%m-%Y')}")

# On scanne automatiquement Aujourd'hui (0), Demain (1), Après-demain (2)
tabs = st.tabs(["AUJOURD'HUI", "DEMAIN", "J+2"])

for i, tab in enumerate(tabs):
    with tab:
        status, preds = get_predictions_automatic(df_history, df_calendar, i)
        
        if status == "NO_MATCHES":
            st.warning("Aucun match programmé dans le fichier 'calendrier_2025.csv' pour cette date.")
        elif status == "OK" and preds:
            st.success(f"{len(preds)} Matchs Analysés & Traités")
            
            for p in preds:
                st.markdown(f"""
                <div class="big-card">
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <div>
                            <span class="team-name">{p['Home']}</span> <span class="vs">vs</span> <span class="team-name">{p['Away']}</span>
                        </div>
                        <div style="text-align:right; color:#9ca3af;">
                            Réf 2022: {p['Ref_Date']}
                        </div>
                    </div>
                    
                    <div class="prediction-box">
                        <div style="display:flex; justify-content:space-around; color:#fff; font-weight:bold; font-size:18px;">
                            <span>SCORE: {p['Score']}</span>
                            <span>O2.5: {p['O25']}</span>
                            <span>BTTS: {p['BTTS']}</span>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("Matchs trouvés au calendrier, mais aucune correspondance historique en 2022.")
