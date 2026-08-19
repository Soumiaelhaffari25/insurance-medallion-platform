import streamlit as st
import pandas as pd
import plotly.express as px
import snowflake.connector

st.set_page_config(page_title="Insurance Risk Analytics", page_icon="📊", layout="wide")

# ---------- Palette pastel ----------
ROSE, BLEU, VIOLET = "#E89BB8", "#8FB8E8", "#B49BE8"
TXT = "#4A3A5E"
SCALE = [[0, BLEU], [0.5, VIOLET], [1, ROSE]]          # bleu -> violet -> rose
SCALE_DIV = [[0, "#8FD9B8"], [0.5, "#E8D0A6"], [1, ROSE]]  # vert -> jaune -> rose (rentabilite)

st.markdown(f"""
<style>
  .stApp {{ background: #FBF6FF; color: {TXT}; }}
  h1 {{ color: #6B4E9E !important; font-weight: 700; }}
  h2, h3 {{ color: #7B5EAE !important; }}
  p, span, label, div, li {{ color: {TXT}; }}
  [data-testid="stMetric"] {{ background: white; border-radius: 16px; padding: 14px;
    box-shadow: 0 4px 14px rgba(180,155,232,0.22); border: 1px solid #EAD9F7; }}
  [data-testid="stMetricLabel"] p {{ color: #7B5EAE !important; font-weight: 600; }}
  [data-testid="stMetricValue"] {{ color: #8B5FBF !important; }}
  section[data-testid="stSidebar"] {{ background: #F6EEFB; }}
  section[data-testid="stSidebar"] * {{ color: {TXT} !important; }}
  .subtitle {{ color: #8B5FBF; font-size: 1.12em; margin-bottom: 6px; }}
  .narratif {{ background: white; border-left: 5px solid {ROSE}; padding: 13px 18px;
    border-radius: 10px; margin: 8px 0 16px 0; box-shadow: 0 2px 8px rgba(232,155,184,0.15); color: {TXT}; }}
  .narratif b {{ color: #7B5EAE; }}
  div[role="radiogroup"] label {{ background: white; border: 1px solid #EAD9F7; border-radius: 10px;
    padding: 8px 16px; margin-right: 8px; color: {TXT} !important; box-shadow: 0 2px 6px rgba(180,155,232,0.15); }}
</style>
""", unsafe_allow_html=True)

@st.cache_resource
def get_connection():
    c = st.secrets["snowflake"]
    return snowflake.connector.connect(account=c["account"], user=c["user"], password=c["password"],
        warehouse=c["warehouse"], database=c["database"], schema=c["schema"], role=c["role"])

@st.cache_data(ttl=600)
def load_data():
    q = """
        SELECT f.id_pol, f.exposure, f.claim_count, f.claim_amount, f.earned_premium,
               p.driver_age, p.bonus_malus, v.brand AS veh_brand, v.power AS veh_power,
               v.fuel_type AS veh_gas, r.region, r.area, r.density
        FROM INSURANCE.GOLD.FCT_RISK_METRICS f
        JOIN INSURANCE.GOLD.DIM_POLICYHOLDER p ON f.policyholder_key = p.policyholder_key
        JOIN INSURANCE.GOLD.DIM_VEHICLE v ON f.vehicle_key = v.vehicle_key
        JOIN INSURANCE.GOLD.DIM_REGION r ON f.region_key = r.region_key
    """
    df = pd.read_sql(q, get_connection())
    df.columns = [c.lower() for c in df.columns]
    df["tranche_age"] = df["driver_age"].apply(lambda a: "18-24" if a<25 else "25-34" if a<35
        else "35-49" if a<50 else "50-64" if a<65 else "65+")
    df["tranche_bm"] = pd.cut(df["bonus_malus"], bins=[49,60,80,100,150,400],
        labels=["50-60","60-80","80-100","100-150","150+"])
    return df

def lr(d): return d["claim_amount"].sum()/d["earned_premium"].sum() if d["earned_premium"].sum() else 0
def fr(d): return d["claim_count"].sum()/d["exposure"].sum() if d["exposure"].sum() else 0
def sv(d): return d["claim_amount"].sum()/d["claim_count"].sum() if d["claim_count"].sum() else 0

def seg_metrics(d, col):
    """Loss ratio, frequence, severite, exposition, primes, sinistres par segment."""
    g = d.groupby(col).agg(
        expo=("exposure","sum"), primes=("earned_premium","sum"),
        sin=("claim_amount","sum"), nsin=("claim_count","sum"), n=("id_pol","nunique")).reset_index()
    g["loss_ratio"] = g["sin"]/g["primes"]
    g["frequence"]  = g["nsin"]/g["expo"]
    g["severite"]   = g["sin"]/g["nsin"].replace(0, pd.NA)
    return g

def style_fig(fig, h=None):
    fig.update_layout(plot_bgcolor="white", paper_bgcolor="white",
        font=dict(family="Segoe UI", color=TXT, size=13), margin=dict(t=30,l=10,r=10,b=10))
    if h: fig.update_layout(height=h)
    fig.update_xaxes(gridcolor="#F0E6FA"); fig.update_yaxes(gridcolor="#F0E6FA")
    return fig

# ---------- Header ----------
st.title("Insurance Risk Analytics")
st.markdown("<p class='subtitle'>De la santé du portefeuille à la décision de tarification — "
            "analyse du risque en assurance automobile.</p>", unsafe_allow_html=True)

with st.spinner("Connexion à Snowflake..."):
    df = load_data()

# ---------- Filtres communs ----------
st.sidebar.header("Filtres")
f_reg  = st.sidebar.multiselect("Région", sorted(df["region"].unique()))
f_age  = st.sidebar.multiselect("Tranche d'âge", ["18-24","25-34","35-49","50-64","65+"])
f_veh  = st.sidebar.multiselect("Marque véhicule", sorted(df["veh_brand"].unique()))
dff = df.copy()
if f_reg: dff = dff[dff["region"].isin(f_reg)]
if f_age: dff = dff[dff["tranche_age"].isin(f_age)]
if f_veh: dff = dff[dff["veh_brand"].isin(f_veh)]
st.sidebar.divider()
st.sidebar.caption(f"{dff['id_pol'].nunique():,} polices · {dff['exposure'].sum():,.0f} années d'exposition")
st.sidebar.caption("Source : Snowflake · couche Gold")

vue = st.radio("nav", ["Vue d'ensemble", "Analyse du risque", "Rentabilité & tarification"],
               horizontal=True, label_visibility="collapsed")
st.divider()

# ================= VUE 1 — EXECUTIVE OVERVIEW =================
if vue == "Vue d'ensemble":
    st.markdown("<div class='narratif'><b>Santé globale du portefeuille.</b> Une photo d'ensemble : "
                "volume, exposition, et rentabilité agrégée. Le <b>loss ratio</b> (sinistres ÷ primes) "
                "au-dessus de 1 signale un déséquilibre technique.</div>", unsafe_allow_html=True)

    c1,c2,c3 = st.columns(3)
    c1.metric("Contrats", f"{dff['id_pol'].nunique():,}")
    c2.metric("Exposition (années-contrat)", f"{dff['exposure'].sum():,.0f}")
    c3.metric("Loss Ratio global", f"{lr(dff):.1%}")
    c4,c5 = st.columns(2)
    c4.metric("Fréquence moyenne", f"{fr(dff):.3f}")
    c5.metric("Sévérité moyenne", f"{sv(dff):,.0f} €")
    st.divider()

    g1, g2 = st.columns(2)
    with g1:
        st.subheader("Loss Ratio par région")
        d = seg_metrics(dff, "region").sort_values("loss_ratio", ascending=False)
        fig = px.bar(d, x="loss_ratio", y="region", orientation="h", color="loss_ratio",
                     color_continuous_scale=SCALE)
        fig.add_vline(x=1, line_dash="dash", line_color=ROSE)
        fig.update_layout(yaxis={"categoryorder":"total ascending"})
        st.plotly_chart(style_fig(fig, 480), use_container_width=True)
    with g2:
        st.subheader("Répartition de l'exposition par région")
        d = seg_metrics(dff, "region").sort_values("expo", ascending=False)
        fig = px.treemap(d, path=["region"], values="expo", color="loss_ratio",
                         color_continuous_scale=SCALE)
        st.plotly_chart(style_fig(fig, 480), use_container_width=True)

    st.subheader("Structure démographique — contrats par tranche d'âge")
    d = dff.groupby("tranche_age")["id_pol"].nunique().reset_index(name="contrats")
    fig = px.bar(d, x="tranche_age", y="contrats", color="contrats", color_continuous_scale=[[0,BLEU],[1,VIOLET]])
    st.plotly_chart(style_fig(fig, 300), use_container_width=True)

# ================= VUE 2 — RISK ANALYSIS =================
elif vue == "Analyse du risque":
    st.markdown("<div class='narratif'><b>Décomposer le risque technique.</b> Le loss ratio se décompose "
                "en <b>fréquence</b> (nombre de sinistres par unité d'exposition) et <b>sévérité</b> "
                "(coût moyen d'un sinistre). Croiser les facteurs révèle où le risque se concentre.</div>",
                unsafe_allow_html=True)

    g1, g2 = st.columns(2)
    with g1:
        st.subheader("Fréquence par tranche d'âge")
        d = seg_metrics(dff, "tranche_age").sort_values("frequence", ascending=False)
        fig = px.bar(d, x="frequence", y="tranche_age", orientation="h", color="frequence",
                     color_continuous_scale=[[0,BLEU],[1,ROSE]])
        fig.update_layout(yaxis={"categoryorder":"total ascending"})
        st.plotly_chart(style_fig(fig, 360), use_container_width=True)
    with g2:
        st.subheader("Sévérité par marque de véhicule")
        d = seg_metrics(dff, "veh_brand").sort_values("severite", ascending=False).head(12)
        fig = px.bar(d, x="severite", y="veh_brand", orientation="h", color="severite",
                     color_continuous_scale=[[0,BLEU],[1,VIOLET]])
        fig.update_layout(yaxis={"categoryorder":"total ascending"})
        st.plotly_chart(style_fig(fig, 360), use_container_width=True)

    st.subheader("Concentration du risque — âge × bonus-malus (fréquence)")
    h = dff.groupby(["tranche_age","tranche_bm"]).apply(fr).reset_index(name="frequence")
    fig = px.density_heatmap(h, x="tranche_age", y="tranche_bm", z="frequence",
                             color_continuous_scale=SCALE, text_auto=".3f", histfunc="avg")
    fig.update_coloraxes(colorbar_title="Fréquence")
    st.plotly_chart(style_fig(fig, 380), use_container_width=True)

    st.subheader("Fréquence vs Sévérité par segment d'âge (taille = exposition)")
    s = seg_metrics(dff, "tranche_age")
    fig = px.scatter(s, x="frequence", y="severite", size="expo", color="loss_ratio",
                     color_continuous_scale=SCALE, text="tranche_age", size_max=70)
    fig.update_traces(textposition="top center")
    st.plotly_chart(style_fig(fig, 420), use_container_width=True)
    st.markdown("<div class='narratif'>Les segments en haut à droite cumulent <b>fréquence et sévérité "
                "élevées</b> : ce sont les profils les plus coûteux à couvrir.</div>", unsafe_allow_html=True)

# ================= VUE 3 — PROFITABILITY =================
else:
    st.markdown("<div class='narratif'><b>Rentabilité par segment — le cœur décisionnel.</b> "
                "On identifie les segments à re-tarifer : loss ratio au-dessus de 1 = déficitaire. "
                "Le croisement volume × rentabilité priorise les actions.</div>", unsafe_allow_html=True)

    st.subheader("Loss Ratio par tranche d'âge — rentable vs déficitaire")
    d = seg_metrics(dff, "tranche_age").sort_values("loss_ratio", ascending=False)
    fig = px.bar(d, x="loss_ratio", y="tranche_age", orientation="h", color="loss_ratio",
                 color_continuous_scale=SCALE_DIV)
    fig.add_vline(x=1, line_dash="dash", line_color=ROSE, annotation_text="Seuil rentabilité")
    fig.update_layout(yaxis={"categoryorder":"total ascending"})
    st.plotly_chart(style_fig(fig, 340), use_container_width=True)

    # --- Priorisation en pleine largeur ---
    st.subheader("Priorisation — volume vs rentabilité")
    d = seg_metrics(dff, "region")
    fig = px.scatter(d, x="loss_ratio", y="primes", size="sin", color="loss_ratio",
                     color_continuous_scale=SCALE_DIV, text="region", size_max=60)
    fig.add_vline(x=1, line_dash="dash", line_color=ROSE)
    fig.update_traces(textposition="top center")
    fig.update_layout(xaxis_title="Loss Ratio", yaxis_title="Primes (€)")
    st.plotly_chart(style_fig(fig, 440), use_container_width=True)

    # --- Détail par segment, en dessous, pleine largeur ---
    st.subheader("Détail par segment")
    d = seg_metrics(dff, "tranche_age")[["tranche_age","expo","primes","sin","frequence","severite"]]
    d.columns = ["Âge","Exposition","Primes","Sinistres","Fréq.","Sévérité"]
    st.dataframe(d.style.format({"Exposition":"{:,.0f}","Primes":"{:,.0f}","Sinistres":"{:,.0f}",
        "Fréq.":"{:.3f}","Sévérité":"{:,.0f}"}),
        use_container_width=True, hide_index=True,
        height=(len(d) + 1) * 35 + 3
    )

    st.markdown("<div class='narratif'><b>Note méthodologique.</b> Le loss ratio repose sur une "
                "<b>prime pure modélisée</b> (fréquence portefeuille × sévérité × exposition, chargée de 20 %), "
                "et non sur une prime commerciale réelle absente de freMTPL2. Les niveaux absolus sont donc "
                "indicatifs ; ce sont les <b>écarts entre segments</b> qui portent l'information décisionnelle.</div>",
                unsafe_allow_html=True)