import streamlit as st
import pandas as pd
import numpy as np
import joblib
import json
import networkx as nx
import plotly.graph_objects as go
import os

# ── PAGE CONFIG ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="SaludMapper · INMEGEN",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ── CSS ────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600&family=JetBrains+Mono:wght@400;500&display=swap');

:root {
    --bg:       #f7f5f0;
    --surface:  #ffffff;
    --border:   #e2ddd6;
    --ink:      #1a1814;
    --muted:    #8a8478;
    --accent:   #2d6a4f;
    --accent2:  #95d5b2;
    --warn:     #d4860a;
    --danger:   #c0392b;
    --ok:       #2d6a4f;
    --tag-bg:   #e8f5ee;
}
html, body, [data-testid="stAppViewContainer"] {
    background: var(--bg) !important;
    color: var(--ink) !important;
    font-family: 'Outfit', sans-serif;
}
[data-testid="stHeader"] { background: transparent !important; }
[data-testid="stSidebar"] { display: none; }

.app-header {
    display: flex; align-items: baseline; gap: 1rem;
    padding: 2rem 0 0.5rem 0;
    border-bottom: 2px solid var(--ink);
    margin-bottom: 2rem;
}
.app-header h1 {
    font-family: 'Outfit', sans-serif; font-weight: 600;
    font-size: 1.9rem; color: var(--ink); margin: 0; letter-spacing: -0.5px;
}
.app-header .sub {
    font-family: 'JetBrains Mono', monospace; font-size: 0.72rem;
    color: var(--muted); letter-spacing: 1px; text-transform: uppercase;
}
.sec-label {
    font-family: 'JetBrains Mono', monospace; font-size: 0.65rem;
    letter-spacing: 2.5px; text-transform: uppercase; color: var(--accent);
    margin-bottom: 0.8rem; display: flex; align-items: center; gap: 0.5rem;
}
.sec-label::after { content:''; flex:1; height:1px; background:var(--border); }

.score-wrap {
    display: flex; flex-direction: column; align-items: center; padding: 1.5rem 0;
}
.score-number {
    font-family: 'Outfit', sans-serif; font-weight: 600;
    font-size: 4rem; line-height: 1;
}
.score-denom { font-size: 1.4rem; color: var(--muted); font-weight: 300; }
.score-label {
    font-family: 'JetBrains Mono', monospace; font-size: 0.7rem;
    letter-spacing: 2px; text-transform: uppercase; color: var(--muted); margin-top: 0.3rem;
}
.habit-row {
    display: flex; align-items: center; gap: 0.8rem; margin-bottom: 0.55rem;
}
.habit-name { font-size: 0.82rem; color: var(--ink); width: 155px; flex-shrink: 0; }
.habit-bar-bg {
    flex: 1; height: 6px; background: var(--border); border-radius: 3px; overflow: hidden;
}
.bar-ok   { height:100%; width:100%; background:var(--accent); border-radius:3px; }
.bar-fail { height:100%; width:0%;   background:var(--border); border-radius:3px; }
.tag-ok   { font-family:'JetBrains Mono',monospace; font-size:0.65rem;
            color:var(--ok); background:var(--tag-bg);
            padding:0.1rem 0.4rem; border-radius:3px; }
.tag-fail { font-family:'JetBrains Mono',monospace; font-size:0.65rem;
            color:var(--muted); background:var(--border);
            padding:0.1rem 0.4rem; border-radius:3px; }

.perfil-badge {
    display:inline-block; font-family:'JetBrains Mono',monospace;
    font-size:0.7rem; letter-spacing:1px; text-transform:uppercase;
    padding:0.3rem 0.8rem; border-radius:4px; border:1px solid var(--accent);
    color:var(--accent); background:var(--tag-bg); margin-bottom:1rem;
}
.topo-meta {
    background:var(--tag-bg); border:1px solid var(--accent2);
    border-radius:8px; padding:1rem 1.2rem; margin-bottom:1.2rem; font-size:0.85rem;
}
.topo-meta strong { color:var(--accent); }
.recom-item {
    display:flex; gap:1rem; align-items:flex-start;
    padding:0.8rem 0; border-bottom:1px solid var(--border);
}
.recom-item:last-child { border-bottom:none; }
.recom-num {
    font-family:'Outfit',sans-serif; font-weight:600;
    font-size:1.4rem; color:var(--accent); line-height:1.2;
    width:1.8rem; flex-shrink:0;
}
.recom-text { font-size:0.9rem; line-height:1.5; }
.recom-pct  { font-family:'JetBrains Mono',monospace; font-size:0.7rem; color:var(--muted); margin-top:0.2rem; }
.riesgo-dot { width:12px; height:12px; border-radius:50%; display:inline-block; margin-right:4px; }

div[data-testid="stNumberInput"] label,
div[data-testid="stSelectbox"] label,
div[data-testid="stCheckbox"] label p,
div[data-testid="stRadio"] label p {
    font-size:0.82rem !important; color:var(--muted) !important;
    font-family:'JetBrains Mono',monospace !important;
}
div[data-testid="stNumberInput"] input {
    background:var(--bg) !important; border:1px solid var(--border) !important;
    border-radius:6px !important; color:var(--ink) !important;
    font-family:'Outfit',sans-serif !important;
}
button[kind="primaryFormSubmit"] {
    background:var(--accent) !important; color:white !important;
    border:none !important; font-family:'Outfit',sans-serif !important;
    font-weight:500 !important; border-radius:8px !important;
    font-size:0.95rem !important; padding:0.6rem 2rem !important;
}
div[data-testid="stForm"] {
    background:var(--surface) !important; border:1px solid var(--border) !important;
    border-radius:12px !important; padding:1.5rem !important;
}
</style>
""", unsafe_allow_html=True)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# ── CARGAR ACTIVOS ─────────────────────────────────────────────────────────────

@st.cache_resource
def cargar_activos():
    df_data  = pd.read_csv(os.path.join(BASE_DIR, 'df_active_habitos.csv'), index_col=0)
    df_nodes = pd.read_csv(os.path.join(BASE_DIR, 'nodos_stats_habitos.csv'))

    with open(os.path.join(BASE_DIR, 'grafo_adyacencia.json'), 'r') as f:
        datos_grafo = json.load(f)
    if 'links' not in datos_grafo and 'edges' in datos_grafo:
        datos_grafo['links'] = datos_grafo.pop('edges')
    if 'links' not in datos_grafo:
        datos_grafo['links'] = []
    try:
        G_topo = nx.node_link_graph(datos_grafo)
    except Exception:
        G_topo = nx.node_link_graph(
            datos_grafo,
            attrs={'source':'source','target':'target',
                   'name':'id','key':'key','link':'links'}
        )
    meta = {}
    try:
        meta = joblib.load(os.path.join(BASE_DIR, 'metadata.pkl'))
    except FileNotFoundError:
        pass
    return df_data, df_nodes, G_topo, meta

try:
    metadata, df_data, df_nodes, G_topo = cargar_activos()
    p33 = metadata['p33']
    p66 = metadata['p66']
except Exception as e:
    st.error(f"Error cargando archivos: {e}")
    st.info("Necesitas: metadata.pkl · df_active_habitos.csv · nodos_stats_habitos.csv · grafo_adyacencia.json")
    st.stop()

# ── DEFINICIÓN DE COMPONENTES ──────────────────────────────────────────────────
COMPONENTES = {
    's_IMC':          ('IMC saludable',          'Alcanza un peso corporal en rango saludable (18.5–24.9 kg/m²)'),
    's_CINTURA':      ('Cintura en rango',        'Reduce grasa abdominal: <102cm hombres, <88cm mujeres'),
    's_TG':           ('Triglicéridos < 150',     'Reduce azúcares simples; aumenta actividad física aeróbica'),
    's_HDL':          ('HDL adecuado',            'Ejercicio aeróbico regular y grasas saludables (omega-3, aguacate)'),
    's_GLU':          ('Glucosa < 100',           'Controla carbohidratos refinados; mantén actividad física constante'),
    's_AZUCAR':       ('Azúcar añadida ≤ 2 cdas', 'Elimina refrescos y dulces; usa edulcorantes naturales con moderación'),
    's_SAL':          ('Sin sal extra',           'Usa hierbas aromáticas; evita el salero en la mesa'),
    's_SEDENTARISMO': ('Sedentarismo ≤ 3.5 días', 'Camina mínimo 30 min/día, al menos 4 días a la semana'),
}

# ── LÓGICA DE SCORES ───────────────────────────────────────────────────────────
def calcular_scores(d):
    s = {
        's_IMC':          int(18.5 <= d['IMC'] < 25),
        's_CINTURA':      int((d['Sx']==1 and d['CINTURA_CM']<102) or (d['Sx']==2 and d['CINTURA_CM']<88)),
        's_TG':           int(d['tg'] < 150),
        's_HDL':          int((d['Sx']==1 and d['hdlc']>40) or (d['Sx']==2 and d['hdlc']>50)),
        's_GLU':          int(d['glu'] < 100),
        's_AZUCAR':       int(d['azucar'] <= 2),
        's_SAL':          int(d['sal'] == 0),
        's_SEDENTARISMO': int(d['dias_sed'] <= 3.5),
    }
    score_hab  = sum(s.values())
    riesgo_cli = min(3.0, d['HTA'] + d['DM'] * 1.5)
    if   d['HTA'] and d['DM']:  perfil = 'HTA_y_DM'
    elif d['HTA']:               perfil = 'Solo_HTA'
    elif d['DM']:                perfil = 'Solo_DM'
    else:                        perfil = 'Sin_diagnostico'
    return s, score_hab, riesgo_cli, perfil

# ── RUTA TOPOLÓGICA ────────────────────────────────────────────────────────────
def ruta_topologica(perfil, score_actual, s_pac, df_nodes):
    # 1. Candidatos: mismo perfil diagnóstico con score mayor al actual
    cands = df_nodes[
        (df_nodes['perfil_predominante'] == perfil) &
        (df_nodes['score_habitos_avg']   >  score_actual)
    ].copy()

    # Fallback: si no hay candidatos del mismo perfil, buscar en todos
    if cands.empty:
        cands = df_nodes[df_nodes['score_habitos_avg'] > score_actual].copy()

    if cands.empty:
        return None, 0, []

    # 2. Nodo destino = mayor score de hábitos en candidatos
    nodo_dest = cands.loc[cands['score_habitos_avg'].idxmax()]

    # 3. Brechas por componente
    brechas = []
    for s_col, (nombre, consejo) in COMPONENTES.items():
        if s_col not in nodo_dest.index:
            continue
        pct_dest = float(nodo_dest[s_col])
        val_pac  = s_pac.get(s_col, 0)
        # Recomendar solo si el paciente falla y el nodo destino cumple >60%
        if val_pac == 0 and pct_dest > 0.60:
            brechas.append({
                'nombre':   nombre,
                'consejo':  consejo,
                'pct':      pct_dest,
            })

    brechas.sort(key=lambda x: x['pct'], reverse=True)
    return nodo_dest, len(cands), brechas

# ── HEADER ─────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="app-header">
  <h1>🧬 SaludMapper</h1>
  <span class="sub">INMEGEN · Navegación Topológica de Perfiles Metabólicos</span>
</div>
""", unsafe_allow_html=True)

col_form, col_res = st.columns([1, 1.2], gap="large")

# ── FORMULARIO ─────────────────────────────────────────────────────────────────
with col_form:
    st.markdown('<div class="sec-label">Datos del paciente</div>', unsafe_allow_html=True)
    with st.form("form_paciente"):

        st.markdown("**Diagnósticos y generales**")
        g1, g2 = st.columns(2)
        with g1:
            hta  = st.checkbox("Hipertensión diagnosticada", value=False)
            dm   = st.checkbox("Diabetes diagnosticada",     value=False)
        with g2:
            sx   = st.radio("Sexo", [1,2],
                            format_func=lambda x:"♂ Hombre" if x==1 else "♀ Mujer",
                            horizontal=True)
            edad = st.number_input("Edad (años)", 60, 100, 70)

        st.markdown("---")
        st.markdown("**Biometría y laboratorio**")
        b1, b2 = st.columns(2)
        with b1:
            imc     = st.number_input("IMC (kg/m²)",              13.0, 57.0,  28.0, 0.1)
            cintura = st.number_input("Cintura (cm)",              50.0,140.0,  96.0, 0.5)
            glu     = st.number_input("Glucosa en ayunas (mg/dL)", 50.0,500.0, 110.0)
        with b2:
            tg   = st.number_input("Triglicéridos (mg/dL)", 45.0, 500.0, 160.0)
            hdlc = st.number_input("HDL (mg/dL)",           20.0, 100.0,  48.0)

        st.markdown("---")
        st.markdown("**Hábitos**")
        h1, h2 = st.columns(2)
        with h1:
            dias_sed = st.selectbox(
                "Días sedentarios/semana", [0.0, 1.5, 3.5, 6.0], index=3,
                format_func=lambda x:{0:"Nunca",1.5:"1-2 días",3.5:"3-4 días",6.0:"5-7 días"}[x]
            )
            azucar = st.number_input("Cucharadas azúcar añadida/día", 0.0, 10.0, 2.0, 0.5)
        with h2:
            sal = st.checkbox("Agrega sal antes de probar", value=False)

        st.markdown("")
        submitted = st.form_submit_button("→  Calcular perfil y ruta de salud",
                                          use_container_width=True)

# ── RESULTADOS ─────────────────────────────────────────────────────────────────
with col_res:
    if not submitted:
        st.markdown("""
        <div style="height:420px;display:flex;align-items:center;justify-content:center;
                    border:1px dashed #e2ddd6;border-radius:12px;margin-top:3rem;">
          <p style="color:#8a8478;font-family:'JetBrains Mono',monospace;
                    font-size:0.8rem;letter-spacing:1px;text-align:center;">
            Completa el formulario<br>y presiona el botón
          </p>
        </div>
        """, unsafe_allow_html=True)
    else:
        datos = {
            'HTA': int(hta), 'DM': int(dm), 'Sx': sx,
            'IMC': imc, 'CINTURA_CM': cintura,
            'glu': glu, 'tg': tg, 'hdlc': hdlc,
            'azucar': azucar, 'sal': int(sal), 'dias_sed': dias_sed,
        }
        s_pac, score_hab, riesgo_cli, perfil = calcular_scores(datos)

        # ── Score de hábitos ───────────────────────────────────────────────────
        st.markdown('<div class="sec-label">Score de hábitos</div>', unsafe_allow_html=True)
        sc1, sc2 = st.columns([1, 2])

        color_score = "#2d6a4f" if score_hab >= 6 else "#d4860a" if score_hab >= 4 else "#c0392b"
        with sc1:
            st.markdown(f"""
            <div class="score-wrap">
              <div>
                <span class="score-number" style="color:{color_score};">{score_hab}</span>
                <span class="score-denom">/8</span>
              </div>
              <div class="score-label">score de hábitos</div>
            </div>
            """, unsafe_allow_html=True)

        with sc2:
            for s_col, (nombre, _) in COMPONENTES.items():
                val  = s_pac.get(s_col, 0)
                tag  = '<span class="tag-ok">✓</span>' if val else '<span class="tag-fail">✗</span>'
                bar  = 'bar-ok' if val else 'bar-fail'
                st.markdown(f"""
                <div class="habit-row">
                  <span class="habit-name">{nombre}</span>
                  <div class="habit-bar-bg"><div class="{bar}"></div></div>
                  {tag}
                </div>
                """, unsafe_allow_html=True)

        # ── Perfil diagnóstico ─────────────────────────────────────────────────
        st.markdown('<div class="sec-label" style="margin-top:1.2rem;">Perfil clínico</div>',
                    unsafe_allow_html=True)

        PERFIL_META = {
            'Sin_diagnostico': ('Sin diagnóstico crónico', '#2d6a4f'),
            'Solo_HTA':        ('Hipertensión',            '#d4860a'),
            'Solo_DM':         ('Diabetes',                '#d4860a'),
            'HTA_y_DM':        ('Hipertensión + Diabetes', '#c0392b'),
        }
        p_label, p_color = PERFIL_META[perfil]
        n_dots = int(round(riesgo_cli))
        dots_html = "".join([
            f'<span class="riesgo-dot" style="background:{p_color if i < n_dots else "#e2ddd6"};"></span>'
            for i in range(3)
        ])
        st.markdown(f"""
        <span class="perfil-badge" style="border-color:{p_color};color:{p_color};background:{p_color}18;">
          {p_label}
        </span>
        <div style="font-size:0.8rem;color:#8a8478;font-family:'JetBrains Mono',monospace;margin-bottom:1rem;">
          {dots_html} Carga clínica: {riesgo_cli:.1f} / 3.0
        </div>
        """, unsafe_allow_html=True)

        # ── Ruta topológica ───────────────────────────────────────────────────
        st.markdown('<div class="sec-label">Ruta topológica de mejora</div>',
                    unsafe_allow_html=True)

        nodo_dest, n_cands, brechas = ruta_topologica(perfil, score_hab, s_pac, df_nodes)

        if nodo_dest is None:
            st.markdown(f"""
            <div class="topo-meta">
              <strong>Tu score de {score_hab}/8 ya es el más alto en tu grupo.</strong><br>
              Pacientes con tu mismo perfil clínico no superan este nivel. ¡Mantén tus hábitos!
            </div>
            """, unsafe_allow_html=True)
        else:
            meta = float(nodo_dest['score_habitos_avg'])
            st.markdown(f"""
            <div class="topo-meta">
              Pacientes con tu mismo perfil <strong>({p_label})</strong> han alcanzado
              un score de <strong>{meta:.1f}/8</strong>.
              Tu brecha actual es de <strong>{meta - score_hab:.1f} punto(s)</strong> —
              comparando contra <strong>{n_cands} nodos</strong> topológicos con mejor perfil.
            </div>
            """, unsafe_allow_html=True)

            if brechas:
                for i, b in enumerate(brechas[:3]):
                    st.markdown(f"""
                    <div class="recom-item">
                      <div class="recom-num">{i+1}</div>
                      <div>
                        <div class="recom-text">
                          <strong>{b['nombre']}</strong><br>{b['consejo']}
                        </div>
                        <div class="recom-pct">
                          {b['pct']*100:.0f}% de los casos exitosos en tu perfil cumplen esto
                        </div>
                      </div>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.success("Ya cumples los hábitos clave de los casos de éxito en tu perfil.")

        # ── Nota metodológica ──────────────────────────────────────────────────
        st.markdown("""
        <p style="font-size:0.72rem;color:#8a8478;font-family:'JetBrains Mono',monospace;
                  margin-top:2rem;line-height:1.7;border-top:1px solid #e2ddd6;padding-top:1rem;">
          Metodología: Análisis Topológico de Datos (Mapper TDA) · Cohorte geriátrica INMEGEN
          (n=884) · Score de hábitos basado en umbrales OMS/AHA · Las recomendaciones reflejan
          la distancia topológica entre el perfil actual y los nodos de mayor score en el mismo
          grupo diagnóstico · Herramienta de apoyo educativo, no sustituye el juicio médico.
        </p>
        """, unsafe_allow_html=True)
