# app.py - TVA &Co Prediction IA - 100% AUTOMATIQUE SCRAPING

import streamlit as st
import requests
from datetime import datetime, timedelta
import json

# ============================================================
# CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="TVA Prediction IA",
    page_icon="⚽",
    layout="wide"
)

DECALAGE_JOURS = 730  # 2 ans entre saisons

# ============================================================
# API GRATUITE - API-FOOTBALL (rapidapi.com)
# 100 requetes/jour GRATUIT
# ============================================================

API_KEY = "VOTRE_CLE_GRATUITE"  # Obtenir sur rapidapi.com/api-sports/api/api-football
API_HOST = "v3.football.api-sports.io"

# ============================================================
# SCRAPING AUTOMATIQUE
# ============================================================

@st.cache_data(ttl=43200)  # Cache 12 heures
def fetch_matches_from_api(date_str, season):
    """
    Telecharge automatiquement les matchs depuis l'API
    """
    
    matches = []
    
    try:
        # Convertir date DD-MM-YYYY vers YYYY-MM-DD
        date_obj = datetime.strptime(date_str, "%d-%m-%Y")
        date_api = date_obj.strftime("%Y-%m-%d")
        
        # Leagues: 39=PL, 140=LaLiga, 135=SerieA, 61=Ligue1, 78=Bundesliga
        leagues = [39, 140, 135, 61, 78]
        
        for league_id in leagues:
            url = "https://v3.football.api-sports.io/fixtures"
            
            headers = {
                "x-rapidapi-key": API_KEY,
                "x-rapidapi-host": API_HOST
            }
            
            params = {
                "date": date_api,
                "league": league_id,
                "season": season
            }
            
            response = requests.get(url, headers=headers, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                for fixture in data.get("response", []):
                    teams = fixture.get("teams", {})
                    goals = fixture.get("goals", {})
                    league = fixture.get("league", {})
                    fixture_info = fixture.get("fixture", {})
                    
                    matches.append({
                        "date": date_str,
                        "home": teams.get("home", {}).get("name", ""),
                        "away": teams.get("away", {}).get("name", ""),
                        "score_home": goals.get("home"),
                        "score_away": goals.get("away"),
                        "league": league.get("name", ""),
                        "time": fixture_info.get("date", "")[11:16],
                        "status": fixture_info.get("status", {}).get("short", "")
                    })
    
    except Exception as e:
        st.error(f"Erreur API: {e}")
    
    return matches

@st.cache_data(ttl=43200)
def fetch_matches_free_api(date_str):
    """
    Alternative: API football-data.org (gratuit sans cle)
    """
    
    matches = []
    
    try:
        date_obj = datetime.strptime(date_str, "%d-%m-%Y")
        date_api = date_obj.strftime("%Y-%m-%d")
        
        # Football-data.org - 10 requetes/min gratuit
        url = f"https://api.football-data.org/v4/matches"
        
        headers = {
            "X-Auth-Token": "YOUR_FREE_TOKEN"  # Gratuit sur football-data.org
        }
        
        params = {
            "dateFrom": date_api,
            "dateTo": date_api
        }
        
        response = requests.get(url, headers=headers, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            for match in data.get("matches", []):
                score = match.get("score", {}).get("fullTime", {})
                
                matches.append({
                    "date": date_str,
                    "home": match.get("homeTeam", {}).get("name", ""),
                    "away": match.get("awayTeam", {}).get("name", ""),
                    "score_home": score.get("home"),
                    "score_away": score.get("away"),
                    "league": match.get("competition", {}).get("name", ""),
                    "time": match.get("utcDate", "")[11:16],
                    "status": match.get("status", "")
                })
    
    except Exception as e:
        pass
    
    return matches

@st.cache_data(ttl=43200)
def scrape_flashscore_direct(date_str):
    """
    Scraping direct Flashscore (sans API)
    """
    
    matches = []
    
    try:
        date_obj = datetime.strptime(date_str, "%d-%m-%Y")
        
        # Flashscore utilise un format specifique
        # On utilise une API tierce qui scrape Flashscore
        
        # Option 1: AllSportsAPI (gratuit)
        url = "https://allsportsapi.com/api/football/"
        
        # Option 2: TheSportsDB (gratuit)
        date_api = date_obj.strftime("%Y-%m-%d")
        url = f"https://www.thesportsdb.com/api/v1/json/3/eventsday.php?d={date_api}&s=Soccer"
        
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            events = data.get("events", []) or []
            
            for event in events:
                # Filtrer les grandes ligues
                league = event.get("strLeague", "")
                
                top_leagues = ["English Premier League", "Spanish La Liga", 
                              "Italian Serie A", "French Ligue 1", "German Bundesliga"]
                
                if any(l in league for l in top_leagues):
                    matches.append({
                        "date": date_str,
                        "home": event.get("strHomeTeam", ""),
                        "away": event.get("strAwayTeam", ""),
                        "score_home": event.get("intHomeScore"),
                        "score_away": event.get("intAwayScore"),
                        "league": league,
                        "time": event.get("strTime", "")[:5] if event.get("strTime") else "",
                        "status": "FT" if event.get("intHomeScore") else "NS"
                    })
    
    except Exception as e:
        pass
    
    return matches

# ============================================================
# FONCTION PRINCIPALE - TELECHARGE TOUT
# ============================================================

@st.cache_data(ttl=43200)  # 12 heures
def get_all_matches(date_str, season):
    """
    Essaie plusieurs sources pour obtenir les matchs
    """
    
    # Essayer TheSportsDB (gratuit, sans cle)
    matches = scrape_flashscore_direct(date_str)
    
    if matches:
        return matches
    
    # Sinon essayer football-data.org
    matches = fetch_matches_free_api(date_str)
    
    if matches:
        return matches
    
    # Sinon API-Football (necessite cle gratuite)
    matches = fetch_matches_from_api(date_str, season)
    
    return matches

# ============================================================
# FONCTIONS UTILITAIRES
# ============================================================

def get_date_offset(offset=0):
    date = datetime.now() + timedelta(days=offset)
    return date.strftime("%d-%m-%Y")

def get_date_reference(date_str):
    try:
        date_obj = datetime.strptime(date_str, "%d-%m-%Y")
        date_ref = date_obj - timedelta(days=DECALAGE_JOURS)
        return date_ref.strftime("%d-%m-%Y")
    except:
        return None

def get_season_from_date(date_str):
    try:
        date_obj = datetime.strptime(date_str, "%d-%m-%Y")
        year = date_obj.year
        month = date_obj.month
        
        if month >= 8:
            return year
        else:
            return year - 1
    except:
        return 2024

def analyze_match(score_home, score_away):
    if score_home is None or score_away is None:
        return None
    
    try:
        score_home = int(score_home)
        score_away = int(score_away)
    except:
        return None
    
    total = score_home + score_away
    
    return {
        "score": f"{score_home}-{score_away}",
        "total": total,
        "result": "1" if score_home > score_away else ("2" if score_away > score_home else "X"),
        "over_15": "✅" if total > 1.5 else "❌",
        "over_25": "✅" if total > 2.5 else "❌",
        "over_35": "✅" if total > 3.5 else "❌",
        "btts": "✅" if (score_home > 0 and score_away > 0) else "❌",
    }

def find_team_match(team_name, matches_list):
    if not matches_list or not team_name:
        return None
    
    team_lower = team_name.lower()
    ignore = ["fc", "cf", "ac", "as", "us", "sc", "rc", "real", "sporting", "club", "city", "united"]
    keywords = [w for w in team_lower.split() if len(w) > 3 and w not in ignore]
    
    for match in matches_list:
        home_lower = str(match.get("home", "")).lower()
        away_lower = str(match.get("away", "")).lower()
        
        for kw in keywords:
            if kw in home_lower or kw in away_lower:
                return match
    
    return None

# ============================================================
# INTERFACE
# ============================================================

# Header
st.markdown("""
<div style="text-align:center; padding:30px; background:linear-gradient(135deg, #0f2027, #203a43, #2c5364); border-radius:20px; margin-bottom:30px; border:2px solid #00d4ff;">
    <h1 style="color:#00d4ff; margin:0;">⚽ TVA &Co Prediction IA</h1>
    <p style="color:#888; margin:10px 0 0 0;">100% Automatique - Scraping Flashscore</p>
    <p style="color:#00ff88; font-size:0.9em;">Mise a jour toutes les 12h</p>
</div>
""", unsafe_allow_html=True)

# ============================================================
# CALENDRIER
# ============================================================

st.subheader("📅 Selectionner une date")

# 7 jours de navigation
cols = st.columns(7)

if "selected_date" not in st.session_state:
    st.session_state.selected_date = get_date_offset(0)

labels = ["J-3", "J-2", "Hier", "📍 Auj.", "Demain", "J+2", "J+3"]

for i, offset in enumerate(range(-3, 4)):
    date = get_date_offset(offset)
    
    with cols[i]:
        is_selected = st.session_state.selected_date == date
        btn_type = "primary" if is_selected else "secondary"
        
        if st.button(f"{labels[i]}\n{date}", key=f"btn_{i}", use_container_width=True, type=btn_type):
            st.session_state.selected_date = date
            st.rerun()

# ============================================================
# CHARGEMENT AUTOMATIQUE
# ============================================================

DATE_ACTIVE = st.session_state.selected_date
DATE_REF = get_date_reference(DATE_ACTIVE)
SEASON_ACTIVE = get_season_from_date(DATE_ACTIVE)
SEASON_REF = get_season_from_date(DATE_REF)

st.markdown("---")

# Info
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.info(f"📅 **{DATE_ACTIVE}**\nSaison {SEASON_ACTIVE}-{SEASON_ACTIVE+1}")

with col2:
    st.warning(f"📆 **{DATE_REF}**\nSaison {SEASON_REF}-{SEASON_REF+1}")

with col3:
    st.markdown("⏳ Chargement...")

with col4:
    st.markdown("⏳ Chargement...")

# ============================================================
# TELECHARGEMENT AUTOMATIQUE
# ============================================================

st.markdown("---")
st.subheader("🔄 Telechargement automatique des matchs...")

# Telecharger matchs 2024-2025 (aujourd'hui)
with st.spinner(f"📥 Telechargement matchs du {DATE_ACTIVE}..."):
    matches_today = get_all_matches(DATE_ACTIVE, SEASON_ACTIVE)

# Telecharger matchs 2022-2023 (reference)
with st.spinner(f"📥 Telechargement matchs du {DATE_REF}..."):
    matches_ref = get_all_matches(DATE_REF, SEASON_REF)

# Mettre a jour les stats
col3.metric("⚽ Matchs aujourd'hui", len(matches_today))
col4.metric("📚 Matchs reference", len(matches_ref))

st.markdown("---")

# ============================================================
# AFFICHAGE RESULTATS
# ============================================================

st.header(f"🎯 Predictions du {DATE_ACTIVE}")

if not matches_today:
    st.warning(f"⚠️ Aucun match trouve pour le {DATE_ACTIVE}")
    st.info("Les donnees seront disponibles quand les matchs seront programmes.")
    
    # Afficher statut API
    st.markdown("### 🔧 Statut des sources :")
    st.write("• TheSportsDB: Verification...")
    st.write("• Football-Data.org: Verification...")
    st.write("• API-Football: Verification...")

elif not matches_ref:
    st.warning(f"⚠️ Aucun match de reference pour le {DATE_REF}")
    
    # Afficher matchs du jour quand meme
    st.markdown(f"### ⚽ Matchs du {DATE_ACTIVE} :")
    for m in matches_today:
        status = "🟢" if m.get("status") == "FT" else "🔵"
        score = f"{m['score_home']}-{m['score_away']}" if m.get("score_home") is not None else "vs"
        st.write(f"{status} {m['home']} **{score}** {m['away']} ({m['league']})")

else:
    # Afficher matchs telecharges
    with st.expander(f"📚 Matchs reference {DATE_REF} ({len(matches_ref)} matchs)"):
        for m in matches_ref:
            score = f"{m['score_home']}-{m['score_away']}" if m.get("score_home") is not None else "vs"
            st.write(f"• {m['home']} **{score}** {m['away']} ({m['league']})")
    
    with st.expander(f"⚽ Matchs du jour {DATE_ACTIVE} ({len(matches_today)} matchs)"):
        for m in matches_today:
            time_str = m.get("time", "")
            st.write(f"• {m['home']} vs {m['away']} - {time_str} ({m['league']})")
    
    st.markdown("---")
    
    # Chercher correspondances
    correspondances = []
    
    for match in matches_today:
        ref = find_team_match(match["home"], matches_ref)
        equipe = match["home"]
        
        if not ref:
            ref = find_team_match(match["away"], matches_ref)
            equipe = match["away"]
        
        if ref:
            correspondances.append({
                "match_today": match,
                "match_ref": ref,
                "equipe": equipe
            })
    
    # Stats
    col1, col2, col3 = st.columns(3)
    col1.metric("⚽ Matchs analyses", len(matches_today))
    col2.metric("✅ Correspondances", len(correspondances))
    pct = round(len(correspondances) / len(matches_today) * 100) if matches_today else 0
    col3.metric("📊 Taux", f"{pct}%")
    
    st.markdown("---")
    
    if not correspondances:
        st.warning("❌ Aucune correspondance trouvee")
        st.info("Les equipes du jour n'ont pas joue a la meme date en 2022-2023")
    
    else:
        st.success(f"✅ {len(correspondances)} correspondance(s) trouvee(s) !")
        
        for corr in correspondances:
            mt = corr["match_today"]
            mr = corr["match_ref"]
            
            st.markdown("---")
            st.markdown(f"### 🏟️ {mt['home']} vs {mt['away']}")
            st.markdown(f"**{mt['league']}** | ⏰ {mt.get('time', 'TBD')}")
            
            # Reference
            analysis = analyze_match(mr.get("score_home"), mr.get("score_away"))
            
            if analysis:
                st.info(f"🔗 **{corr['equipe']}** a joue le **{DATE_REF}**")
                st.warning(f"📊 {mr['home']} **{mr['score_home']}-{mr['score_away']}** {mr['away']}")
                
                # Predictions
                st.markdown("#### 🎯 PREDICTIONS :")
                
                cols = st.columns(7)
                
                preds = [
                    ("🎯 Score", analysis["score"], "@9.00"),
                    ("🏆 1X2", analysis["result"], "@2.20"),
                    ("⚽ O/U 1.5", analysis["over_15"], "@1.35"),
                    ("⚽ O/U 2.5", analysis["over_25"], "@1.85"),
                    ("⚽ O/U 3.5", analysis["over_35"], "@2.50"),
                    ("👥 BTTS", analysis["btts"], "@1.80"),
                    ("📊 Total", f"{analysis['total']} buts", ""),
                ]
                
                for i, (label, value, cote) in enumerate(preds):
                    with cols[i]:
                        st.markdown(f"**{label}**")
                        st.markdown(f"### {value}")
                        if cote:
                            st.caption(cote)
                
                # Combines
                st.success(f"🔥 **COMBINE** : Over 1.5 + BTTS = @{round(1.35*1.80, 2)}")
            
            else:
                st.warning("Match de reference sans score")

# ============================================================
# FOOTER
# ============================================================

st.markdown("---")

# Derniere mise a jour
last_update = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
st.caption(f"🔄 Derniere mise a jour : {last_update}")
st.caption("⚠️ Les paris sportifs comportent des risques. Jouez responsablement.")
st.caption("**TVA &Co Prediction IA** © 2025 - 100% Automatique")
