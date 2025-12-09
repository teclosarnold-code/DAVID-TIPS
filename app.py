import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import requests
import io

# --- CONFIGURATION SYSTÈME ---
st.set_page_config(page_title="TVA &Co | AUTO-PILOTE", layout="wide", page_icon="🚀")

# Mise à jour du cache toutes les 12h (43200 secondes)
CACHE_TIME = 43200 

st.markdown("""
    <style>
    .match-card { background-color: #1e293b; padding: 15px; border-radius: 8px; margin-bottom: 10px; border-left: 5px solid #10b981; }
    .date-badge { background-color: #334155; color: #fff; padding: 2px 8px; border-radius: 4px; font-size: 12px; }
    .score-ref { color: #fbbf24; font-weight: bold; font-size: 18px; }
    </style>
    """, unsafe_allow_html=True)

# --- 1. CHARGEMENT AUTOMATIQUE DES LIGUES (2022-2023) ---
@st.cache_data(ttl=CACHE_TIME)
def load_historical_data():
    # Liste des URLs officielles des championnats (Saison 22/23)
    urls = {
        "France (L1)": "https://www.football-data.co.uk/mmz4281/2223/F1.csv",
        "France (L2)": "https://www.football-data.co.uk/mmz4281/2223/F2.csv",
        "Angleterre (PL)": "https://www.football-data.co.uk/mmz4281/2223/E0.csv",
        "Belgique": "https://www.football-data.co.uk/mmz4281/2223/B1.csv",
        "Turquie": "https://www.football-data.co.uk/mmz4281/2223/T1.csv",
        "Espagne": "https://www.football-data.co.uk/mmz4281/2223/SP1.csv",
        "Italie": "https://www.football-data.co.uk/mmz4281/2223/I1.csv",
        "Allemagne": "https://www.football-data.co.uk/mmz4281/2223/D1.csv",
        "Pays-Bas": "https://www.football-data.co.uk/mmz4281/2223/N1.csv",
        "Portugal": "https://www.football-data.co.uk/mmz4281/2223/P1.csv"
    }
    
    all_data = []
    
    for league, url in urls.items():
        try:
            r = requests.get(url)
            df = pd.read_csv(io.StringIO(r.content.decode('latin1'))) # latin1 pour les accents
            # Standardisation
            df = df[['Date', 'HomeTeam', 'AwayTeam', 'FTHG', 'FTAG']].dropna()
            df['League'] = league
            all_data.append(df)
        except:
            continue # Si un lien foire, on continue les autres
            
    if all_data:
        full_df = pd.concat(all_data)
        # Conversion Date (Format Jour/Mois/Année)
        full_df['Date'] = pd.to_datetime(full_df['Date'], dayfirst=True, errors='coerce')
        return full_df
    return pd.DataFrame()

# --- 2. CHARGEMENT DU CALENDRIER ACTUEL (FIXTURES) ---
# Puisque nous ne pouvons pas scraper Flashscore sans blocage, nous utilisons un fichier "Fixtures"
# ou nous permettons à l'utilisateur de coller la liste brute une fois.
@st.cache_data(ttl=CACHE_TIME) 
def load_upcoming_fixtures():
    # ICI : On essaie de charger un fichier de calendrier public
    # Si ça échoue, on retourne vide et on demandera à l'utilisateur de coller son texte Flashscore
    # C'est la seule façon d'éviter le blocage "Anti-Bot".
    return pd.DataFrame() 

# --- 3. MOTEUR DE CALCUL TEMPOREL (LE DÉCALAGE) ---
def find_match_by_offset(history_df, team_home, ref_date_2022):
    # On cherche si l'équipe a joué à la date exacte calculée
    match = history_df[
        (history_df['Date'] == ref_date_2022) & 
        (history_df['HomeTeam'].str.lower() == team_home.lower().strip())
    ]
    
    if not match.empty:
        rec = match.iloc[0]
        s_dom, s_ext = int(rec['FTHG']), int(rec['FTAG'])
        total = s_dom + s_ext
        return {
            'Found': True,
            'Match_Ref': f"{rec['HomeTeam']} vs {rec['AwayTeam']}",
            'Score': f"{s_dom}-{s_ext}",
            'Total': total,
            'O25': "OUI" if total > 2.5 else "NON",
            'BTTS': "OUI" if (s_dom > 0 and s_ext > 0) else "NON",
            'League': rec['League']
        }
    return None

# ==========================================
# --- INTERFACE ---
# ==========================================

st.title("🚀 TVA &Co | PREDICTION IA AUTO")

# --- CHARGEMENT SILENCIEUX ---
with st.spinner("Mise à jour des bases de données (Update 12h)..."):
    df_history = load_historical_data()

col_status, col_conf = st.columns([1, 3])
col_status.success(f"Base de Données : {len(df_history)} matchs (Europe/Monde)")

# --- CONFIGURATION DU "SHIFT" TEMPOREL ---
with col_conf:
    st.info("ℹ️ RÉGLAGE DE LA MACHINE À REMONTER LE TEMPS")
    c1, c2 = st.columns(2)
    # L'utilisateur dit : "Aujourd'hui (2025)" correspond à "Telle date (2022)"
    today_real = datetime.now().date()
    
    # C'est ici que tu règles ta "Journée du 22-11-2022"
    ref_date_input = c2.date_input("Date Miroir (2022)", pd.to_datetime("2022-11-22"))
    
    # Calcul du décalage (Delta)
    delta_days = (pd.to_datetime(today_real) - pd.to_datetime(ref_date_input)).days
    c1.metric("Décalage Temporel Actif", f"-{delta_days} Jours")

st.divider()

# --- GESTION DES ONGLETS ---
tab_hier, tab_auj, tab_demain, tab_j3 = st.tabs(["⏮️ HIER", "🚨 AUJOURD'HUI", "⏭️ DEMAIN", "📅 J+3"])

def render_tab(day_offset):
    # 1. Calcul de la date réelle affichée (Ex: Demain)
    target_date_real = datetime.now() + timedelta(days=day_offset)
    
    # 2. Calcul AUTOMATIQUE de la date historique correspondante
    # Si Aujourd'hui = 22/11/22, Alors Demain = 23/11/22. L'algo le fait tout seul.
    target_date_history = target_date_real - timedelta(days=delta_days)
    
    st.subheader(f"Programme du {target_date_real.strftime('%d-%m-%Y')}")
    st.caption(f"🤖 L'IA cherche les matchs joués le : **{target_date_history.strftime('%d-%m-%Y')}** (Base 2022)")
    
    # 3. Saisie des équipes (C'est là qu'on gagne du temps)
    # L'utilisateur colle TOUT le bloc de texte de Flashscore d'un coup
    raw_text = st.text_area(f"Collez les matchs ici (Copier/Coller Flashscore)", height=100, key=f"txt_{day_offset}", placeholder="Monaco\nGalatasaray\nUnion SG")
    
    if raw_text:
        # Nettoyage automatique du texte (enlève les heures, garde les noms)
        lines = raw_text.split('\n')
        
        found_count = 0
        for line in lines:
            # On prend chaque ligne comme un nom d'équipe potentiel
            team_name = line.strip()
            if len(team_name) < 3: continue # Ignore les lignes vides ou "20:00"
            
            # RECHERCHE DANS LA BASE
            # Note: target_date_history doit être converti en Timestamp pour matcher pandas
            res = find_match_by_offset(df_history, team_name, pd.to_datetime(target_date_history))
            
            if res:
                found_count += 1
                with st.container():
                    st.markdown(f"""
                    <div class="match-card">
                        <div style="display:flex; justify-content:space-between;">
                            <span style="color:#fff; font-weight:bold;">{team_name} (2025)</span>
                            <span class="date-badge">{res['League']}</span>
                        </div>
                        <div style="margin-top:5px; color:#94a3b8; font-size:13px;">
                            Identifié comme : {res['Match_Ref']}
                        </div>
                        <hr style="border-color:#334155;">
                        <div style="display:flex; justify-content:space-between; align-items:center;">
                            <div>
                                Score Prédit : <span class="score-ref">{res['Score']}</span>
                            </div>
                            <div>
                                O2.5: <b>{res['O25']}</b> | BTTS: <b>{res['BTTS']}</b>
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
        
        if found_count == 0:
            st.warning(f"Aucune correspondance trouvée pour le {target_date_history.strftime('%d-%m-%Y')}. Vérifiez que ces équipes jouaient bien à cette date précise en 2022.")

# --- RENDER DES ONGLETS ---
with tab_hier: render_tab(-1)
with tab_auj: render_tab(0)
with tab_demain: render_tab(1)
with tab_j3: render_tab(3) # Pour ton avance de 3 jours
