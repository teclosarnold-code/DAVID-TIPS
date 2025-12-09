import streamlit as st
import pandas as pd
import numpy as np

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(page_title="TVA &Co | Dashboard", layout="wide", page_icon="⚽")

# --- STYLE ---
st.markdown("""
    <style>
    .stMetric { background-color: #f0f2f6; padding: 10px; border-radius: 5px; border-left: 5px solid #ff4b4b; }
    div[data-testid="stExpander"] { border: 1px solid #ddd; border-radius: 5px; }
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

# --- 2. CHARGEMENT DONNÉES HISTORIQUES (2022) ---
@st.cache_data
def load_database_2022():
    # Tente de charger le fichier CSV
    try:
        try:
            df = pd.read_csv("data_2022.csv", sep=',')
        except:
            df = pd.read_csv("data_2022.csv", sep=';')
            
        required_cols = ['Home', 'Away', 'S_Dom', 'S_Ext']
        # Si colonnes manquantes, on renvoie vide
        if not all(col in df.columns for col in required_cols):
            return pd.DataFrame()
            
        metrics_list = df.apply(lambda x: extract_metrics(x['S_Dom'], x['S_Ext']), axis=1)
        df_metrics = pd.DataFrame(metrics_list.tolist())
        return pd.concat([df, df_metrics], axis=1)
    except:
        # DONNÉES DE SECOURS (DÉMO) SI PAS DE FICHIER
        data = [
            {'Date': '29-09-2022', 'Home': 'FBC Melgar', 'Away': 'Binacional', 'S_Dom': 2, 'S_Ext': 1},
            {'Date': '29-09-2022', 'Home': 'AA', 'Away': '1Z', 'S_Dom': 4, 'S_Ext': 1},
            {'Date': '29-09-2022', 'Home': 'BB', 'Away': '2Y', 'S_Dom': 4, 'S_Ext': 1},
        ]
        df = pd.DataFrame(data)
        metrics_list = df.apply(lambda x: extract_metrics(x['S_Dom'], x['S_Ext']), axis=1)
        df_metrics = pd.DataFrame(metrics_list.tolist())
        return pd.concat([df, df_metrics], axis=1)

# --- 3. ALGORITHME DE MATCHING ---
def scan_matches(history, today):
    results = []
    if history.empty: return pd.DataFrame()
    if today.empty: return pd.DataFrame()

    for idx, match_now in today.iterrows():
        # Nettoyage des noms (enlever espaces inutiles)
        if pd.isna(match_now['Home']): continue
        
        match_now_home = str(match_now['Home']).strip()
        
        # Recherche dans l'historique
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

# ==========================================
# --- INTERFACE UTILISATEUR (UI) ---
# ==========================================

st.title("⚽ TVA &Co | Dashboard")
st.markdown("### 📊 Analyseur de Coïncidences Temporelles")

# --- BARRE LATÉRALE : SAISIE DES MATCHS ---
with st.sidebar:
    st.header("📝 Saisie des Matchs (2025)")
    st.info("Modifiez le tableau ci-dessous pour ajouter les matchs du jour.")
    
    # Données par défaut pour l'exemple
    input_data = pd.DataFrame(
        [
            {"Home": "FBC Melgar", "Away": "Alianza Huanuco"},
            {"Home": "Ajouter Equipe Dom", "Away": "Ajouter Equipe Ext"},
        ]
    )

    # WIDGET ÉDITEUR DE DONNÉES (Le cœur de la modif)
    edited_df = st.data_editor(
        input_data,
        num_rows="dynamic", # Permet d'ajouter/supprimer des lignes
        column_config={
            "Home": st.column_config.TextColumn("Équipe Domicile (Aujourd'hui)"),
            "Away": st.column_config.TextColumn("Équipe Extérieur (Aujourd'hui)"),
        },
        hide_index=True
    )
    
    st.write("---")
    st.caption("Astuce: Cliquez sur '+' dans le tableau pour ajouter un match.")

# --- PARTIE PRINCIPALE ---

# 1. Chargement de l'historique (Base 2022)
df_hist = load_database_2022()

# 2. Exécution de l'Algorithme sur les données saisies
if not edited_df.empty:
    predictions = scan_matches(df_hist, edited_df)
else:
    predictions = pd.DataFrame()

# 3. Affichage des Résultats
st.divider()

col_info, col_results = st.columns([1, 3])

with col_info:
    st.subheader("ℹ️ État du Système")
    if df_hist.shape[0] < 10:
        st.warning("⚠️ Mode Démo Actif")
        st.caption("Fichier 'data_2022.csv' non détecté ou vide.")
    else:
        st.success(f"✅ Base de Données Chargée")
        st.caption(f"{len(df_hist)} matchs historiques en mémoire.")

with col_results:
    st.subheader("🎯 Résultats de l'Analyse")
    
    if not predictions.empty:
        st.success(f"✨ {len(predictions)} Correspondances trouvées !")
        
        for index, row in predictions.iterrows():
            with st.container(border=True):
                # En-tête du match
                c_title, c_ref = st.columns([3, 2])
                c_title.markdown(f"### 🏟️ {row['Match']}")
                c_ref.caption(f"Basé sur l'archive : {row['Match_Ref']}")
                
                st.markdown("---")
                
                # Les 4 Indicateurs Clés
                kpi1, kpi2, kpi3, kpi4 = st.columns(4)
                kpi1.metric("SCORE EXACT", row['Score_Ref'])
                kpi2.metric("TOTAL BUTS", row['Total_Buts'])
                kpi3.metric("OVER 2.5", row['O25'])
                kpi4.metric("LES 2 MARQUENT", row['BTTS'])
                
                # Alerte Value
                if row['O25'] == "OUI" and row['BTTS'] == "OUI":
                    st.markdown("🔥 **OPPORTUNITÉ DÉTECTÉE :** Configuration offensive récurrente.")

    else:
        st.info("En attente de matchs... ou aucune correspondance trouvée.")
        st.markdown("""
        **Comment faire ?**
        1. Regardez la barre latérale à gauche.
        2. Effacez les exemples.
        3. Écrivez les équipes qui jouent aujourd'hui (ex: 'FBC Melgar').
        4. Si l'équipe a joué à la date clé en 2022, le résultat s'affichera ici.
        """)
