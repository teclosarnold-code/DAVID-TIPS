import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# --- CONFIGURATION ---
st.set_page_config(page_title="TVA &Co | PRO", layout="wide", page_icon="⚽")

# --- STYLE ---
st.markdown("""
    <style>
    .stMetric { background-color: #f8f9fa; border: 1px solid #dee2e6; }
    h3 { color: #0f5132; }
    </style>
    """, unsafe_allow_html=True)

# --- 1. MOTEUR MATHÉMATIQUE ---
def extract_metrics(score_dom, score_ext):
    try:
        total_goals = int(score_dom) + int(score_ext)
        return {
            'Score_Exact': f"{int(score_dom)}-{int(score_ext)}",
            'Total_Buts': total_goals,
            'O15': "OUI" if total_goals > 1.5 else "NON",
            'O25': "OUI" if total_goals > 2.5 else "NON",
            'BTTS': "OUI" if (int(score_dom) > 0 and int(score_ext) > 0) else "NON"
        }
    except:
        return None

# --- 2. CHARGEMENT INTELLIGENT (Traducteur automatique) ---
@st.cache_data
def load_database_2022():
    try:
        # Lecture du fichier
        try: df = pd.read_csv("data_2022.csv", sep=',')
        except: df = pd.read_csv("data_2022.csv", sep=';')
        
        # --- TRADUCTEUR DE COLONNES (Le Secret) ---
        # Si le fichier vient de football-data.co.uk, les colonnes sont :
        # HomeTeam, AwayTeam, FTHG (Buts Dom), FTAG (Buts Ext), Date
        
        rename_map = {
            'HomeTeam': 'Home',
            'AwayTeam': 'Away',
            'FTHG': 'S_Dom',
            'FTAG': 'S_Ext',
            'Date': 'Date' # Parfois Date est déjà Date
        }
        df = df.rename(columns=rename_map)
        
        # Vérification finale que les colonnes existent maintenant
        required_cols = ['Home', 'Away', 'S_Dom', 'S_Ext']
        
        # Si une colonne manque, on arrête tout
        if not all(col in df.columns for col in required_cols): 
            st.error("Le fichier CSV n'a pas le bon format standard (HomeTeam, AwayTeam, FTHG, FTAG).")
            return pd.DataFrame()
            
        # Nettoyage des données (supprimer les lignes vides)
        df = df.dropna(subset=['Home', 'Away', 'S_Dom', 'S_Ext'])
            
        # Calcul des stats
        metrics_list = df.apply(lambda x: extract_metrics(x['S_Dom'], x['S_Ext']), axis=1)
        df_metrics = pd.DataFrame(metrics_list.tolist())
        return pd.concat([df, df_metrics], axis=1)

    except FileNotFoundError:
        # C'EST ICI QUE LE MODE DÉMO S'ACTIVE SI TU N'AS PAS MIS LE FICHIER
        return pd.DataFrame() # Retourne vide pour forcer l'alerte visuelle

# --- 3. ALGORITHME DE MATCHING ---
def scan_matches(history, match_input):
    results = []
    if history.empty or match_input.empty: return pd.DataFrame()

    for idx, row in match_input.iterrows():
        if pd.isna(row['Home']) or row['Home'] == "": continue
        
        # Nettoyage strict
        team_home = str(row['Home']).strip()
        
        # Recherche correspondance (Insensible à la casse si possible)
        # On cherche l'équipe Domicile dans la colonne Home de l'historique
        found = history[history['Home'].astype(str).str.strip() == team_home]
        
        if not found.empty:
            # On prend le dernier match trouvé ou le premier de la liste
            hist_data = found.iloc[0]
            
            if hist_data['Score_Exact'] is not None:
                results.append({
                    'Match': f"{row['Home']} vs {row['Away']}",
                    'Match_Ref': f"{hist_data['Home']} vs {hist_data['Away']} ({hist_data['Date']})",
                    'Score_Ref': hist_data['Score_Exact'],
                    'Total_Buts': hist_data['Total_Buts'],
                    'O25': hist_data['O25'],
                    'BTTS': hist_data['BTTS']
                })
    return pd.DataFrame(results)

# --- 4. FONCTION D'AFFICHAGE ---
def render_tab_content(label, df_history):
    st.markdown(f"### 📅 Saisie : {label}")
    
    col_input, col_res = st.columns([1, 2])
    
    with col_input:
        st.info("✍️ Écrivez les équipes EXACTEMENT comme dans le fichier :")
        # Exemple vide
        default_data = [{"Home": "", "Away": ""}]
        if df_history.empty:
             st.warning("⚠️ FICHIER 'data_2022.csv' MANQUANT SUR GITHUB")
            
        input_df = st.data_editor(
            pd.DataFrame(default_data),
            num_rows="dynamic",
            column_config={
                "Home": st.column_config.TextColumn("Domicile"),
                "Away": st.column_config.TextColumn("Extérieur")
            },
            key=f"editor_{label}"
        )

    with col_res:
        if not df_history.empty:
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
                if input_df.iloc[0]['Home'] != "":
                    st.warning("Pas de correspondance trouvée. Vérifiez l'orthographe de l'équipe.")
        else:
            st.error("🛑 STOP : Veuillez uploader data_2022.csv sur GitHub pour activer l'IA.")

# ==========================================
# --- INTERFACE PRINCIPALE ---
# ==========================================

st.title("⚽ TVA &Co | Interface PRO")

# Chargement Base
df_base = load_database_2022()

if not df_base.empty:
    st.toast(f"✅ Base de données chargée : {len(df_base)} matchs en mémoire.", icon="💾")

# ONGLETS
tab_hier, tab_auj, tab_demain = st.tabs(["⏮️ HIER", "🚨 AUJOURD'HUI", "⏭️ DEMAIN"])

with tab_hier: render_tab_content("Hier", df_base)
with tab_auj: render_tab_content("Aujourd'hui", df_base)
with tab_demain: render_tab_content("Demain", df_base)
