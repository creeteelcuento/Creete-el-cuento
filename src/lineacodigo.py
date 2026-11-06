"""
Créete el Cuento · Sistema de gestión interno (prototipo funcional)

Páginas: Panel · Participantes · Pagos · Asistencia · Becas · Seguimiento · Reportes · Historial.
DATOS: por ahora todo vive en memoria (st.session_state) con datos ficticios,
para que el prototipo corra sin base de datos.

Ejecutar:  streamlit run app.py
"""
from __future__ import annotations

import base64
import calendar
import csv
import io
import re
import os

from supabase import create_client, Client
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Conectar con Supabase
supabase_url = os.environ.get("SUPABASE_URL")
supabase_key = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(supabase_url, supabase_key)

from datetime import date, datetime, timedelta
from html import escape
from pathlib import Path

try:
    from zoneinfo import ZoneInfo
    TZ = ZoneInfo("America/Santiago")
except Exception:  # noqa: BLE001
    TZ = None

import streamlit as st

# ─────────────────────────────── CONFIGURACIÓN ───────────────────────────────
st.set_page_config(page_title="Créete el Cuento · Gestión", page_icon="💡", layout="wide")

ASSETS = Path(__file__).parent / "assets"
NOMBRE_USUARIA = "[Nombre]"      # cámbialo por el nombre de la coordinadora
DIAS_ALERTA = 15                 # alerta de vencimiento: faltan 15 días o menos
PRECIO_DEMO = 25000              # monto ficticio solo para datos de ejemplo
URL_DATASTUDIO = "https://lookerstudio.google.com/"   # pega aquí el enlace de tu informe
ROLES = ["Mentora", "Emprendedora", "Becada", "Red de psicólogos", "Red de coaches"]
PAISES = ["Chile", "Argentina", "Bolivia", "Brasil", "Colombia", "Ecuador", "España", "México", "Perú",
          "Uruguay", "Venezuela", "Otro"]
SIGUIENTE_PASO = {
    "Mentora": ("En validación de perfil", "Validación de perfil por la coordinadora"),
    "Emprendedora": ("Pendiente de pago", "Pago directo de membresía"),
    "Becada": ("En evaluación de beca", "Evaluación de beca"),
    "Red de psicólogos": ("En validación de perfil", "Validación de perfil por la coordinadora"),
    "Red de coaches": ("En validación de perfil", "Validación de perfil por la coordinadora"),
}
CARTA_TIPOS = ["png", "jpg", "jpeg", "pdf", "doc", "docx"]
TIPOS_ACTIVIDAD = ["Taller", "Mentoría", "Coaching", "Charla"]
MODALIDADES = ["Online", "Presencial"]
ESTADOS = ["Pagado", "Vencido", "Por vencer", "Becado (exento)"]
MESES = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]
MESES_LARGO = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre",
               "octubre", "noviembre", "diciembre"]
NAV_GRUPOS = [
    ("Inicio", [("Panel", "dashboard")]),
    ("Gestión", [("Participantes", "group"), ("Pagos", "credit_card"), ("Asistencia", "check"),
                 ("Becas", "workspace_premium")]),
    ("Análisis", [("Seguimiento", "bar_chart"), ("Reportes", "description"), ("Historial", "schedule")]),
]

# Paleta: blanco, dorado, amarillos pastel y negro
C_BG = "#FAF7EE"
C_INK = "#15130E"
C_SIDE = "#14120D"
C_GOLD = "#C9A227"
C_GOLD2 = "#F2C230"
C_PASTEL = "#FFF3C4"
C_LINE = "#E9DFB8"
C_MUTED = "#6F6A5A"

ICONOS = {
    "users": '<path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/>',
    "clock": '<circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/>',
    "check": '<path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/>',
    "award": '<circle cx="12" cy="8" r="7"/><polyline points="8.21 13.89 7 23 12 20 17 23 15.79 13.88"/>',
    "trend": '<polyline points="23 6 13.5 15.5 8.5 10.5 1 18"/><polyline points="17 6 23 6 23 12"/>',
    "alert": '<path d="M10.29 3.86 1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/>',
    "heart": '<path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"/>',
}

# ─────────────────────────────────── ESTILOS ─────────────────────────────────
CSS = """
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700;800&display=swap');
.stApp :where(p, span, div, label, button, input, textarea, li, td, th, a, small, h1, h2, h3):not([data-testid="stIconMaterial"]) {font-family:'Poppins','Segoe UI',sans-serif;}
[data-testid="stDialog"] :where(p, span, div, label, button, input, h1, h2, h3):not([data-testid="stIconMaterial"]) {font-family:'Poppins','Segoe UI',sans-serif;}
.stApp {background:@BG; color:@INK;}
.stApp p, .stApp label {color:@INK;}
#MainMenu, footer, .stAppDeployButton {display:none !important;}
header[data-testid="stHeader"] {background:transparent; height:0; pointer-events:none;}
[data-testid="stToolbar"], [data-testid="stDecoration"] {display:none !important;}
.block-container {padding:1.6rem 2.2rem 3rem 2.2rem; max-width:1500px;}
[data-testid="stHorizontalBlock"] {gap:16px;}
[data-testid="stVerticalBlock"] {gap:.75rem;}
[data-testid="column"], [data-testid="stColumn"] {min-width:0 !important;}
@media (max-width: 900px) {
  .block-container {padding:1rem 1rem 2rem 1rem;}
  [data-testid="stHorizontalBlock"] {flex-wrap:wrap;}
  [data-testid="stHorizontalBlock"] > :is([data-testid="column"], [data-testid="stColumn"]) {flex:1 1 240px;}}

[data-testid="stDialog"] [role="dialog"] {background:#fff; border:1px solid @LINE; border-top:4px solid @GOLD2; border-radius:18px;}
[data-testid="stDialog"] h2 {font-weight:700; color:@INK;}
[data-testid="stFileUploaderDropzone"] {background:#FFFDF3; border:2px dashed @GOLD; border-radius:14px;}
[data-testid="stFileUploaderDropzone"] button {background:@GOLD2; border:1px solid @INK; color:@INK; border-radius:10px;}

/* Menú lateral */
section[data-testid="stSidebar"] {background:@SIDE; border-right:0; width:250px !important; min-width:250px !important;}
section[data-testid="stSidebar"] > div:first-child {width:250px !important; background:@SIDE;}
[data-testid="stSidebarHeader"], [data-testid="stSidebarCollapseButton"], [data-testid="stSidebarResizeHandle"] {display:none !important;}
[data-testid="stSidebarContent"] {padding:0 !important;}
[data-testid="stSidebarUserContent"] {padding:1rem 12px 2rem 12px;}
section[data-testid="stSidebar"] [data-testid="stVerticalBlock"] {gap:4px;}
.logo-box {background:#fff; border-radius:16px; padding:12px; margin:10px 0 22px 0; text-align:center; font-weight:800; color:@INK; line-height:1.2;}
.logo-box img {height:72px; max-width:100%; object-fit:contain;}
.nav-g {font-size:11px; font-weight:700; letter-spacing:.14em; color:#B8A55E; margin:16px 0 4px 6px; text-transform:uppercase;}
section[data-testid="stSidebar"] [class*="st-key-nav_"] button, section[data-testid="stSidebar"] [class*="st-key-navon_"] button {width:100%; min-height:44px; justify-content:flex-start; background:transparent; border:0; border-radius:12px; box-shadow:none; color:#EFE8D0; padding:0 14px;}
section[data-testid="stSidebar"] [class*="st-key-nav_"] button > div, section[data-testid="stSidebar"] [class*="st-key-navon_"] button > div {justify-content:flex-start; gap:10px;}
section[data-testid="stSidebar"] [class*="st-key-nav_"] button p, section[data-testid="stSidebar"] [class*="st-key-navon_"] button p {font-weight:600; font-size:14px; color:#EFE8D0;}
section[data-testid="stSidebar"] [class*="st-key-nav_"] button:hover {background:rgba(255,255,255,.08);}
section[data-testid="stSidebar"] [class*="st-key-navon_"] button, section[data-testid="stSidebar"] [class*="st-key-navon_"] button:hover {background:linear-gradient(135deg,#F7D44C,#D9A514) !important;}
section[data-testid="stSidebar"] [class*="st-key-navon_"] button p {color:@INK; font-weight:700;}
section[data-testid="stSidebar"] [data-testid="stIconMaterial"] {color:@GOLD2 !important;}
section[data-testid="stSidebar"] [class*="st-key-navon_"] [data-testid="stIconMaterial"] {color:@INK !important;}
.user-card {display:flex; align-items:center; gap:10px; margin-top:26px; padding:12px; border-radius:14px; background:rgba(255,255,255,.07); border:1px solid rgba(242,194,48,.25);}
.user-card .av {width:38px; height:38px; border-radius:12px; background:@GOLD2; color:@INK; font-weight:800; display:flex; align-items:center; justify-content:center; font-size:14px;}
.user-card b {display:block; color:#fff; font-size:13px;}
.user-card span {color:#B8A55E; font-size:12px;}

/* Banner superior */
.hero {position:relative; overflow:hidden; display:flex; justify-content:space-between; align-items:flex-start; gap:20px; background:linear-gradient(120deg,#15130E 0%,#2A2210 62%,#5A4410 100%); border-radius:22px; padding:26px 32px; margin-bottom:6px; box-shadow:0 10px 26px rgba(40,30,0,.18);}
.hero:before {content:""; position:absolute; right:-60px; top:-90px; width:300px; height:300px; border-radius:50%; background:radial-gradient(circle,rgba(242,194,48,.38),transparent 68%);}
.hmain {position:relative; z-index:1;}
.eyebrow {font-size:11px; font-weight:700; letter-spacing:.16em; color:@GOLD2;}
.h1 {font-size:32px; font-weight:700; color:#fff; line-height:1.15; margin:8px 0 6px 0;}
.hsub {font-size:14px; color:#E4DAB6; margin-bottom:14px;}
.hstats {display:flex; gap:10px; flex-wrap:wrap;}
.hstat {background:rgba(255,255,255,.09); border:1px solid rgba(242,194,48,.3); border-radius:12px; padding:8px 16px; min-width:120px;}
.hstat span {display:block; font-size:11px; color:#E4DAB6;}
.hstat b {font-size:20px; color:#fff; font-weight:700;}
.hpill {position:relative; z-index:1; background:#fff; color:@INK; font-size:12px; font-weight:600; padding:8px 16px; border-radius:99px; white-space:nowrap; display:flex; align-items:center; gap:8px;}
.hpill .dot {width:8px; height:8px; border-radius:50%; background:#27C45B;}

/* Tarjetas */
[class*="st-key-card_"] {background:#fff; border:1px solid @LINE; border-top:3px solid @GOLD2; border-radius:18px; padding:20px 22px; box-shadow:0 6px 18px rgba(70,52,0,.06); gap:.6rem; min-width:0; max-width:100%;}.sub {font-weight:700; font-size:15px; margin-bottom:2px;}
.muted {color:@MUTED; font-size:13px;}
.mc {background:#fff; border:1px solid @LINE; border-radius:18px; padding:16px 18px; box-shadow:0 6px 18px rgba(70,52,0,.06); min-height:142px;}
.mic {width:38px; height:38px; border-radius:12px; background:@PASTEL; color:#8A6A00; display:flex; align-items:center; justify-content:center; margin-bottom:10px;}
.ml {font-size:13px; color:@MUTED; line-height:1.3;}
.mv {font-size:clamp(20px,2vw,27px); font-weight:800; line-height:1.15; margin-top:2px; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;}.ms {font-size:12px; color:@MUTED; margin-top:4px;}
.info {background:@PASTEL; border:1px solid @LINE; color:@INK; border-radius:12px; padding:10px 14px; font-size:13px;}

/* Botones */
.stButton > button, .stFormSubmitButton > button {border:1px solid #1B1810; background:@GOLD2; color:@INK; border-radius:12px; min-height:42px; box-shadow:none; padding:0 20px;}
.stButton > button:hover {background:#E2AE1F; border-color:#1B1810; color:@INK;}
.stButton > button p {font-weight:700; font-size:14px; color:@INK;}
.stDownloadButton > button {border:1px solid #1B1810; background:#fff; color:@INK; border-radius:12px; min-height:42px; box-shadow:none; padding:0 20px;}
.stDownloadButton > button:hover {background:@PASTEL; border-color:#1B1810; color:@INK;}
.stDownloadButton > button p {font-weight:700; font-size:14px; color:@INK;}
[class*="st-key-mini_"] button {min-height:32px; padding:0 14px; background:#fff; border:1px solid #D6C98F; border-radius:99px;}
[class*="st-key-mini_"] button p {font-size:12px; font-weight:600;}
[class*="st-key-mini_"] button:hover {background:@PASTEL; border-color:@GOLD;}

/* Campos */
[data-testid="stWidgetLabel"] p {font-weight:600; font-size:13px;}
[data-testid="stTextInputRootElement"], [data-testid="stTextAreaRootElement"], [data-testid="stSelectbox"] [data-baseweb="select"] > div, [data-testid="stMultiSelect"] [data-baseweb="select"] > div, [data-testid="stDateInputField"], [data-testid="stNumberInputContainer"] {border-radius:12px !important; border:1px solid #E0D4A2 !important; background:#fff !important;}
[data-testid="stTextInputRootElement"] {min-height:44px;}
[data-testid="stSelectbox"] div:has(> input), [data-testid="stDateInput"] div:has(> input), [data-testid="stMultiSelect"] div:has(> input) {border-radius:12px !important; background:#fff !important;}
[data-baseweb="tag"] {background:@PASTEL !important; color:@INK !important; border-radius:99px !important;}

/* Chips */
.chip {display:inline-block; padding:3px 11px; border-radius:99px; font-size:12px; font-weight:600; border:1px solid #DCCB86; color:@INK; background:@PASTEL; white-space:normal; overflow-wrap:anywhere;}
.c-pagado, .c-activa {background:#DDF5E4; color:#14532D; border-color:#9ED9B1;}
.c-vencer {background:#FFF1BF; color:#6B4E00; border-color:#E6C34D;}
.c-vencido {background:#FDE0DD; color:#8A1C14; border-color:#F0A8A2;}
.c-exento {background:#EDE6FB; color:#4B2E8A; border-color:#CDBDF2;}
.c-inact {background:#ECEAE3; color:#55503F; border-color:#D5D1C2;}
.c-ink {background:#1B1810; color:#F5D678; border-color:#1B1810;}
.clasif {background:#FFFDF3; border:1px solid transparent; border-radius:12px; padding:10px 14px; margin-bottom:8px; font-size:14px;}
.clasif .chip {margin-bottom:5px;}
.clasif.sel {border-color:@GOLD; background:@PASTEL;}

/* Gráficos propios */
.leg {display:flex; gap:16px; font-size:12px; color:@MUTED; margin:2px 0 4px 0;}
.leg i {display:inline-block; width:10px; height:10px; border-radius:3px; margin-right:6px;}
.vchart {display:flex; align-items:stretch; gap:14px; height:250px; margin-top:6px; background:repeating-linear-gradient(to top, transparent 0, transparent 49px, #F1E9CB 49px, #F1E9CB 50px);}
.vg {flex:1; display:flex; flex-direction:column; height:100%;}
.vbars {flex:1; min-height:0; display:flex; align-items:flex-end; justify-content:center; gap:5px; padding-top:22px; border-bottom:2px solid #E4D8A8;}
.vb {width:min(34px,44%); border-radius:8px 8px 0 0; position:relative; min-height:3px;}
.vb span {position:absolute; top:-18px; left:50%; transform:translateX(-50%); font-size:11px; font-weight:700; white-space:nowrap; color:@INK;}
.vl {text-align:center; font-size:12px; color:@MUTED; padding-top:6px; height:26px;}
.hr {display:flex; align-items:center; gap:12px; padding:7px 0;}
.hl {width:150px; font-size:13px; flex-shrink:0;}
.hb {flex:1; height:12px; background:#F5EFD6; border-radius:9px; overflow:hidden;}
.hb i {display:block; height:12px; border-radius:9px;}
.hv {min-width:70px; text-align:right; font-size:13px; font-weight:700;}
.pctrow {display:flex; align-items:center; gap:10px;}
.pctrow b {font-size:13px; min-width:40px; text-align:right;}
.bar {flex:1; height:10px; background:#F5EFD6; border-radius:9px; overflow:hidden;}
.bar i {display:block; height:10px; background:linear-gradient(90deg,#E3B72A,#C9A227); border-radius:9px;}

/* Tablas */
.th {font-size:12px; font-weight:700; color:@MUTED; padding-bottom:6px; white-space:normal; overflow-wrap:anywhere; line-height:1.35; text-transform:uppercase; letter-spacing:.04em;}
.hline {border-bottom:2px solid @LINE; margin:0 0 2px 0;}
.td {font-size:14px; padding:8px 0; min-width:0; overflow-wrap:anywhere; line-height:1.4;}
.nw {white-space:nowrap;}
.fila {border-bottom:1px solid #F3ECCF; margin:0;}
.tbl {width:100%; max-width:100%; table-layout:fixed; border-collapse:collapse;}
.tbl th {text-align:left; padding:10px; font-size:12px; color:@MUTED; background:#FBF7E6; border-bottom:2px solid @LINE; text-transform:uppercase; letter-spacing:.04em; overflow-wrap:anywhere;}
.tbl td {padding:10px; border-bottom:1px solid #F3ECCF; font-size:14px; overflow-wrap:anywhere;}
.dg {font-size:12px; font-weight:700; letter-spacing:.08em; color:#8A6A00; text-transform:uppercase; margin:14px 0 2px 0;}

/* Asistencia tipo banner */
.att-title {font-size:12px; font-weight:600; text-align:center; line-height:1.35;}
.att-title .t {font-size:13px;}
.att-head {font-size:12px; font-weight:700; color:@MUTED; text-transform:uppercase; letter-spacing:.04em;}
[class*="st-key-att"] {display:flex; justify-content:center;}
[class*="st-key-att"] button {width:34px; min-width:34px; height:34px; min-height:34px; padding:0; border-radius:50%; border:2px solid #D9CFA6; background:#fff; box-shadow:none; transition:all .15s;}
[class*="st-key-att"] button:hover {border-color:#C9A227; background:#FFF8DC; transform:scale(1.05);}
[class*="st-key-attp_"] button, [class*="st-key-attp_"] button:hover {background:#CDE8D3; border-color:#8FC39E;}
[class*="st-key-atta_"] button, [class*="st-key-atta_"] button:hover {background:#F6D2CB; border-color:#DFA196;}
[class*="st-key-attp_"] button p {color:#3F7D52 !important; font-size:16px; font-weight:700;}
[class*="st-key-atta_"] button p {color:#A5554A !important; font-size:16px; font-weight:700;}
/* Tablas anchas: conservar columnas y desplazar dentro de la tarjeta. */
.st-key-card_lista, .st-key-card_tabla, .st-key-card_asis, .st-key-card_seg, .st-key-card_becas_tabla,
.st-key-card_hist {
  max-width:100%; overflow-x:auto; overflow-y:hidden;
}
.st-key-card_lista [data-testid="stHorizontalBlock"],
.st-key-card_tabla [data-testid="stHorizontalBlock"],
.st-key-card_seg [data-testid="stHorizontalBlock"],
.st-key-card_becas_tabla [data-testid="stHorizontalBlock"],
.st-key-card_hist [data-testid="stHorizontalBlock"] {
  width:max-content; min-width:100%; flex-wrap:nowrap;
}
.st-key-card_lista [data-testid="stHorizontalBlock"] > :is([data-testid="column"], [data-testid="stColumn"]),
.st-key-card_tabla [data-testid="stHorizontalBlock"] > :is([data-testid="column"], [data-testid="stColumn"]),
.st-key-card_seg [data-testid="stHorizontalBlock"] > :is([data-testid="column"], [data-testid="stColumn"]),
.st-key-card_becas_tabla [data-testid="stHorizontalBlock"] > :is([data-testid="column"], [data-testid="stColumn"]),
.st-key-card_hist [data-testid="stHorizontalBlock"] > :is([data-testid="column"], [data-testid="stColumn"]) {
  flex:0 0 160px !important; min-width:160px !important;
}
.st-key-card_lista [data-testid="stHorizontalBlock"] > :is([data-testid="column"], [data-testid="stColumn"]):first-child,
.st-key-card_tabla [data-testid="stHorizontalBlock"] > :is([data-testid="column"], [data-testid="stColumn"]):first-child,
.st-key-card_seg [data-testid="stHorizontalBlock"] > :is([data-testid="column"], [data-testid="stColumn"]):first-child,
.st-key-card_becas_tabla [data-testid="stHorizontalBlock"] > :is([data-testid="column"], [data-testid="stColumn"]):first-child,
.st-key-card_hist [data-testid="stHorizontalBlock"] > :is([data-testid="column"], [data-testid="stColumn"]):first-child {
  flex-basis:200px !important; min-width:200px !important;
}
.st-key-card_asis [data-testid="stHorizontalBlock"] {width:max-content; min-width:100%; flex-wrap:nowrap;}
.st-key-card_asis [data-testid="stHorizontalBlock"] > :is([data-testid="column"], [data-testid="stColumn"]) {flex:0 0 110px !important; min-width:110px !important;}
.st-key-card_asis [data-testid="stHorizontalBlock"] > :is([data-testid="column"], [data-testid="stColumn"]):first-child {flex-basis:230px !important; min-width:230px !important;}

/* Arreglo de superposiciones: Streamlit aplica margen negativo a st.markdown */
[data-testid="stMarkdown"], [data-testid="stMarkdownContainer"], .stMarkdown {margin-bottom:0 !important; margin-top:0 !important;}
[data-testid="stMarkdownContainer"] p {margin-bottom:0 !important;}
[data-testid="stElementContainer"] {min-width:0; max-width:100%;}
[data-testid="stHorizontalBlock"] {align-items:stretch;}
.mc {height:100%; min-height:165px; box-sizing:border-box;}
.nav-g {margin:18px 0 6px 6px !important; line-height:1.3;}
.hero {margin-bottom:14px;}
"""
CSS = (CSS.replace("@BG", C_BG).replace("@INK", C_INK).replace("@SIDE", C_SIDE).replace("@GOLD2", C_GOLD2)
       .replace("@GOLD", C_GOLD).replace("@PASTEL", C_PASTEL).replace("@LINE", C_LINE).replace("@MUTED", C_MUTED))
st.markdown("<style>" + re.sub(r"\s*\n\s*", " ", CSS) + "</style>", unsafe_allow_html=True)

# ─────────────────────────────────── UTILIDADES ──────────────────────────────
def ahora() -> datetime:
    """Fecha y hora actuales en Chile (sin zona, para guardarlas simples)."""
    return (datetime.now(TZ) if TZ else datetime.now()).replace(tzinfo=None)


def hoy() -> date:
    return ahora().date()


def b64(nombre: str) -> str:
    ruta = ASSETS / nombre
    if not ruta.exists():
        return ""
    mime = "image/png" if nombre.endswith("png") else "image/jpeg"
    return f"data:{mime};base64," + base64.b64encode(ruta.read_bytes()).decode()


def _p(s: str) -> str:
    # "$" se escapa para que Markdown no lo confunda con fórmulas matemáticas
    return re.sub(r">\s+<", "><", s.strip()).replace("$", "&#36;")


def html(s: str) -> None:
    st.markdown(_p(s), unsafe_allow_html=True)


def celda(col, s: str) -> None:
    col.markdown(_p(s), unsafe_allow_html=True)


def td(col, contenido: str, extra: str = "") -> None:
    celda(col, f'<div class="td {extra}">{contenido}</div>')


def cabecera(anchos: list[float], titulos: list[str]) -> None:
    for col, t in zip(st.columns(anchos), titulos):
        celda(col, f'<div class="th">{escape(t)}</div>')
    html('<div class="hline"></div>')


def sep() -> None:
    html('<div class="fila"></div>')


def icono(nombre: str) -> str:
    return (f'<svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" '
            f'stroke-linecap="round" stroke-linejoin="round">{ICONOS[nombre]}</svg>')


def plata(v: float) -> str:
    return "$ " + f"{v:,.0f}".replace(",", ".")


def corto(v: float) -> str:
    if v >= 1_000_000:
        return f"{v / 1_000_000:.1f}M"
    if v >= 1000:
        return f"{v / 1000:.0f}k"
    return str(int(v))


def fecha_txt(d: date | None) -> str:
    return d.strftime("%d/%m/%Y") if d else "—"


def fecha_corta(d: date | None) -> str:
    return d.strftime("%d/%m/%y") if d else "—"


def fecha_larga(d: date) -> str:
    return f"{d.day} de {MESES_LARGO[d.month - 1]} de {d.year}"


def sumar_meses(d: date, n: int) -> date:
    m = d.month - 1 + n
    a, m = d.year + m // 12, m % 12 + 1
    return date(a, m, min(d.day, calendar.monthrange(a, m)[1]))


def ultimos_meses(n: int) -> list[tuple[int, int]]:
    h = hoy()
    out = []
    for i in range(n - 1, -1, -1):
        a, m = divmod(h.year * 12 + h.month - 1 - i, 12)
        out.append((a, m + 1))
    return out


def etiqueta_mes(k: tuple[int, int]) -> str:
    return f"{MESES[k[1] - 1]} {str(k[0])[-2:]}"


def total_mes(lista: list[dict], k: tuple[int, int]) -> int:
    return sum(x["monto"] for x in lista if (x["fecha"].year, x["fecha"].month) == k)


def chip(estado: str) -> str:
    clase = {"Pagado": "c-pagado", "Por vencer": "c-vencer", "Vencido": "c-vencido", "Becado (exento)": "c-exento",
             "Activa": "c-activa", "Inactiva": "c-inact"}.get(estado, "")
    punto = "● " if estado in ("Pagado", "Por vencer", "Vencido") else ""
    return f'<span class="chip {clase}">{punto}{escape(estado)}</span>'


def tabla_html(cabeceras: list[str], filas: list[list[str]]) -> str:
    th = "".join(f"<th>{escape(c)}</th>" for c in cabeceras)
    tr = "".join("<tr>" + "".join(f"<td>{c}</td>" for c in f) + "</tr>" for f in filas)
    return f'<table class="tbl"><tr>{th}</tr>{tr}</table>'


def barra(pct: int | None) -> str:
    if pct is None:
        return '<div class="pctrow"><span class="muted">Sin datos</span></div>'
    return f'<div class="pctrow"><div class="bar"><i style="width:{pct}%"></i></div><b>{pct}%</b></div>'


def a_csv(cabeceras: list[str], filas: list[list]) -> bytes:
    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow(cabeceras)
    w.writerows(filas)
    return buf.getvalue().encode("utf-8-sig")


def voucher_demo(texto: str) -> bytes:
    from PIL import Image, ImageDraw
    img = Image.new("RGB", (480, 300), "#FFFCEF")
    d = ImageDraw.Draw(img)
    d.rectangle([8, 8, 471, 291], outline="#3A3A3A", width=3)
    d.text((30, 40), "COMPROBANTE DE EJEMPLO", fill="#3A3A3A")
    d.text((30, 90), texto, fill="#706F6F")
    d.text((30, 140), "Datos ficticios para demostración", fill="#D7AE00")
    buf = io.BytesIO()
    img.save(buf, "PNG")
    return buf.getvalue()


# ── Componentes visuales ──
def hero(seccion: str, titulo_txt: str, sub: str, stats: list[tuple[str, object]] | None = None) -> None:
    caja = "".join(f'<div class="hstat"><span>{escape(l)}</span><b>{escape(str(v))}</b></div>' for l, v in (stats or []))
    html(f'<div class="hero"><div class="hmain"><div class="eyebrow">CRÉETE EL CUENTO · {escape(seccion.upper())}</div>'
         f'<div class="h1">{escape(titulo_txt)}</div><div class="hsub">{escape(sub)}</div>'
         f'<div class="hstats">{caja}</div></div><div class="hpill"><span class="dot"></span>{fecha_larga(hoy())}</div></div>')


def mc(ic: str, label: str, valor: str, sub: str = "") -> str:
    return (f'<div class="mc"><div class="mic">{icono(ic)}</div><div class="ml">{escape(label)}</div>'
            f'<div class="mv">{escape(valor)}</div><div class="ms">{escape(sub)}</div></div>')


def grafico_barras(etiquetas: list[str], series: list[tuple[str, list[float], str]]) -> str:
    mx = max([v for _, vals, _ in series for v in vals] + [1])
    grupos = ""
    for i, e in enumerate(etiquetas):
        barras = ""
        for nombre, vals, color in series:
            v = vals[i]
            alto = 0 if v == 0 else max(v / mx * 100, 2)
            etq = f"<span>{corto(v)}</span>" if v else ""
            barras += f'<div class="vb" title="{escape(nombre)}: {plata(v)}" style="height:{alto:.1f}%;background:{color}">{etq}</div>'
        grupos += f'<div class="vg"><div class="vbars">{barras}</div><div class="vl">{escape(e)}</div></div>'
    leyenda = "".join(f'<span><i style="background:{c}"></i>{escape(n)}</span>' for n, _, c in series)
    return f'<div class="leg">{leyenda}</div><div class="vchart">{grupos}</div>'


def grafico_h(datos: list[tuple[str, float]], color: str = C_GOLD2, fmt=lambda v: str(int(v)), maximo: float | None = None) -> str:
    if not datos:
        return '<div class="muted">Sin datos para mostrar.</div>'
    mx = maximo or max([v for _, v in datos] + [1])
    filas = ""
    for lab, v in datos:
        filas += (f'<div class="hr"><div class="hl">{escape(lab)}</div><div class="hb"><i style="width:{min(v / mx * 100, 100):.1f}%;'
                  f'background:{color}"></i></div><div class="hv">{escape(fmt(v))}</div></div>')
    return filas


# ───────────────────────────── CAPA DE DATOS (en memoria) ─────────────────────
def registrar_log(accion: str, detalle: str, archivo_nombre: str | None = None, archivo_bytes: bytes | None = None) -> None:
    s = st.session_state
    s.setdefault("historial_logs", [])
    nuevo_id = max([x["id"] for x in s.historial_logs] + [0]) + 1
    s.historial_logs.insert(0, dict(id=nuevo_id, ts=ahora(), accion=accion, detalle=detalle,
                                    archivo_nombre=archivo_nombre, archivo_bytes=archivo_bytes))

def cargar_participantes_desde_db() -> list:
    """Carga todos los participantes desde Supabase."""
    try:
        response = supabase.table("Participantes").select("*").execute()
        return response.data
    except Exception as e:
        st.error(f"Error al cargar participantes: {e}")
        return []

#NUEVO SOLO PARA CONECTAR CON EL SUPABASE, SE DEBE REEMPLAZAR LA FUNCION INICIALIZAR DATOS PARA QUE CARGUE DESDE LA BASE DE DATOS EN LUGAR DE MEMORIA
def iniciar_datos() -> None:
    """Inicializa datos desde Supabase en lugar de memoria."""
    if "participantes" in st.session_state:
        return
    
    # Cargar desde Supabase
    participantes_db = cargar_participantes_desde_db()
    
    # Convertir a formato que entiende el código existente
    st.session_state.participantes = []
    for p in participantes_db:
        st.session_state.participantes.append({
            "id": p["id"],
            "nombre": p["nombre"],
            "correo": p["correo"],
            "telefono": p.get("telefono", ""),
            "pais": p.get("pais", "Chile"),
            "rol": p.get("rol", "Emprendedora"),
            "descripcion": "",
            "estado": p.get("estado", "Activa"),
            "carta_nombre": None,
            "carta": None
        })
    
    # Inicializar otras estructuras en memoria (por ahora)
    # TODO: Crear tablas en Supabase para: membresias, pagos, becas, actividades, etc.
    st.session_state.membresias = {}
    st.session_state.pagos = []
    st.session_state.donaciones = []
    st.session_state.becas = []
    st.session_state.actividades = []
    st.session_state.asistencias = set()
    st.session_state.ausencias = set()
    st.session_state.historial_logs = []


def participante(pid: int) -> dict:
    return next(p for p in st.session_state.participantes if p["id"] == pid)


def estado_pago(p: dict) -> str | None:
    b = beca_actual(p["id"])
    if b and estado_beca(b) == "Activa":
        return "Becado (exento)"
    m = st.session_state.membresias.get(p["id"])
    if not m:
        return None
    dias = (m["vencimiento"] - hoy()).days
    return "Vencido" if dias < 0 else "Por vencer" if dias <= DIAS_ALERTA else "Pagado"


def filas_pagos() -> list[dict]:
    filas = []
    for p in st.session_state.participantes:
        est = estado_pago(p)
        if est is None:
            continue
        m = st.session_state.membresias.get(p["id"], {})
        filas.append(dict(p=p, estado=est, inicio=m.get("inicio"), vence=m.get("vencimiento")))
    return filas


def ultimo_comprobante(pid: int) -> dict | None:
    cs = [x for x in st.session_state.pagos if x["participante_id"] == pid and x["comprobante"]]
    return max(cs, key=lambda x: (x["fecha"], x["id"])) if cs else None


def registrar_pago(pid: int, monto: int, metodo: str, fecha: date, meses: int, archivo) -> None:
    s = st.session_state
    s.pagos.append(dict(id=max([x["id"] for x in s.pagos] + [0]) + 1, participante_id=pid, fecha=fecha, monto=monto,
                        metodo=metodo, comprobante_nombre=archivo.name, comprobante=archivo.getvalue()))
    s.membresias[pid] = dict(inicio=fecha, vencimiento=sumar_meses(fecha, meses))
    participante(pid)["estado"] = "Activa"
    registrar_log("Registro de pago", f"Se registró pago de {plata(monto)} para {participante(pid)['nombre']}.",
                  archivo.name, archivo.getvalue())


def registrar_donacion(donante: str, monto: int, fecha: date, archivo) -> None:
    s = st.session_state
    s.donaciones.append(dict(id=max([x["id"] for x in s.donaciones] + [0]) + 1, donante=donante, monto=monto, fecha=fecha,
                             comprobante_nombre=archivo.name if archivo else None,
                             comprobante=archivo.getvalue() if archivo else None))
    registrar_log("Registro de donación", f"Se registró donación de {plata(monto)} de '{donante}'.",
                  archivo.name if archivo else None, archivo.getvalue() if archivo else None)


def email_valido(c: str) -> bool:
    return re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", c) is not None

#NUEVO, PARA EL SUPABASE
def guardar_participante_en_db(nombre: str, correo: str, telefono: str, pais: str, rol: str, estado: str) -> bool:
    """Guarda un nuevo participante en la tabla de Supabase."""
    try:
        response = supabase.table("Participantes").insert({
            "nombre": nombre,
            "correo": correo,
            "telefono": telefono,
            "pais": pais,
            "rol": rol,
            "estado": estado
        }).execute()
        return True
    except Exception as e:
        st.error(f"Error al guardar en base de datos: {e}")
        return False
#HASTA AQUI

#NUEVO PARA EL SUPABASE
def guardar_participante() -> None:
    s = st.session_state
    nombre, correo = s.f_nombre.strip(), s.f_correo.strip().lower()
    carta = s.get(f"f_carta_{s.carta_n}")
    
    # Validaciones
    if not nombre or not correo or not s.f_rol or not s.f_pais:
        s.f_msg = ("error", "Completa nombre, correo, país y rol para guardar.")
    elif not email_valido(correo):
        s.f_msg = ("error", "El correo no tiene un formato válido.")
    elif any(p["correo"].lower() == correo for p in s.participantes):
        s.f_msg = ("error", "Ese correo ya está registrado: no se permiten duplicados.")
    elif s.f_rol == "Mentora" and carta is None:
        s.f_msg = ("error", "La carta de compromiso es obligatoria para registrar a una mentora.")
    else:
        estado = SIGUIENTE_PASO[s.f_rol][0]
        
        # 1. Intentar guardar en Supabase primero
        if guardar_participante_en_db(nombre, correo, s.f_tel.strip(), s.f_pais, s.f_rol, estado):
            
            # 2. Si fue exitoso, actualizar también la sesión local para que se vea al instante
            nuevo_id = max((p["id"] for p in s.participantes), default=0) + 1
            s.participantes.append(dict(
                id=nuevo_id, nombre=nombre, correo=correo, telefono=s.f_tel.strip(),
                pais=s.f_pais, rol=s.f_rol, descripcion=s.f_desc.strip(), estado=estado,
                carta_nombre=carta.name if carta else None, carta=carta.getvalue() if carta else None))
            
            s.f_msg = ("ok", f"{nombre} quedó registrada como {s.f_rol.lower()} · siguiente paso: {estado.lower()}.")
            registrar_log("Registro de participante", f"Se agregó a {nombre} ({s.f_pais}) como {s.f_rol}.",
                          carta.name if carta else None, carta.getvalue() if carta else None)
            
            # Limpiar el formulario
            s.f_nombre = s.f_correo = s.f_tel = s.f_desc = ""
            s.f_rol = None
            s.carta_n += 1
        else:
            s.f_msg = ("error", "No se pudo guardar en la base de datos. Intenta de nuevo.")
#Hasta aqui


def beca_actual(pid: int) -> dict | None:
    recs = [b for b in st.session_state.becas if b["participante_id"] == pid]
    return max(recs, key=lambda b: b["id"]) if recs else None


def estado_beca(b: dict) -> str:
    return "Activa" if b["estado"] == "Activa" and b["termino"] >= hoy() else "Inactiva"


def detalle_inactiva(b: dict) -> str:
    return "Revocada" if b["estado"] == "Revocada" else "Vigencia terminada"


def asignar_beca(pid: int, motivo: str, inicio: date, termino: date) -> None:
    s = st.session_state
    s.becas.append(dict(id=max([b["id"] for b in s.becas] + [0]) + 1, participante_id=pid, motivo=motivo,
                        asignacion=hoy(), inicio=inicio, termino=termino, estado="Activa"))
    participante(pid)["estado"] = "Activa"
    registrar_log("Asignación de beca", f"Se otorgó beca a {participante(pid)['nombre']} por '{motivo}'.")


def revocar_beca(pid: int, motivo: str) -> None:
    b = beca_actual(pid)
    b["estado"], b["motivo_revocacion"], b["fecha_revocacion"] = "Revocada", motivo, hoy()
    participante(pid)["estado"] = "Beca revocada"
    registrar_log("Revocación de beca", f"Se revocó la beca a {participante(pid)['nombre']}. Motivo: {motivo}")


def marca(aid: int, pid: int) -> str:
    s = st.session_state
    k = (aid, pid)
    return "presente" if k in s.asistencias else "ausente" if k in s.ausencias else "sin marcar"


def ciclar_asistencia(aid: int, pid: int) -> None:
    """Círculo blanco → verde (presente) → rojo (ausente) → blanco."""
    s = st.session_state
    k = (aid, pid)
    if k in s.asistencias:
        s.asistencias.discard(k)
        s.ausencias.add(k)
    elif k in s.ausencias:
        s.ausencias.discard(k)
    else:
        s.asistencias.add(k)


def crear_actividad(tipo: str, nombre: str, fecha: date, modalidad: str) -> None:
    s = st.session_state
    aid = max([a["id"] for a in s.actividades] + [0]) + 1
    s.actividades.append(dict(id=aid, tipo=tipo, nombre=nombre or tipo, fecha=fecha, modalidad=modalidad))
    registrar_log("Nueva actividad", f"Se creó '{nombre or tipo}' ({tipo}, {modalidad.lower()}) para el {fecha_txt(fecha)}.")


def pct_asistencia(pid: int, acts: list[dict]) -> int | None:
    """% de presencias sobre las actividades que SÍ fueron marcadas (blanco = no cuenta)."""
    marcadas = [a for a in acts if marca(a["id"], pid) != "sin marcar"]
    if not marcadas:
        return None
    return round(100 * sum(marca(a["id"], pid) == "presente" for a in marcadas) / len(marcadas))


def pct_actividades(acts: list[dict], participantes: list[dict]) -> int | None:
    pres = aus = 0
    for a in acts:
        for p in participantes:
            m = marca(a["id"], p["id"])
            pres += m == "presente"
            aus += m == "ausente"
    return round(100 * pres / (pres + aus)) if pres + aus else None


def asistencia_promedio() -> int:
    vals = [v for v in (pct_asistencia(p["id"], st.session_state.actividades)
                        for p in st.session_state.participantes if p["estado"] == "Activa") if v is not None]
    return round(sum(vals) / len(vals)) if vals else 0


def csv_asistencia(acts: list[dict]) -> bytes:
    filas = []
    for a in sorted(acts, key=lambda x: x["fecha"]):
        for p in st.session_state.participantes:
            m = marca(a["id"], p["id"])
            if m != "sin marcar" or p["estado"] == "Activa":
                filas.append([fecha_txt(a["fecha"]), a["tipo"], a["nombre"], a["modalidad"], p["nombre"], p["rol"],
                              {"presente": "Presente", "ausente": "Ausente", "sin marcar": "Sin marcar"}[m]])
    return a_csv(["Fecha", "Tipo", "Actividad", "Modalidad", "Participante", "Rol", "Asistencia"], filas)


# ───────────────────────────────── DIÁLOGOS ──────────────────────────────────
@st.dialog("Registrar pago", width="large")
def dialogo_pago() -> None:
    elegibles = [p for p in st.session_state.participantes if estado_pago(p) != "Becado (exento)"]
    opciones = {f"{p['nombre']} · {p['rol']}": p["id"] for p in elegibles}
    sel = st.selectbox("Participante", list(opciones))
    c1, c2 = st.columns(2)
    monto = c1.number_input("Monto ($)", min_value=0, step=1000, value=PRECIO_DEMO)
    metodo = c2.selectbox("Método de pago", ["Transferencia", "PayPal", "Voucher"])
    c3, c4 = st.columns(2)
    fecha = c3.date_input("Fecha de pago", value=hoy(), format="DD/MM/YYYY")
    meses = c4.selectbox("Duración de la membresía (meses)", [1, 3, 6, 12], index=2)
    archivo = st.file_uploader("Comprobante o voucher (imagen o PDF)", type=["png", "jpg", "jpeg", "pdf"])
    if st.button("Guardar pago", key="btn_guardar_pago"):
        if monto <= 0:
            st.error("El monto debe ser mayor que 0.")
        elif archivo is None:
            st.error("Sube el comprobante como evidencia del pago.")
        else:
            registrar_pago(opciones[sel], int(monto), metodo, fecha, int(meses), archivo)
            st.session_state.flash = f"Pago registrado para {sel.split(' · ')[0]}."
            st.rerun()


@st.dialog("Registrar donación", width="large")
def dialogo_donacion() -> None:
    donante = st.text_input("Nombre del donante / institución", placeholder="Ej. Fundación Amigos")
    c1, c2 = st.columns(2)
    monto = c1.number_input("Monto donado ($)", min_value=0, step=5000, value=50000)
    fecha = c2.date_input("Fecha de donación", value=hoy(), format="DD/MM/YYYY")
    archivo = st.file_uploader("Comprobante de donación (opcional)", type=["png", "jpg", "jpeg", "pdf"])
    if st.button("Guardar donación", key="btn_guardar_donacion"):
        if not donante.strip():
            st.error("Indica el nombre del donante.")
        elif monto <= 0:
            st.error("El monto debe ser mayor que 0.")
        else:
            registrar_donacion(donante.strip(), int(monto), fecha, archivo)
            st.session_state.flash = f"Donación registrada de {donante}."
            st.rerun()


def mostrar_archivo(nombre: str, datos: bytes, etiqueta: str) -> None:
    if nombre.lower().endswith(("png", "jpg", "jpeg")):
        st.image(datos)
    else:
        st.download_button(etiqueta, datos, file_name=nombre)


@st.dialog("Comprobante de pago")
def dialogo_ver(pid: int) -> None:
    c = ultimo_comprobante(pid)
    if not c:
        st.info("Esta participante no tiene comprobante cargado.")
        return
    st.caption(f"{participante(pid)['nombre']} · {fecha_txt(c['fecha'])} · {plata(c['monto'])} · {c['metodo']}")
    mostrar_archivo(c["comprobante_nombre"], c["comprobante"], "Descargar comprobante")


@st.dialog("Historial financiero", width="large")
def dialogo_historial_fin() -> None:
    tabs = st.tabs(["Membresías", "Donaciones"])
    with tabs[0]:
        hist = sorted(st.session_state.pagos, key=lambda x: (x["fecha"], x["id"]), reverse=True)
        html(tabla_html(["Fecha", "Participante", "Monto", "Método", "Comprobante"],
                        [[fecha_txt(x["fecha"]), escape(participante(x["participante_id"])["nombre"]), plata(x["monto"]),
                          escape(x["metodo"]), "Sí" if x["comprobante"] else "—"] for x in hist]))
    with tabs[1]:
        dones = sorted(st.session_state.donaciones, key=lambda x: x["fecha"], reverse=True)
        html(tabla_html(["Fecha", "Donante", "Monto", "Comprobante"],
                        [[fecha_txt(x["fecha"]), escape(x["donante"]), plata(x["monto"]), "Sí" if x["comprobante"] else "—"]
                         for x in dones]))


@st.dialog("Carta de compromiso")
def dialogo_ver_carta(pid: int) -> None:
    p = participante(pid)
    st.caption(f"{p['nombre']} · {p['carta_nombre']}")
    mostrar_archivo(p["carta_nombre"], p["carta"], "Descargar carta")


@st.dialog("Subir carta de compromiso")
def dialogo_subir_carta(pid: int) -> None:
    st.caption(participante(pid)["nombre"])
    archivo = st.file_uploader("Imagen o documento", type=CARTA_TIPOS, key=f"carta_dlg_{pid}")
    if st.button("Guardar carta", key=f"btn_carta_{pid}"):
        if archivo is None:
            st.error("Selecciona un archivo.")
        else:
            p = participante(pid)
            p["carta_nombre"], p["carta"] = archivo.name, archivo.getvalue()
            registrar_log("Subida de documento", f"Se cargó la carta de compromiso de {p['nombre']}.",
                          archivo.name, archivo.getvalue())
            st.session_state.flash = f"Carta de compromiso guardada para {p['nombre']}."
            st.rerun()


@st.dialog("Nueva actividad", width="large")
def dialogo_actividad() -> None:
    c1, c2 = st.columns(2)
    tipo = c1.selectbox("Tipo de actividad", TIPOS_ACTIVIDAD)
    modalidad = c2.selectbox("Modalidad", MODALIDADES)
    nombre = st.text_input("Nombre de la actividad (opcional)", placeholder="Ej. Marca personal")
    fecha = st.date_input("Fecha", value=hoy(), format="DD/MM/YYYY")
    if st.button("Crear actividad", key="btn_crear_actividad"):
        crear_actividad(tipo, nombre.strip(), fecha, modalidad)
        st.session_state.flash = f"Actividad creada para el {fecha_txt(fecha)}."
        st.rerun()


@st.dialog("Revocar beca")
def dialogo_revocar(pid: int) -> None:
    st.caption(participante(pid)["nombre"])
    motivo = st.text_input("Motivo de la revocación", placeholder="Ej. No cumple la asistencia mínima")
    if st.button("Revocar beca", key=f"btn_revocar_{pid}"):
        if not motivo.strip():
            st.error("Indica el motivo para dejar registro.")
        else:
            revocar_beca(pid, motivo.strip())
            st.session_state.flash = f"Beca revocada a {participante(pid)['nombre']}."
            st.rerun()


@st.dialog("Renovar beca")
def dialogo_renovar(pid: int) -> None:
    st.caption(participante(pid)["nombre"])
    c1, c2 = st.columns(2)
    inicio = c1.date_input("Nuevo inicio", value=hoy(), format="DD/MM/YYYY")
    termino = c2.date_input("Nuevo término", value=sumar_meses(hoy(), 6), format="DD/MM/YYYY")
    if st.button("Renovar beca", key=f"btn_renovar_{pid}"):
        if termino <= inicio:
            st.error("El término debe ser posterior al inicio.")
        else:
            asignar_beca(pid, "Renovación de beca", inicio, termino)
            st.session_state.flash = f"Beca renovada a {participante(pid)['nombre']}."
            st.rerun()


# ─────────────────────────────────── PÁGINAS ─────────────────────────────────
def pagina_panel() -> None:
    h = hoy()
    s = st.session_state
    P, filas = s.participantes, filas_pagos()
    activas = sum(p["estado"] == "Activa" for p in P)
    alerta = [f for f in filas if f["vence"] and f["estado"] != "Becado (exento)" and 0 <= (f["vence"] - h).days <= DIAS_ALERTA]
    vencidas = [f for f in filas if f["estado"] == "Vencido"]
    ultimas = [b for b in (beca_actual(p["id"]) for p in P) if b]
    becas_act = sum(estado_beca(b) == "Activa" for b in ultimas)
    becas_rev = sum(b["estado"] == "Revocada" for b in ultimas)
    k = (h.year, h.month)
    ing_mes, don_mes = total_mes(s.pagos, k), total_mes(s.donaciones, k)

    hero("Panel general", f"¡Hola, {NOMBRE_USUARIA}!", "Resumen de participantes, membresías e ingresos de la fundación.",
         [("Participantes activas", activas), ("Por vencer", len(alerta)), ("Vencidas", len(vencidas))])

    metricas = [
        ("users", "Participantes activas", str(activas), f"de {len(P)} registradas"),
        ("clock", f"Por vencer ({DIAS_ALERTA} días)", str(len(alerta)), f"{len(vencidas)} membresías vencidas"),
        ("check", "Asistencia promedio", f"{asistencia_promedio()}%", "sobre actividades marcadas"),
        ("award", "Becas activas", str(becas_act), f"{becas_rev} revocadas"),
        ("trend", "Ingresos del mes", plata(ing_mes + don_mes), f"Membresías {plata(ing_mes)} · Donac. {plata(don_mes)}"),
    ]
    for col, m in zip(st.columns(5), metricas):
        celda(col, mc(*m))

    izq, der = st.columns([1.6, 1])
    with izq, st.container(key="card_ingresos"):
        meses = ultimos_meses(6)
        html('<div class="sub">Ingresos de los últimos 6 meses</div><div class="muted">Membresías y donaciones en pesos chilenos (CLP)</div>')
        html(grafico_barras([etiqueta_mes(m) for m in meses],
                            [("Membresías", [total_mes(s.pagos, m) for m in meses], C_GOLD2),
                             ("Donaciones", [total_mes(s.donaciones, m) for m in meses], C_INK)]))
    with der, st.container(key="card_por_vencer"):
        html('<div class="sub">Membresías por vencer</div><div class="muted">Próximos 30 días y ya vencidas</div>')
        prox = sorted([f for f in filas if f["vence"] and f["estado"] != "Becado (exento)" and (f["vence"] - h).days <= 30],
                      key=lambda f: f["vence"])
        if not prox:
            st.caption("No hay vencimientos próximos.")
        for f in prox[:6]:
            d = (f["vence"] - h).days
            if d < 0:
                etiqueta, clase = f"vencida hace {-d} d", "c-vencido"
            else:
                etiqueta, clase = f"{d} días", "c-vencer" if d <= DIAS_ALERTA else ""
            html(f'<div style="display:flex;justify-content:space-between;align-items:center;padding:6px 0;border-bottom:1px solid #F3ECCF">'
                 f'<span style="font-size:14px">{escape(f["p"]["nombre"])}</span><span class="chip {clase}">{etiqueta}</span></div>')
        if st.button("Enviar recordatorio", key="btn_recordatorio", width="stretch"):
            st.toast(f"Recordatorio registrado para {len(prox)} participante(s). (Simulado: aún no se envían correos.)")

def pagina_registro() -> None:
    s = st.session_state
    P = s.participantes
    hero("Participantes", "Registro de participantes", "Alta de mentoras, emprendedoras, becadas y redes de apoyo.",
         [("Registradas", len(P)), ("Mentoras", sum(p["rol"] == "Mentora" for p in P)),
          ("Cartas pendientes", sum(p["rol"] == "Mentora" and not p["carta"] for p in P))])
    izq, der = st.columns([1.5, 1])
    with izq, st.container(key="card_form"):
        html('<div class="sub">Nueva participante</div>')
        c1, c2 = st.columns(2)
        c1.text_input("Nombre completo", placeholder="Ej. María Pérez", key="f_nombre")
        c2.text_input("Correo electrónico", placeholder="nombre@correo.com", key="f_correo")
        c1.text_input("Teléfono", placeholder="+56 9 0000 0000", key="f_tel")
        c2.selectbox("País", PAISES, key="f_pais")
        c1.selectbox("Rol", ROLES, index=None, placeholder="Elige un rol", key="f_rol")
        st.text_area("Descripción profesional", placeholder="Trayectoria y especialidad", height=100, key="f_desc")
        es_mentora = s.get("f_rol") == "Mentora"
        st.file_uploader(
            "Carta de compromiso (obligatoria para mentoras)" if es_mentora else "Carta de compromiso (opcional)",
            type=CARTA_TIPOS, key=f"f_carta_{s.carta_n}",
            help="Puedes subirla ahora o después desde la lista de participantes.")
        st.button("Guardar participante", key="btn_guardar_part", on_click=guardar_participante)
        msg = s.pop("f_msg", None)
        if msg:
            (st.success if msg[0] == "ok" else st.error)(msg[1])
    with der, st.container(key="card_clasif"):
        sel = s.get("f_rol")
        cajas = "".join(f'<div class="clasif {"sel" if r == sel else ""}"><span class="chip">{r}</span>'
                        f'<div>{SIGUIENTE_PASO[r][1]}</div></div>' for r in ROLES)
        html(f'<div class="sub" style="margin-bottom:8px">Clasificación y siguiente paso</div>{cajas}'
             '<div class="info">El sistema valida el correo: formato correcto y sin duplicados.</div>')

    with st.container(key="card_lista"):
        html(f'<div class="sub">Participantes registradas ({len(P)})</div>')
        f1, f2, _ = st.columns([2, 1.2, 2])
        q = f1.text_input("Buscar", placeholder="Buscar por nombre o correo", key="q_part", label_visibility="collapsed")
        rol_f = f2.selectbox("Rol", ["Todos los roles"] + ROLES, key="q_rol", label_visibility="collapsed")
        anchos = [1.5, 1.9, 1.0, 1.4, 1.5, 1.3]
        cabecera(anchos, ["Nombre", "Correo", "País", "Rol", "Estado", "Carta de compromiso"])
        lista = [p for p in reversed(P) if (rol_f == "Todos los roles" or p["rol"] == rol_f)
                 and (not q or q.lower() in p["nombre"].lower() or q.lower() in p["correo"].lower())]
        if not lista:
            st.caption("No hay participantes que coincidan con la búsqueda.")
        for p in lista:
            cols = st.columns(anchos, vertical_alignment="center")
            td(cols[0], escape(p["nombre"]))
            td(cols[1], escape(p["correo"]))
            td(cols[2], escape(p.get("pais", "Chile")))
            td(cols[3], f'<span class="chip">{escape(p["rol"])}</span>')
            td(cols[4], escape(p["estado"]))
            if p["carta"]:
                if cols[5].button("Ver carta", key=f"mini_carta_{p['id']}"):
                    dialogo_ver_carta(p["id"])
            else:
                etiqueta_carta = "Subir carta" if p["rol"] == "Mentora" else "Subir carta (opcional)"
                if cols[5].button(etiqueta_carta, key=f"mini_subir_{p['id']}"):
                    dialogo_subir_carta(p["id"])
            sep()


def pagina_pagos() -> None:
    s = st.session_state
    h = hoy()
    filas = filas_pagos()
    k = (h.year, h.month)
    hero("Finanzas", "Membresías, pagos y donaciones", "Control de vigencias, comprobantes y aportes recibidos.",
         [("Ingresos del mes", plata(total_mes(s.pagos, k))), ("Donaciones del mes", plata(total_mes(s.donaciones, k)))])

    b1, b2, b3, _ = st.columns([1, 1, 1.1, 2])
    if b1.button("+ Registrar pago", key="btn_nuevo_pago", width="stretch"):
        dialogo_pago()
    if b2.button("+ Registrar donación", key="btn_nueva_donacion", width="stretch"):
        dialogo_donacion()
    if b3.button("Historial financiero", key="btn_hist_fin", width="stretch"):
        dialogo_historial_fin()

    cuenta = {e: sum(f["estado"] == e for f in filas) for e in ESTADOS}
    for col, m in zip(st.columns(4), [("check", "Al día", str(cuenta["Pagado"]), "membresías vigentes"),
                                      ("clock", "Por vencer", str(cuenta["Por vencer"]), f"vencen en {DIAS_ALERTA} días o menos"),
                                      ("alert", "Vencidas", str(cuenta["Vencido"]), "requieren seguimiento"),
                                      ("award", "Becadas (exentas)", str(cuenta["Becado (exento)"]), "no pagan membresía")]):
        celda(col, mc(*m))

    with st.container(key="card_tabla"):
        c1, c2 = st.columns([1.3, 3])
        filtro = c1.selectbox("Estado", ["Todos los estados"] + ESTADOS, key="f_estado_pago", label_visibility="collapsed")
        celda(c2, f'<div class="info">Aviso en el panel cuando falten {DIAS_ALERTA} días o menos para el vencimiento.</div>')
        anchos = [2, 1.5, 1.1, 1.2, 1.5, 1.2]
        cabecera(anchos, ["Participante", "Rol", "Inicio", "Vencimiento", "Estado", "Comprobante"])
        for f in filas:
            if filtro != "Todos los estados" and f["estado"] != filtro:
                continue
            p = f["p"]
            cols = st.columns(anchos, vertical_alignment="center")
            td(cols[0], escape(p["nombre"]))
            td(cols[1], f'<span class="chip">{escape(p["rol"])}</span>')
            td(cols[2], fecha_txt(f["inicio"]))
            td(cols[3], fecha_txt(f["vence"]))
            td(cols[4], chip(f["estado"]))
            if ultimo_comprobante(p["id"]):
                if cols[5].button("Ver archivo", key=f"mini_ver_{p['id']}"):
                    dialogo_ver(p["id"])
            else:
                td(cols[5], "—")
            sep()


def pagina_asistencia() -> None:
    s = st.session_state
    acts_all = sorted(s.actividades, key=lambda a: (a["fecha"], a["id"]))
    hero("Asistencia", "Control de asistencia", "Marca a cada participante por actividad con un clic.",
         [("Actividades", len(acts_all)), ("Asistencia promedio", f"{asistencia_promedio()}%")])

    c1, c2, c3, _ = st.columns([1.1, 1.3, 1.2, 1.6], vertical_alignment="center")
    if c1.button("+ Nueva actividad", key="btn_nueva_actividad", width="stretch"):
        dialogo_actividad()
    n = c2.selectbox("Mostrar", [4, 6, 8], index=1, key="asis_n", format_func=lambda v: f"Últimas {v} actividades",
                     label_visibility="collapsed")
    c3.download_button("Exportar CSV", csv_asistencia(acts_all), file_name="asistencia.csv", mime="text/csv",
                       key="btn_exportar_asistencia", width="stretch")
    if not acts_all:
        st.info("Primero crea una actividad para generar una columna de fecha.")
        return
    visibles = acts_all[-n:]
    widths = [2.4] + [1] * len(visibles)
    with st.container(key="card_asis"):
        header = st.columns(widths, vertical_alignment="center")
        celda(header[0], '<div class="att-head">Participante</div>')
        for col, a in zip(header[1:], visibles):
            celda(col, f'<div class="att-title"><div class="t">{escape(a["nombre"])}</div>{fecha_corta(a["fecha"])}<br>'
                       f'<span class="chip" style="font-size:11px">{escape(a["tipo"])} · {escape(a["modalidad"])}</span></div>')
        html('<div class="hline"></div>')
        for p in s.participantes:
            cols = st.columns(widths, vertical_alignment="center")
            celda(cols[0], f'<div style="font-weight:700;padding:6px 0;font-size:14px">{escape(p["nombre"])}'
                           f'<div class="muted" style="font-weight:400">{escape(p["rol"])} · {escape(p.get("pais", "Chile"))}</div></div>')
            for col, a in zip(cols[1:], visibles):
                m = marca(a["id"], p["id"])
                pref, lbl = {"presente": ("attp", "✓"), "ausente": ("atta", "✕"), "sin marcar": ("attn", "\u00a0")}[m]
                col.button(lbl, key=f"{pref}_{a['id']}_{p['id']}", on_click=ciclar_asistencia, args=(a["id"], p["id"]))
            sep()
        pie = st.columns(widths, vertical_alignment="center")
        celda(pie[0], '<div class="att-head" style="padding:8px 0">Presentes</div>')
        for col, a in zip(pie[1:], visibles):
            pres = sum(marca(a["id"], p["id"]) == "presente" for p in s.participantes)
            celda(col, f'<div class="att-title">{pres} / {len(s.participantes)}</div>')


def formulario_beca() -> None:
    n = st.session_state.beca_n
    con_beca = {b["participante_id"] for b in st.session_state.becas if estado_beca(b) == "Activa"}
    elegibles = [p["id"] for p in st.session_state.participantes if p["id"] not in con_beca]
    pid = st.selectbox("Participante", elegibles, index=None, placeholder="Elige a la participante", key=f"b_p{n}",
                       format_func=lambda i: f"{participante(i)['nombre']} · {participante(i)['rol']}")
    motivo = st.text_input("Motivo", placeholder="Describe el motivo", key=f"b_m{n}")
    c1, c2 = st.columns(2)
    inicio = c1.date_input("Inicio de vigencia", value=hoy(), format="DD/MM/YYYY", key=f"b_i{n}")
    termino = c2.date_input("Término de vigencia", value=sumar_meses(hoy(), 6), format="DD/MM/YYYY", key=f"b_t{n}")
    if st.button("Asignar beca", key="btn_beca_asignar", width="stretch"):
        if pid is None or not motivo.strip():
            st.error("Elige a la participante e indica el motivo.")
        elif termino <= inicio:
            st.error("El término debe ser posterior al inicio.")
        else:
            asignar_beca(pid, motivo.strip(), inicio, termino)
            st.session_state.beca_n += 1
            st.session_state.flash = f"Beca asignada a {participante(pid)['nombre']}."
            st.rerun()


def pagina_becas() -> None:
    s = st.session_state
    registros = [(p, beca_actual(p["id"])) for p in s.participantes]
    registros = sorted([(p, b) for p, b in registros if b], key=lambda x: (estado_beca(x[1]) != "Activa", x[0]["id"]))
    activas = sum(estado_beca(b) == "Activa" for _, b in registros)
    hero("Becas", "Gestión de becas", "Asignación, vigencia y seguimiento de asistencia de las becadas.",
         [("Becas activas", activas), ("Inactivas", len(registros) - activas)])

    izq, der = st.columns([2.15, 1])
    with izq, st.container(key="card_becas_tabla"):
        html('<div class="sub">Becadas</div>')
        anchos = [1.9, 1.1, 2.1, 1.3, 1.1, 1.1]
        cabecera(anchos, ["Nombre", "Asignación", "Vigencia (inicio – fin)", "% asistencia", "Estado", "Acción"])
        if not registros:
            st.caption("Todavía no hay becas registradas.")
        for p, b in registros:
            est = estado_beca(b)
            hasta = min(b["termino"], hoy())
            pct = pct_asistencia(p["id"], [a for a in s.actividades if b["inicio"] <= a["fecha"] <= hasta])
            cols = st.columns(anchos, vertical_alignment="center")
            td(cols[0], escape(p["nombre"]))
            td(cols[1], fecha_corta(b["asignacion"]), "nw")
            td(cols[2], f'{fecha_corta(b["inicio"])} – {fecha_corta(b["termino"])}', "nw")
            celda(cols[3], f'<div class="td">{barra(pct)}</div>')
            td(cols[4], chip(est))
            if est == "Activa":
                if cols[5].button("Revocar", key=f"mini_rev_{p['id']}"):
                    dialogo_revocar(p["id"])
            elif cols[5].button("Renovar", key=f"mini_ren_{p['id']}", help=detalle_inactiva(b)):
                dialogo_renovar(p["id"])
            sep()
        st.caption("«Inactiva»: beca revocada o con la vigencia terminada. El % de asistencia se mide dentro de la vigencia.")
    with der, st.container(key="card_becas_form"):
        html('<div class="sub">Asignar nueva beca</div><div class="muted">Para revocar o renovar usa los botones de la tabla.</div>')
        formulario_beca()


def nivel_chip(pct: int | None) -> str:
    if pct is None:
        return '<span class="chip c-inact">Sin datos</span>'
    if pct >= 80:
        return '<span class="chip c-pagado">Óptimo</span>'
    if pct >= 50:
        return '<span class="chip c-vencer">Regular</span>'
    return '<span class="chip c-vencido">En riesgo</span>'


def pagina_seguimiento() -> None:
    s = st.session_state
    P, acts = s.participantes, s.actividades
    pcts = {p["id"]: pct_asistencia(p["id"], acts) for p in P}
    validos = [v for v in pcts.values() if v is not None]
    hero("Seguimiento", "Seguimiento e impacto", "Participación de cada persona en las actividades registradas.",
         [("Asistencia promedio", f"{round(sum(validos) / len(validos)) if validos else 0}%"),
          ("En riesgo (<50%)", sum(v < 50 for v in validos)), ("Óptimas (≥80%)", sum(v >= 80 for v in validos))])
    with st.container(key="card_seg"):
        f1, _ = st.columns([1.3, 3])
        rol_f = f1.selectbox("Rol", ["Todos los roles"] + ROLES, key="seg_rol", label_visibility="collapsed")
        anchos = [2, 1.5, 1.8, 1.3, 2.4, 1.2]
        cabecera(anchos, ["Participante", "Rol", "Estado actual", "Marcadas", "Asistencia global", "Nivel"])
        for p in sorted(P, key=lambda x: (pcts[x["id"]] is None, pcts[x["id"]] if pcts[x["id"]] is not None else 0)):
            if rol_f != "Todos los roles" and p["rol"] != rol_f:
                continue
            marcadas = sum(marca(a["id"], p["id"]) != "sin marcar" for a in acts)
            cols = st.columns(anchos, vertical_alignment="center")
            td(cols[0], escape(p["nombre"]))
            td(cols[1], f'<span class="chip">{escape(p["rol"])}</span>')
            td(cols[2], escape(p["estado"]))
            td(cols[3], f"{marcadas} de {len(acts)}")
            celda(cols[4], f'<div class="td">{barra(pcts[p["id"]])}</div>')
            td(cols[5], nivel_chip(pcts[p["id"]]))
            sep()
        st.caption("Ordenado de menor a mayor asistencia para detectar rápido a quién acompañar.")

def pagina_reportes() -> None:
    s = st.session_state
    h = hoy()
    P = s.participantes
    k = (h.year, h.month)
    activas = [p for p in P if p["estado"] == "Activa"]
    hero("Reportes", "Resumen rápido", "Indicadores clave del mes. El análisis completo está en Data Studio.")

    for col, m in zip(st.columns(4), [
        ("users", "Participantes registradas", str(len(P)), f"{len(activas)} activas"),
        ("trend", "Ingresos del mes", plata(total_mes(s.pagos, k) + total_mes(s.donaciones, k)), "membresías + donaciones"),
        ("check", "Asistencia promedio", f"{asistencia_promedio()}%", "sobre actividades marcadas"),
        ("alert", "Membresías vencidas", str(sum(estado_pago(p) == "Vencido" for p in P)), "al día de hoy"),
    ]):
        celda(col, mc(*m))

    with st.container(key="card_rep_desc"):
        html('<div class="sub">Análisis detallado</div>'
             '<div class="muted">Gráficos, cruces y exportaciones se consultan en el informe de Data Studio.</div>')
        st.link_button("Abrir informe en Data Studio", URL_DATASTUDIO)

def clase_accion(accion: str) -> str:
    a = accion.lower()
    if "pago" in a or "donaci" in a:
        return "c-vencer"
    if "beca" in a:
        return "c-exento"
    if "actividad" in a or "asistencia" in a:
        return "c-activa"
    return "c-ink"


def pagina_historial() -> None:
    s = st.session_state
    logs = s.get("historial_logs", [])
    h = hoy()
    hero("Auditoría", "Historial de acciones", "Registro cronológico de lo que hace el equipo, con respaldos descargables.",
         [("Acciones registradas", len(logs)), ("Hoy", sum(x["ts"].date() == h for x in logs))])

    with st.container(key="card_hist_filtros"):
        f1, f2, f3 = st.columns([1.3, 2, 1], vertical_alignment="center")
        tipos = sorted({x["accion"] for x in logs})
        tipo = f1.selectbox("Tipo de acción", ["Todas las acciones"] + tipos, key="hist_tipo", label_visibility="collapsed")
        q = f2.text_input("Buscar", placeholder="Buscar en el detalle (nombre, monto, motivo…)", key="hist_q", label_visibility="collapsed")
        f3.download_button("Exportar CSV", a_csv(["Fecha", "Hora", "Acción", "Detalle"],
                                                 [[fecha_txt(x["ts"].date()), x["ts"].strftime("%H:%M"), x["accion"], x["detalle"]] for x in logs]),
                           file_name="historial_acciones.csv", mime="text/csv", key="dl_hist_csv", width="stretch")

    vistos = [x for x in logs if (tipo == "Todas las acciones" or x["accion"] == tipo) and (not q or q.lower() in x["detalle"].lower())][:100]
    with st.container(key="card_hist"):
        if not vistos:
            st.info("No hay acciones que coincidan con el filtro.")
        dia_actual = None
        for x in vistos:
            d = x["ts"].date()
            if d != dia_actual:
                dia_actual = d
                etq = "Hoy" if d == h else "Ayer" if d == h - timedelta(days=1) else fecha_larga(d)
                html(f'<div class="dg">{etq}</div><div class="hline"></div>')
            c1, c2, c3, c4 = st.columns([0.7, 1.9, 4.2, 1.5], vertical_alignment="center")
            td(c1, f'<b>{x["ts"].strftime("%H:%M")}</b>', "nw")
            td(c2, f'<span class="chip {clase_accion(x["accion"])}">{escape(x["accion"])}</span>')
            td(c3, escape(x["detalle"]))
            if x["archivo_bytes"] and x["archivo_nombre"]:
                c4.download_button("Descargar respaldo", x["archivo_bytes"], file_name=x["archivo_nombre"], key=f"dl_log_{x['id']}")
            else:
                td(c4, '<span class="muted">Sin archivo</span>')
            sep()


# ─────────────────────────────── NAVEGACIÓN Y MAIN ───────────────────────────
iniciar_datos()
st.session_state.setdefault("pagina", "Panel")
st.session_state.setdefault("carta_n", 0)
st.session_state.setdefault("beca_n", 0)


def ir(destino: str) -> None:
    st.session_state.pagina = destino


with st.sidebar:
    logo = b64("logo.png")
    html(f'<div class="logo-box">{f"<img src={chr(34)}{logo}{chr(34)}>" if logo else "Créete el Cuento"}</div>')
    for grupo, items in NAV_GRUPOS:
        html(f'<div class="nav-g">{grupo}</div>')
        for nombre, icono_nav in items:
            activa = st.session_state.pagina == nombre
            st.button(nombre, key=f"{'navon' if activa else 'nav'}_{nombre}", icon=f":material/{icono_nav}:",
                      on_click=ir, args=(nombre,), width="stretch")
    iniciales = "".join(w[0] for w in NOMBRE_USUARIA.strip("[]").split()[:2]).upper() or "CC"
    html(f'<div class="user-card"><div class="av">{escape(iniciales)}</div><div><b>{escape(NOMBRE_USUARIA)}</b><span>Coordinación</span></div></div>')

if "flash" in st.session_state:
    st.toast(st.session_state.pop("flash"))

PAGINAS = {
    "Panel": pagina_panel,
    "Participantes": pagina_registro,
    "Pagos": pagina_pagos,
    "Asistencia": pagina_asistencia,
    "Becas": pagina_becas,
    "Seguimiento": pagina_seguimiento,
    "Reportes": pagina_reportes,
    "Historial": pagina_historial,
}
PAGINAS[st.session_state.pagina]()