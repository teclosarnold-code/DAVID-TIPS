# app.py - TVA &Co Prediction IA - AVEC CHARGEMENT CSV

import streamlit as st
from datetime import datetime, timedelta
import pandas as pd

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
        score_str = str(score_str).strip()
        if "-" in score_str:
            parts = score_str.split("-")
        elif ":" in score_str:
            parts = score_str.split(":")
        else:
            return 0, 0
        return int(parts[0].strip()), int(parts[1].strip())
    except:
        return 0, 0

def analyze_match(home_score, away_score):
    total = home_score + away_score
    
    if home_score > away_score:
        result_short = "1"
    elif away_score > home_score:
        result_short = "2"
    else:
        result_short = "X"
    
    return {
        "score_exact": str(home_score) + "-" + str(away_score),
        "total_buts": total,
        "resultat_short": result_short,
        "over_15": total > 1.5,
        "over_25": total > 2.5,
        "over_35": total > 3.5,
        "btts": home_score > 0 and away_score > 0,
    }

def find_match_reference(equipe, matches_ref):
    equipe_lower = equipe.lower().strip()
    ignore = ["fc", "cf", "ac", "as", "us", "sc", "rc", "real", "sporting", "athletic", "atletico", "olympique", "paris", "saint", "club"]
    
    keywords = [w for w in equipe_lower.split() if len(w) > 3 and w not in ignore]
    
    for m_ref in matches_ref:
        ref_home = str(m_ref.get("home", "")).lower()
        ref_away = str(m_ref.get("away", "")).lower()
        
        for kw in keywords:
            if kw in ref_home:
                return m_ref, "domicile"
            if kw in ref_away:
                return m_ref, "exterieur"
    
    return None, None

# ============================================================
# SESSION STATE
# ============================================================

if "base_2022" not in st.session_state:
    st.session_state.base_2022 = {}

if "matchs_hier" not in st.session_state:
    st.session_state.matchs_hier = []

if "matchs_aujourdhui" not in st.session_state:
    st.session_state.matchs_aujourdhui = []

if "matchs_demain" not in st.session_state:
    st.session_state.matchs_demain = []

if "jour_selectionne" not in st.session_state:
    st.session_state.jour_selectionne = "aujourdhui"

# ============================================================
# DATES
# ============================================================

DATE_HIER = get_date(-1)
DATE_AUJOURDHUI = get_date(0)
DATE_DEMAIN = get_date(1)

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
# SIDEBAR - CHARGEMENT DES FICHIERS CSV
# ============================================================

with st.sidebar:
    st.header("📁 Chargement des donnees")
    
    # ========== BASE 2022-2023 ==========
    st.subheader("1️⃣ Base historique 2022-2023")
    
    st.markdown("""
    **Format CSV requis :**
    ```
    date,home,away,score,league
    29-09-2022,Real Madrid,Barcelona,3-1,La Liga
    ```
    """)
    
    fichier_2022 = st.file_uploader(
        "Charger CSV 2022-2023",
        type=["csv"],
        key="csv_2022"
    )
    
    if fichier_2022:
        try:
            df = pd.read_csv(fichier_2022)
            
            # Convertir en dictionnaire par date
            base = {}
            for idx, row in df.iterrows():
                date = str(row.get("date", "")).strip()
                
                # Normaliser le format de date
                for fmt in ["%d-%m-%Y", "%Y-%m-%d", "%d/%m/%Y"]:
                    try:
                        date_obj = datetime.strptime(date, fmt)
                        date = date_obj.strftime("%d-%m-%Y")
                        break
                    except:
                        continue
                
                if date not in base:
                    base[date] = []
                
                base[date].append({
                    "home": str(row.get("home", row.get("domicile", ""))).strip(),
                    "away": str(row.get("away", row.get("exterieur", ""))).strip(),
                    "score": str(row.get("score", row.get("scores", "0-0"))).strip(),
                    "league": str(row.get("league", row.get("ligue", ""))).strip()
                })
            
            st.session_state.base_2022 = base
            st.success("✅ " + str(len(df)) + " matchs charges!")
            st.info("📅 " + str(len(base)) + " dates differentes")
            
        except Exception as e:
            st.error("Erreur: " + str(e))
    
    # Stats base
    if st.session_state.base_2022:
        st.markdown("---")
        st.markdown("**📊 Base chargee :**")
        st.write("• " + str(len(st.session_state.base_2022)) + " dates")
        total_matchs = sum(len(m) for m in st.session_state.base_2022.values())
        st.write("• " + str(total_matchs) + " matchs")
    
    st.markdown("---")
    
    # ========== MATCHS DU JOUR ==========
    st.subheader("2️⃣ Matchs du jour (2025)")
    
    st.markdown("""
    **Format CSV :**
    ```
    home,away,time,league
    Real Madrid,Barcelona,21:00,La Liga
    ```
    """)
    
    fichier_jour = st.file_uploader(
        "Charger matchs du jour",
        type=["csv"],
        key="csv_jour"
    )
    
    if fichier_jour:
        try:
            df_jour = pd.read_csv(fichier_jour)
            matchs = []
            
            for idx, row in df_jour.iterrows():
                matchs.append({
                    "home": str(row.get("home", row.get("domicile", ""))).strip(),
                    "away": str(row.get("away", row.get("exterieur", ""))).strip(),
                    "time": str(row.get("time", row.get("heure", "20:00"))).strip(),
                    "league": str(row.get("league", row.get("ligue", ""))).strip()
                })
            
            st.session_state.matchs_aujourdhui = matchs
            st.success("✅ " + str(len(matchs)) + " matchs!")
            
        except Exception as e:
            st.error("Erreur: " + str(e))

# ============================================================
# NAVIGATION HIER / AUJOURD'HUI / DEMAIN
# ============================================================

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("📅 HIER\n" + DATE_HIER, use_container_width=True):
        st.session_state.jour_selectionne = "hier"

with col2:
    if st.button("📍 AUJOURD'HUI\n" + DATE_AUJOURDHUI, use_container_width=True, type="primary"):
        st.session_state.jour_selectionne = "aujourdhui"

with col3:
    if st.button("🔮 DEMAIN\n" + DATE_DEMAIN, use_container_width=True):
        st.session_state.jour_selectionne = "demain"

# Variables selon selection
if st.session_state.jour_selectionne == "hier":
    DATE_ACTIVE = DATE_HIER
    MATCHS_ACTIFS = st.session_state.matchs_hier
    TITRE_JOUR = "📅 HIER"
elif st.session_state.jour_selectionne == "demain":
    DATE_ACTIVE = DATE_DEMAIN
    MATCHS_ACTIFS = st.session_state.matchs_demain
    TITRE_JOUR = "🔮 DEMAIN"
else:
    DATE_ACTIVE = DATE_AUJOURDHUI
    MATCHS_ACTIFS = st.session_state.matchs_aujourdhui
    TITRE_JOUR = "📍 AUJOURD'HUI"

REF_ACTIVE = get_date_reference(DATE_ACTIVE)

st.markdown("---")

# ============================================================
# INFO DATES
# ============================================================

col1, col2, col3 = st.columns(3)

with col1:
    st.info("📅 " + TITRE_JOUR + " : **" + DATE_ACTIVE + "**")

with col2:
    st.warning("📆 Reference : **" + REF_ACTIVE + "**")

with col3:
    matchs_ref_count = len(st.session_state.base_2022.get(REF_ACTIVE, []))
    if matchs_ref_count > 0:
        st.success("✅ " + str(matchs_ref_count) + " matchs en base")
    else:
        st.error("❌ Pas de donnees")

st.markdown("---")

# ============================================================
# DEUX COLONNES
# ============================================================

col_gauche, col_droite = st.columns([1, 2])

# ============================================================
# COLONNE GAUCHE : SAISIE
# ============================================================

with col_gauche:
    st.subheader("📝 Saisir matchs " + TITRE_JOUR)
    
    st.markdown("**Format : Domicile - Exterieur**")
    
    matchs_texte = st.text_area(
        "Un match par ligne",
        height=200,
        placeholder="Real Madrid - Barcelona\nLiverpool - Man City\nPSG - Marseille",
        key="input_" + st.session_state.jour_selectionne
    )
    
    col_b1, col_b2 = st.columns(2)
    
    with col_b1:
        if st.button("✅ Valider", type="primary", use_container_width=True):
            lignes = matchs_texte.strip().split("\n")
            nouveaux = []
            
            for ligne in lignes:
                ligne = ligne.strip()
                if not ligne:
                    continue
                
                for sep in [" - ", " vs ", " VS ", "-", " contre "]:
                    if sep in ligne:
                        parts = ligne.split(sep, 1)
                        if len(parts) == 2:
                            nouveaux.append({
                                "home": parts[0].strip(),
                                "away": parts[1].strip(),
                                "time": "20:00",
                                "league": ""
                            })
                        break
            
            if st.session_state.jour_selectionne == "hier":
                st.session_state.matchs_hier = nouveaux
            elif st.session_state.jour_selectionne == "demain":
                st.session_state.matchs_demain = nouveaux
            else:
                st.session_state.matchs_aujourdhui = nouveaux
            
            st.rerun()
    
    with col_b2:
        if st.button("🗑️ Effacer", use_container_width=True):
            if st.session_state.jour_selectionne == "hier":
                st.session_state.matchs_hier = []
            elif st.session_state.jour_selectionne == "demain":
                st.session_state.matchs_demain = []
            else:
                st.session_state.matchs_aujourdhui = []
            st.rerun()
    
    # Liste des matchs saisis
    if st.session_state.jour_selectionne == "hier":
        liste = st.session_state.matchs_hier
    elif st.session_state.jour_selectionne == "demain":
        liste = st.session_state.matchs_demain
    else:
        liste = st.session_state.matchs_aujourdhui
    
    if liste:
        st.markdown("---")
        st.markdown("**" + str(len(liste)) + " matchs :**")
        for m in liste:
            st.write("• " + m["home"] + " vs " + m["away"])

# ============================================================
# COLONNE DROITE : PREDICTIONS
# ============================================================

with col_droite:
    st.subheader("🎯 Predictions " + TITRE_JOUR + " - " + DATE_ACTIVE)
    
    # Recuperer matchs
    if st.session_state.jour_selectionne == "hier":
        matchs_jour = st.session_state.matchs_hier
    elif st.session_state.jour_selectionne == "demain":
        matchs_jour = st.session_state.matchs_demain
    else:
        matchs_jour = st.session_state.matchs_aujourdhui
    
    matches_ref = st.session_state.base_2022.get(REF_ACTIVE, [])
    
    if not st.session_state.base_2022:
        st.error("❌ Aucune base 2022 chargee!")
        st.info("👈 Chargez votre fichier CSV dans le menu a gauche")
        
    elif not matchs_jour:
        st.warning("⚠️ Aucun match saisi")
        st.info("👈 Saisissez les matchs ou chargez un CSV")
        
    elif not matches_ref:
        st.error("❌ Pas de matchs en base pour le " + REF_ACTIVE)
        
        # Dates proches
        st.markdown("**Dates disponibles proches :**")
        dates_base = sorted(st.session_state.base_2022.keys())
        for d in dates_base[:10]:
            st.write("• " + d + " (" + str(len(st.session_state.base_2022[d])) + " matchs)")
        
    else:
        # PREDICTIONS
        for m_jour in matchs_jour:
            ref_found, position = find_match_reference(m_jour["home"], matches_ref)
            
            if not ref_found:
                ref_found, position = find_match_reference(m_jour["away"], matches_ref)
            
            st.markdown("---")
            
            if ref_found:
                home_score, away_score = parse_score(ref_found["score"])
                analysis = analyze_match(home_score, away_score)
                
                st.markdown("### 🏟️ " + m_jour["home"] + " vs " + m_jour["away"])
                
                st.info("🔗 Reference " + REF_ACTIVE + " : " + ref_found["home"] + " **" + ref_found["score"] + "** " + ref_found["away"])
                
                # Predictions
                c1, c2, c3, c4, c5, c6 = st.columns(6)
                
                with c1:
                    st.metric("🎯 Score", analysis["score_exact"])
                    st.caption("@9.00")
                
                with c2:
                    st.metric("🏆 1X2", analysis["resultat_short"])
                    st.caption("@2.20")
                
                with c3:
                    st.metric("⚽ O/U 2.5", "O 2.5" if analysis["over_25"] else "U 2.5")
                    st.caption("@1.85")
                
                with c4:
                    st.metric("⚽ O/U 1.5", "O 1.5" if analysis["over_15"] else "U 1.5")
                    st.caption("@1.35")
                
                with c5:
                    st.metric("👥 BTTS", "Oui" if analysis["btts"] else "Non")
                    st.caption("@1.80")
                
                with c6:
                    st.metric("📊 Total", str(analysis["total_buts"]))
                
                st.success("🔥 COMBINE : Over 1.5 + BTTS = @" + str(round(1.35 * 1.80, 2)))
                
            else:
                st.markdown("### ❓ " + m_jour["home"] + " vs " + m_jour["away"])
                st.warning("Pas de correspondance trouvee")

# ============================================================
# FOOTER
# ============================================================

st.markdown("---")
st.caption("⚠️ Les paris comportent des risques. Jouez responsablement. | TVA &Co 2025")
