# app.py - TVA &Co Prediction IA - INTERFACE HIER/AUJOURD'HUI/DEMAIN

import streamlit as st
from datetime import datetime, timedelta

# ============================================================
# CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="TVA Prediction IA",
    page_icon="⚽",
    layout="wide"
)

DECALAGE_JOURS = 1112

# ============================================================
# FONCTIONS
# ============================================================

def get_date_reference(date_str):
    try:
        date_obj = datetime.strptime(date_str, "%d-%m-%Y")
        date_ref = date_obj - timedelta(days=DECALAGE_JOURS)
        return date_ref.strftime("%d-%m-%Y")
    except:
        return "N/A"

def get_date(offset=0):
    date = datetime.now() + timedelta(days=offset)
    return date.strftime("%d-%m-%Y")

def parse_score(score_str):
    try:
        parts = score_str.replace(" ", "").split("-")
        return int(parts[0]), int(parts[1])
    except:
        return 0, 0

def analyze_match(home_score, away_score):
    total = home_score + away_score
    
    if home_score > away_score:
        result = "Victoire Domicile"
        result_short = "1"
    elif away_score > home_score:
        result = "Victoire Exterieur"
        result_short = "2"
    else:
        result = "Match Nul"
        result_short = "X"
    
    return {
        "score_exact": str(home_score) + "-" + str(away_score),
        "total_buts": total,
        "resultat": result,
        "resultat_short": result_short,
        "over_15": total > 1.5,
        "over_25": total > 2.5,
        "over_35": total > 3.5,
        "btts": home_score > 0 and away_score > 0,
    }

def find_match_reference(equipe, matches_ref):
    equipe_lower = equipe.lower()
    ignore = ["fc", "cf", "ac", "as", "us", "sc", "rc", "real", "sporting", "athletic", "atletico", "olympique", "paris", "saint"]
    
    keywords = [w for w in equipe_lower.split() if len(w) > 3 and w not in ignore]
    
    for m_ref in matches_ref:
        ref_home = m_ref["home"].lower()
        ref_away = m_ref["away"].lower()
        
        for kw in keywords:
            if kw in ref_home:
                return m_ref, "domicile"
            if kw in ref_away:
                return m_ref, "exterieur"
    
    return None, None

# ============================================================
# BASE DE DONNÉES 2022 (RÉFÉRENCE)
# ============================================================

MATCHES_2022 = {
    "29-09-2022": [
        {"home": "FBC Melgar", "away": "Binacional", "score": "2-1", "league": "Liga 1 Peru"},
        {"home": "Real Madrid", "away": "Barcelona", "score": "3-1", "league": "La Liga"},
        {"home": "Liverpool", "away": "Arsenal", "score": "2-2", "league": "Premier League"},
        {"home": "PSG", "away": "Lyon", "score": "1-0", "league": "Ligue 1"},
        {"home": "Bayern Munich", "away": "Dortmund", "score": "4-2", "league": "Bundesliga"},
        {"home": "Juventus", "away": "AC Milan", "score": "1-1", "league": "Serie A"},
        {"home": "Napoli", "away": "Torino", "score": "3-1", "league": "Serie A"},
        {"home": "Chelsea", "away": "West Ham", "score": "2-1", "league": "Premier League"},
        {"home": "Marseille", "away": "Lille", "score": "2-1", "league": "Ligue 1"},
        {"home": "Atletico Madrid", "away": "Real Sociedad", "score": "1-1", "league": "La Liga"},
        {"home": "Manchester United", "away": "Aston Villa", "score": "0-1", "league": "Premier League"},
        {"home": "Fiorentina", "away": "Verona", "score": "2-0", "league": "Serie A"},
    ],
    "30-09-2022": [
        {"home": "Atletico Madrid", "away": "Sevilla", "score": "2-1", "league": "La Liga"},
        {"home": "Manchester City", "away": "Chelsea", "score": "2-0", "league": "Premier League"},
        {"home": "Inter", "away": "Roma", "score": "1-2", "league": "Serie A"},
        {"home": "Monaco", "away": "Nice", "score": "1-1", "league": "Ligue 1"},
        {"home": "Borussia Dortmund", "away": "Schalke", "score": "1-0", "league": "Bundesliga"},
        {"home": "Valencia", "away": "Elche", "score": "2-2", "league": "La Liga"},
        {"home": "Torino", "away": "Empoli", "score": "1-1", "league": "Serie A"},
        {"home": "Lens", "away": "Reims", "score": "2-1", "league": "Ligue 1"},
        {"home": "Brighton", "away": "Crystal Palace", "score": "1-1", "league": "Premier League"},
        {"home": "Atalanta", "away": "Fiorentina", "score": "1-0", "league": "Serie A"},
    ],
    "01-10-2022": [
        {"home": "Tottenham", "away": "Leicester", "score": "3-1", "league": "Premier League"},
        {"home": "Villarreal", "away": "Valencia", "score": "0-0", "league": "La Liga"},
        {"home": "AC Milan", "away": "Empoli", "score": "3-0", "league": "Serie A"},
        {"home": "Rennes", "away": "Nantes", "score": "3-0", "league": "Ligue 1"},
        {"home": "Wolfsburg", "away": "Stuttgart", "score": "3-2", "league": "Bundesliga"},
        {"home": "Sevilla", "away": "Athletic Bilbao", "score": "1-0", "league": "La Liga"},
        {"home": "Newcastle", "away": "Fulham", "score": "4-1", "league": "Premier League"},
        {"home": "RB Leipzig", "away": "Bochum", "score": "4-0", "league": "Bundesliga"},
        {"home": "Udinese", "away": "Atalanta", "score": "2-2", "league": "Serie A"},
        {"home": "Montpellier", "away": "Auxerre", "score": "2-1", "league": "Ligue 1"},
    ],
    "02-10-2022": [
        {"home": "Barcelona", "away": "Celta Vigo", "score": "1-0", "league": "La Liga"},
        {"home": "Arsenal", "away": "Tottenham", "score": "3-1", "league": "Premier League"},
        {"home": "Lazio", "away": "Spezia", "score": "4-0", "league": "Serie A"},
        {"home": "Bayer Leverkusen", "away": "Werder Bremen", "score": "1-0", "league": "Bundesliga"},
        {"home": "Lyon", "away": "Toulouse", "score": "1-1", "league": "Ligue 1"},
        {"home": "Manchester United", "away": "Everton", "score": "2-1", "league": "Premier League"},
        {"home": "Roma", "away": "Lecce", "score": "2-1", "league": "Serie A"},
        {"home": "Real Sociedad", "away": "Getafe", "score": "1-0", "league": "La Liga"},
    ],
    "03-10-2022": [
        {"home": "Real Betis", "away": "Girona", "score": "2-1", "league": "La Liga"},
        {"home": "Atalanta", "away": "Fiorentina", "score": "1-0", "league": "Serie A"},
        {"home": "Montpellier", "away": "Strasbourg", "score": "1-0", "league": "Ligue 1"},
        {"home": "Eintracht Frankfurt", "away": "Union Berlin", "score": "2-0", "league": "Bundesliga"},
    ],
}

# ============================================================
# SESSION STATE - MATCHS PAR JOUR
# ============================================================

if "matchs_hier" not in st.session_state:
    st.session_state.matchs_hier = []

if "matchs_aujourdhui" not in st.session_state:
    st.session_state.matchs_aujourdhui = []

if "matchs_demain" not in st.session_state:
    st.session_state.matchs_demain = []

# ============================================================
# DATES
# ============================================================

DATE_HIER = get_date(-1)
DATE_AUJOURDHUI = get_date(0)
DATE_DEMAIN = get_date(1)

REF_HIER = get_date_reference(DATE_HIER)
REF_AUJOURDHUI = get_date_reference(DATE_AUJOURDHUI)
REF_DEMAIN = get_date_reference(DATE_DEMAIN)

# ============================================================
# HEADER
# ============================================================

st.markdown("""
<div style="text-align: center; padding: 20px; background: linear-gradient(135deg, #1e3c72, #2a5298); border-radius: 15px; margin-bottom: 20px;">
    <h1 style="color: white; margin: 0;">⚽ TVA &Co Prediction IA</h1>
    <p style="color: #ccc; margin: 10px 0 0 0;">Systeme de prediction base sur les correspondances historiques</p>
</div>
""", unsafe_allow_html=True)

# ============================================================
# NAVIGATION HIER / AUJOURD'HUI / DEMAIN
# ============================================================

col1, col2, col3 = st.columns(3)

with col1:
    btn_hier = st.button("📅 HIER\n" + DATE_HIER, use_container_width=True, type="secondary")

with col2:
    btn_aujourdhui = st.button("📍 AUJOURD'HUI\n" + DATE_AUJOURDHUI, use_container_width=True, type="primary")

with col3:
    btn_demain = st.button("🔮 DEMAIN\n" + DATE_DEMAIN, use_container_width=True, type="secondary")

# Gestion de la selection
if "jour_selectionne" not in st.session_state:
    st.session_state.jour_selectionne = "aujourdhui"

if btn_hier:
    st.session_state.jour_selectionne = "hier"
if btn_aujourdhui:
    st.session_state.jour_selectionne = "aujourdhui"
if btn_demain:
    st.session_state.jour_selectionne = "demain"

# Variables selon selection
if st.session_state.jour_selectionne == "hier":
    DATE_ACTIVE = DATE_HIER
    REF_ACTIVE = REF_HIER
    MATCHS_ACTIFS = st.session_state.matchs_hier
    TITRE_JOUR = "📅 HIER - " + DATE_HIER
elif st.session_state.jour_selectionne == "demain":
    DATE_ACTIVE = DATE_DEMAIN
    REF_ACTIVE = REF_DEMAIN
    MATCHS_ACTIFS = st.session_state.matchs_demain
    TITRE_JOUR = "🔮 DEMAIN - " + DATE_DEMAIN
else:
    DATE_ACTIVE = DATE_AUJOURDHUI
    REF_ACTIVE = REF_AUJOURDHUI
    MATCHS_ACTIFS = st.session_state.matchs_aujourdhui
    TITRE_JOUR = "📍 AUJOURD'HUI - " + DATE_AUJOURDHUI

st.markdown("---")

# ============================================================
# INFO DATES
# ============================================================

col1, col2, col3 = st.columns(3)

with col1:
    st.info("📅 Date selectionnee : **" + DATE_ACTIVE + "**")

with col2:
    st.warning("📆 Date reference : **" + REF_ACTIVE + "**")

with col3:
    if REF_ACTIVE in MATCHES_2022:
        st.success("✅ " + str(len(MATCHES_2022[REF_ACTIVE])) + " matchs en base 2022")
    else:
        st.error("❌ Pas de donnees pour cette date")

st.markdown("---")

# ============================================================
# DEUX COLONNES : SAISIE + PREDICTIONS
# ============================================================

col_gauche, col_droite = st.columns([1, 2])

# ============================================================
# COLONNE GAUCHE : SAISIE DES MATCHS
# ============================================================

with col_gauche:
    st.subheader("📝 Saisir les matchs")
    
    st.markdown("**Un match par ligne :**")
    st.markdown("`Equipe Dom - Equipe Ext`")
    
    exemple = """Real Madrid - Barcelona
Liverpool - Manchester City
PSG - Marseille
Bayern Munich - Dortmund"""
    
    # Zone de texte
    matchs_texte = st.text_area(
        "Matchs du " + DATE_ACTIVE,
        value="",
        height=200,
        placeholder=exemple,
        key="input_" + st.session_state.jour_selectionne
    )
    
    col_btn1, col_btn2 = st.columns(2)
    
    with col_btn1:
        if st.button("✅ Valider", type="primary", use_container_width=True):
            lignes = matchs_texte.strip().split("\n")
            nouveaux_matchs = []
            
            for ligne in lignes:
                ligne = ligne.strip()
                if not ligne:
                    continue
                    
                separateurs = [" - ", " vs ", " VS ", " contre ", " @ "]
                parts = None
                
                for sep in separateurs:
                    if sep in ligne:
                        parts = ligne.split(sep)
                        break
                
                if parts and len(parts) >= 2:
                    nouveaux_matchs.append({
                        "home": parts[0].strip(),
                        "away": parts[1].strip(),
                        "time": "20:00",
                        "league": ""
                    })
            
            # Sauvegarder selon le jour
            if st.session_state.jour_selectionne == "hier":
                st.session_state.matchs_hier = nouveaux_matchs
            elif st.session_state.jour_selectionne == "demain":
                st.session_state.matchs_demain = nouveaux_matchs
            else:
                st.session_state.matchs_aujourdhui = nouveaux_matchs
            
            st.success(str(len(nouveaux_matchs)) + " matchs!")
            st.rerun()
    
    with col_btn2:
        if st.button("🗑️ Effacer", use_container_width=True):
            if st.session_state.jour_selectionne == "hier":
                st.session_state.matchs_hier = []
            elif st.session_state.jour_selectionne == "demain":
                st.session_state.matchs_demain = []
            else:
                st.session_state.matchs_aujourdhui = []
            st.rerun()
    
    # Afficher matchs saisis
    matchs_affiches = []
    if st.session_state.jour_selectionne == "hier":
        matchs_affiches = st.session_state.matchs_hier
    elif st.session_state.jour_selectionne == "demain":
        matchs_affiches = st.session_state.matchs_demain
    else:
        matchs_affiches = st.session_state.matchs_aujourdhui
    
    if matchs_affiches:
        st.markdown("---")
        st.markdown("**📋 " + str(len(matchs_affiches)) + " matchs saisis :**")
        for m in matchs_affiches:
            st.write("• " + m["home"] + " vs " + m["away"])

# ============================================================
# COLONNE DROITE : PREDICTIONS
# ============================================================

with col_droite:
    st.subheader("🎯 Predictions - " + TITRE_JOUR)
    
    # Recuperer matchs selon jour
    if st.session_state.jour_selectionne == "hier":
        matchs_jour = st.session_state.matchs_hier
    elif st.session_state.jour_selectionne == "demain":
        matchs_jour = st.session_state.matchs_demain
    else:
        matchs_jour = st.session_state.matchs_aujourdhui
    
    matches_ref = MATCHES_2022.get(REF_ACTIVE, [])
    
    if not matchs_jour:
        st.warning("⚠️ Aucun match saisi pour ce jour")
        st.info("👈 Saisissez les matchs dans la zone de gauche")
        
    elif not matches_ref:
        st.error("❌ Pas de matchs de reference pour le " + REF_ACTIVE)
        st.markdown("**Dates disponibles en base :**")
        dates_dispo = sorted(MATCHES_2022.keys())
        st.write(", ".join(dates_dispo))
        
    else:
        # Afficher predictions
        for m_jour in matchs_jour:
            # Chercher correspondance pour equipe domicile
            ref_home, pos_home = find_match_reference(m_jour["home"], matches_ref)
            ref_away, pos_away = find_match_reference(m_jour["away"], matches_ref)
            
            match_ref = ref_home if ref_home else ref_away
            equipe_trouvee = m_jour["home"] if ref_home else (m_jour["away"] if ref_away else None)
            position = pos_home if ref_home else pos_away
            
            # Carte du match
            st.markdown("---")
            
            if match_ref:
                home_score, away_score = parse_score(match_ref["score"])
                analysis = analyze_match(home_score, away_score)
                
                # Header match
                st.markdown("### 🏟️ " + m_jour["home"] + " vs " + m_jour["away"])
                
                # Reference
                st.info("🔗 **" + equipe_trouvee + "** trouve en " + position + " le " + REF_ACTIVE + " : " + match_ref["home"] + " **" + match_ref["score"] + "** " + match_ref["away"])
                
                # Predictions en colonnes
                c1, c2, c3, c4, c5, c6 = st.columns(6)
                
                with c1:
                    st.metric("🎯 Score", analysis["score_exact"])
                    st.caption("@9.00")
                
                with c2:
                    st.metric("🏆 1X2", analysis["resultat_short"])
                    st.caption("@2.20")
                
                with c3:
                    ou25 = "O 2.5" if analysis["over_25"] else "U 2.5"
                    st.metric("⚽ O/U 2.5", ou25)
                    st.caption("@1.85")
                
                with c4:
                    ou15 = "O 1.5" if analysis["over_15"] else "U 1.5"
                    st.metric("⚽ O/U 1.5", ou15)
                    st.caption("@1.35")
                
                with c5:
                    btts = "Oui" if analysis["btts"] else "Non"
                    st.metric("👥 BTTS", btts)
                    st.caption("@1.80")
                
                with c6:
                    st.metric("📊 Buts ref", str(analysis["total_buts"]))
                
                # Combine
                cote_c = round(1.35 * 1.80, 2)
                st.success("🔥 **COMBINE** : Over 1.5 + BTTS = @" + str(cote_c))
                
            else:
                st.markdown("### ❓ " + m_jour["home"] + " vs " + m_jour["away"])
                st.warning("Aucune correspondance trouvee dans la base du " + REF_ACTIVE)

# ============================================================
# SECTION BASE 2022
# ============================================================

st.markdown("---")

with st.expander("📚 Voir la base de donnees 2022"):
    date_sel = st.selectbox("Date :", sorted(MATCHES_2022.keys(), reverse=True))
    
    st.markdown("### Matchs du " + date_sel)
    
    for m in MATCHES_2022[date_sel]:
        st.write("• " + m["home"] + " **" + m["score"] + "** " + m["away"] + " (" + m["league"] + ")")

# ============================================================
# FOOTER
# ============================================================

st.markdown("---")
st.caption("⚠️ Les paris sportifs comportent des risques. Jouez responsablement. | TVA &Co Prediction IA 2025")
