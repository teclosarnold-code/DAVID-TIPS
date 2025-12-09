import streamlit as st
import pandas as pd
import numpy as np
import requests
import io

# --- 1. CONFIGURATION DU CERVEAU ---
st.set_page_config(page_title="TVA &Co | AUTO", layout="wide", page_icon="⚡")

st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: #fff; }
    .metric-box { background: #1f2937; padding: 15px; border-radius: 8px; border: 1px solid #374151; }
    .success-box { border-left: 5px solid #10b981; background: #064e3b; padding: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. FONCTIONS DE CALCUL (MOTEUR) ---
def get_metrics(row):
    try:
        s_dom = int(row['FTHG'])
        s_ext = int(row['FTAG'])
        total = s_dom + s_ext
        return pd.Series({
            'Ref_Score': f"{s_dom}-{s_ext}",
            'Total': total,
            'O25': "OUI" if total > 2.5 else "NON",
            'BTTS': "OUI" if (s_dom > 0 and s_ext > 0) else "NON"
        })
    except:
        return pd.Series([None, None, None, None])

# --- 3. ROBOT DE TÉLÉCHARGEMENT (L'AUTOMATISATION) ---
@st.cache_data
def robot_fetch_data():
    # URL DIRECTE des serveurs de données (Premier League 22/23)
    url = "https://www.football-data.co.uk/mmz4281/2223/E0.csv"
    
    try:
        # Le robot va chercher le fichier sur internet
        response = requests.get(url)
        response.raise_for_status() # Vérifie si le lien est mort
        
        # Conversion en tableau
        df = pd.read_csv(io.StringIO(response.content.decode('utf-8')))
        
        # Nettoyage et Calculs Automatiques
        df = df[['Date', 'HomeTeam', 'AwayTeam', 'FTHG', 'FTAG']].dropna()
        metrics = df.apply(get_metrics, axis=1)
        final_df = pd.concat([df, metrics], axis=1)
        
        return final_df, "CONNECTÉ"
    except Exception as e:
        return pd.DataFrame(), f"ERREUR DE CONNEXION: {e}"

# --- 4. ALGORITHME DE SCAN ---
def scan_protocol(db, home_team, away_team):
    if db.empty: return None
    
    # Recherche stricte
    match = db[db['HomeTeam'].str.lower() == home_team.lower().strip()]
    
    if not match.empty:
        rec = match.iloc[0] # Prend le premier match trouvé
        return {
            'Date': rec['Date'],
            'Match': f"{rec['HomeTeam']} vs {rec['AwayTeam']}",
            'Score': rec['Ref_Score'],
            'Total': rec['Total'],
            'O25': rec['O25'],
            'BTTS': rec['BTTS']
        }
    return None

# ============================================
# --- INTERFACE "ZERO CONFIG" ---
# ============================================

st.title("⚡ TVA &Co | VERSION AUTOMATIQUE")
st.caption("Connexion directe aux serveurs distants. Aucun fichier requis.")

# --- ÉTAPE 1 : LE ROBOT S'ACTIVE ---
with st.spinner('Le robot télécharge les données de la Premier League 2022...'):
    df_base, status = robot_fetch_data()

# Affichage du statut du robot
if not df_base.empty:
    st.markdown(f"""
    <div class="success-box">
        <b>✅ SYSTÈME EN LIGNE</b><br>
        Source : Serveurs UK (Football-Data)<br>
        Matchs en mémoire : <b>{len(df_base)}</b> (Saison 22/23)
    </div>
    """, unsafe_allow_html=True)
else:
    st.error(f"❌ ÉCHEC DU ROBOT : {status}")
    st.stop()

st.divider()

# --- ÉTAPE 2 : SCANNER RAPIDE ---
col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("📡 Radar Match du Jour")
    st.info("Simulation de l'API Live (Entrez le match manuellement car l'API payante est désactivée)")
    
    # Saisie ultra-rapide
    team_home = st.text_input("Équipe Domicile", placeholder="ex: Arsenal")
    team_away = st.text_input("Équipe Extérieur", placeholder="ex: Chelsea")
    
    btn_scan = st.button("LANCER LE SCANNER", type="primary", use_container_width=True)

with col2:
    if btn_scan and team_home:
        # Lancement de l'algo
        result = scan_protocol(df_base, team_home, team_away)
        
        if result:
            st.markdown(f"### 🎯 RÉSULTAT DU SCAN")
            
            # Affichage style "Terminal"
            st.code(f"""
            [MATCH TROUVÉ DANS L'HISTORIQUE]
            DATE : {result['Date']}
            REF  : {result['Match']}
            --------------------------------
            SCORE EXACT    : {result['Score']}
            TOTAL BUTS     : {result['Total']}
            OVER 2.5       : {result['O25']}
            LES 2 MARQUENT : {result['BTTS']}
            """)
            
            if result['O25'] == "OUI":
                st.success("💰 ALGORITHME DÉTECTE UNE VALUE : OVER 2.5")
            else:
                st.warning("🛡️ ALGORITHME PRUDENT : UNDER 2.5")
                
        else:
            st.warning(f"⛔ Aucune correspondance trouvée pour '{team_home}' dans la base 2022.")
            st.markdown("**Aide :** Essayez *Arsenal*, *Liverpool*, *Man City*, *Chelsea*...")

# --- PREUVE DE DONNÉES ---
with st.expander("👁️ Voir les données téléchargées par le robot"):
    st.dataframe(df_base)
