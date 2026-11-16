"""
Créete el Cuento · Sistema de gestión interno (prototipo funcional)

Páginas: Panel · Participantes · Pagos · Asistencia · Becas · Seguimiento · Reportes · Historial.
Participantes y actividades usan Supabase; pagos y comprobantes se guardan en
Supabase y Storage. Otros módulos conservan estado de sesión local.

Ejecutar:  streamlit run src/lineacodigo.py
"""
from __future__ import annotations

import base64
import csv
import io
import re
import os

from httpx import HTTPError
from supabase import Client, SupabaseException
from supabase_auth.errors import AuthApiError
from dotenv import load_dotenv
import streamlit as st
from auth_supabase import iniciar_sesion as iniciar_sesion_supabase
from becas_estado import actividades_de_beca, beca_vigente, becas_para_listado, fechas_pago
from becas_supabase import (
    cargar_becas as cargar_becas_db,
    guardar_beca as guardar_beca_db,
    revocar_beca as revocar_beca_db,
)
from donaciones_supabase import (
    cargar_donaciones as cargar_donaciones_db,
    guardar_donacion as guardar_donacion_db,
)
from participantes_estado import estado_participante
from pagos_supabase import (
    cargar_pagos as cargar_pagos_db,
    crear_membresias,
    descargar_comprobante,
    guardar_pago as guardar_pago_db,
    sumar_meses,
)

# Cargar variables de entorno
load_dotenv()

def configuracion(nombre: str, predeterminado: str | None = None) -> str | None:
    """Lee secretos de Streamlit Cloud o, en local, variables de entorno/.env."""
    try:
        valor = st.secrets.get(nombre)
    except Exception:  # Streamlit lanza un error si no hay secrets.toml local.
        valor = None
    return valor or os.environ.get(nombre, predeterminado)


# Conectar con Supabase
supabase_url = configuracion("SUPABASE_URL")
supabase_key = configuracion("SUPABASE_KEY")
SUPABASE_PAYMENTS_BUCKET = configuracion("SUPABASE_PAYMENTS_BUCKET", "comprobantes-pagos")

from datetime import date, datetime, timedelta
from html import escape
from pathlib import Path

try:
    from zoneinfo import ZoneInfo
    TZ = ZoneInfo("America/Santiago")
except Exception:  # noqa: BLE001
    TZ = None


# ─────────────────────────────── CONFIGURACIÓN ───────────────────────────────
st.set_page_config(page_title="Créete el Cuento · Gestión", page_icon="💡", layout="wide")


def cliente_supabase() -> Client:
    cliente = st.session_state.get("_cliente_supabase")
    if not isinstance(cliente, Client):
        raise RuntimeError("Inicia sesión con Supabase Auth para acceder a los datos.")
    return cliente


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
ESTADOS = ["Pendiente", "Pagado", "Vencido", "Por vencer", "Becado (exento)"]
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
             "Becada": "c-exento", "Activa": "c-activa", "Inactiva": "c-inact"}.get(estado, "")
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
        response = cliente_supabase().table("Participantes").select("*").execute()
        return response.data if response.data else []
    except Exception as e:
        print(f"Error al cargar participantes: {e}")
        return []

# ─────────────────────────────────────────────────────────────────────────────
# FUNCIONES PARA ACTIVIDADES Y ASISTENCIA (SUPABASE)
# ─────────────────────────────────────────────────────────────────────────────

def cargar_actividades_desde_db() -> list:
    try:
        response = cliente_supabase().table("Actividades").select("*").order("fecha", desc=True).execute()
        return response.data if response.data else []
    except Exception as e:
        print(f"Error al cargar actividades: {e}")
        return []

def guardar_actividad_en_db(nombre: str, tipo: str, modalidad: str, fecha: date, descripcion: str = "") -> dict | None:
    try:
        data = {
            "nombre": nombre,
            "tipo": tipo,
            "modalidad": modalidad,
            "fecha": fecha.isoformat(),
            "descripcion": descripcion
        }
        response = cliente_supabase().table("Actividades").insert(data).execute()
        return response.data[0] if response.data else None
    except Exception as e:
        print(f"Error al guardar actividad: {e}")
        return None

def cargar_asistencias_desde_db() -> tuple[set, set]:
    presentes, ausentes = set(), set()
    try:
        response = cliente_supabase().table("Asistencia_actividad").select("actividad_id, participante_id, asistio").execute()
        for r in response.data:
            key = (r["actividad_id"], r["participante_id"])
            if r["asistio"]: presentes.add(key)
            else: ausentes.add(key)
    except Exception as e:
        print(f"Error al cargar asistencias: {e}")
    return presentes, ausentes

def guardar_asistencia_en_db(actividad_id: int, participante_id: int, asistio: bool) -> bool:
    try:
        data = {"actividad_id": actividad_id, "participante_id": participante_id, "asistio": asistio}
        cliente_supabase().table("Asistencia_actividad").upsert(data, on_conflict="actividad_id,participante_id").execute()
        return True
    except Exception as e:
        print(f"Error al guardar asistencia: {e}")
        return False

def borrar_asistencia_db(actividad_id: int, participante_id: int) -> bool:
    """Elimina el registro de asistencia cuando se desmarca (vuelve a blanco)."""
    try:
        cliente_supabase().table("Asistencia_actividad").delete().eq("actividad_id", actividad_id).eq("participante_id", participante_id).execute()
        return True
    except Exception as e:
        print(f"Error al borrar asistencia: {e}")
        return False

def iniciar_datos() -> None:
    """Inicializa datos desde Supabase."""
    requeridos = (
        "participantes", "actividades", "asistencias", "ausencias", "pagos", "membresias",
        "pagos_db_ok", "becas", "becas_db_ok", "donaciones", "donaciones_db_ok",
        "historial_logs",
    )
    if all(key in st.session_state for key in requeridos):
        return  # Ya está inicializado
    
    s = st.session_state
    
    # 1. Participantes
    s.participantes = []
    for p in cargar_participantes_desde_db():
        s.participantes.append({
            "id": p["id"], "nombre": p["nombre"], "correo": p["correo"],
            "telefono": p.get("telefono", ""), "pais": p.get("pais", "Chile"),
            "rol": p.get("rol", "Emprendedora"), "descripcion": "",
            "estado": p.get("estado", "Activa"), "carta_nombre": None, "carta": None
        })
    
    # 2. Actividades
    s.actividades = []
    for a in cargar_actividades_desde_db():
        fecha = datetime.fromisoformat(a["fecha"]).date() if isinstance(a["fecha"], str) else a["fecha"]
        s.actividades.append({
            "id": a["id"], "tipo": a.get("tipo", "Taller"), "nombre": a.get("nombre", ""),
            "fecha": fecha, "modalidad": a.get("modalidad", "Online"), "descripcion": a.get("descripcion", "")
        })
    
    # 3. Asistencias
    s.asistencias, s.ausencias = cargar_asistencias_desde_db()
    
    # 4. Pagos persistidos; si falla la carga, se bloquean escrituras hasta reintentar.
    try:
        s.pagos = cargar_pagos_db(cliente_supabase())
        s.membresias = crear_membresias(s.pagos)
        s.pagos_db_ok, s.pagos_db_error = True, None
    except Exception as exc:
        s.membresias, s.pagos = {}, []
        s.pagos_db_ok, s.pagos_db_error = False, str(exc)

    # 5. Becas persistidas en Supabase.
    try:
        s.becas = cargar_becas_db(cliente_supabase())
        s.becas_db_ok, s.becas_db_error = True, None
    except Exception as exc:
        s.becas = []
        s.becas_db_ok, s.becas_db_error = False, str(exc)

    # 6. Donaciones persistidas en Supabase.
    try:
        s.donaciones = cargar_donaciones_db(cliente_supabase())
        s.donaciones_db_ok, s.donaciones_db_error = True, None
    except Exception as exc:
        s.donaciones = []
        s.donaciones_db_ok, s.donaciones_db_error = False, str(exc)

    # 7. Otros estados en memoria
    s.historial_logs = []
    s.carta_n, s.beca_n, s.pagina = 0, 0, "Panel"


def participante(pid: int) -> dict:
    return next(p for p in st.session_state.participantes if p["id"] == pid)

# ─────────────────────────────────────────────────────────────────────────────


def crear_actividad(tipo: str, nombre: str, fecha: date, modalidad: str, descripcion: str = "") -> bool:
    """Crea una actividad y la guarda en Supabase."""
    s = st.session_state
    
    actividad_db = guardar_actividad_en_db(nombre or tipo, tipo, modalidad, fecha, descripcion)
    
    if actividad_db:
        s.actividades.append({
            "id": actividad_db["id"], "tipo": tipo, "nombre": nombre or tipo,
            "fecha": fecha, "modalidad": modalidad, "descripcion": descripcion
        })
        registrar_log("Nueva actividad", f"Se creó '{nombre or tipo}' ({tipo}, {modalidad.lower()}) para el {fecha_txt(fecha)}.")
        return True
    return False

def estado_pago(p: dict) -> str:
    b = beca_actual(p["id"])
    if beca_vigente(p, b, hoy()):
        return "Becado (exento)"
    m = st.session_state.membresias.get(p["id"])
    if not m:
        return "Pendiente"
    dias = (m["vencimiento"] - hoy()).days
    return "Vencido" if dias < 0 else "Por vencer" if dias <= DIAS_ALERTA else "Pagado"


def filas_pagos() -> list[dict]:
    filas = []
    for p in st.session_state.participantes:
        est = estado_pago(p)
        m = st.session_state.membresias.get(p["id"], {})
        b = beca_actual(p["id"])
        inicio, vence = fechas_pago(p, b, m, hoy())
        filas.append(dict(p=p, estado=est, inicio=inicio, vence=vence))
    return filas


def ultimo_comprobante(pid: int) -> dict | None:
    cs = [x for x in st.session_state.pagos if x["participante_id"] == pid and x["comprobante_url"]]
    return max(cs, key=lambda x: (x["fecha"], str(x.get("creado_en") or ""), str(x["id"]))) if cs else None


def registrar_pago(pid: int, monto: int, metodo: str, fecha: date, meses: int, archivo=None) -> None:
    s = st.session_state
    pago = guardar_pago_db(
        cliente_supabase(), SUPABASE_PAYMENTS_BUCKET, pid, monto, metodo, fecha, meses, archivo, hoy()
    )
    s.pagos.append(pago)
    s.membresias[pid] = dict(inicio=pago["inicio"], vencimiento=pago["vencimiento"])
    participante(pid)["estado"] = "Activa"
    registrar_log("Registro de pago", f"Se registró pago de {plata(monto)} para {participante(pid)['nombre']}.",
                  archivo.name if archivo else None)


def registrar_donacion(donante: str, monto: int, fecha: date, archivo) -> None:
    s = st.session_state
    donacion = guardar_donacion_db(
        cliente_supabase(), SUPABASE_PAYMENTS_BUCKET, donante, monto, fecha, archivo
    )
    s.donaciones.append(donacion)
    registrar_log("Registro de donación", f"Se registró donación de {plata(monto)} de '{donante}'.",
                  archivo.name if archivo else None, archivo.getvalue() if archivo else None)


def email_valido(c: str) -> bool:
    return re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", c) is not None

#NUEVO, PARA EL SUPABASE
def guardar_participante_en_db(
    nombre: str, correo: str, telefono: str, pais: str, rol: str, estado: str
) -> dict | None:
    """Guarda un nuevo participante en la tabla de Supabase."""
    try:
        response = cliente_supabase().table("Participantes").insert({
            "nombre": nombre,
            "correo": correo,
            "telefono": telefono,
            "pais": pais,
            "rol": rol,
            "estado": estado
        }).execute()
        if not response.data:
            raise RuntimeError("Supabase no confirmó el registro de la participante.")
        return response.data[0]
    except Exception as e:
        st.error(f"Error al guardar en base de datos: {e}")
        return None
#HASTA AQUI

#NUEVO PARA EL SUPABASE
def guardar_participante() -> None:
    s = st.session_state
    nombre, correo = s.f_nombre.strip(), s.f_correo.strip().lower()
    carta = s.get(f"f_carta_{s.carta_n}")
    es_becada = s.f_rol == "Becada"
    motivo_beca = s.get("f_beca_motivo", "").strip()
    inicio_beca = s.get("f_beca_inicio", hoy())
    termino_beca = s.get("f_beca_termino", sumar_meses(hoy(), 6))
    
    # Validaciones
    if not nombre or not correo or not s.f_rol or not s.f_pais:
        s.f_msg = ("error", "Completa nombre, correo, país y rol para guardar.")
    elif not email_valido(correo):
        s.f_msg = ("error", "El correo no tiene un formato válido.")
    elif any(p["correo"].lower() == correo for p in s.participantes):
        s.f_msg = ("error", "Ese correo ya está registrado: no se permiten duplicados.")
    elif s.f_rol == "Mentora" and carta is None:
        s.f_msg = ("error", "La carta de compromiso es obligatoria para registrar a una mentora.")
    elif es_becada and not s.get("becas_db_ok", False):
        s.f_msg = ("error", "No se puede registrar una becada porque la tabla de becas no está disponible. Ejecuta la migración indicada en el README y vuelve a iniciar sesión.")
    elif es_becada and not motivo_beca:
        s.f_msg = ("error", "Indica el motivo de asignación de la beca.")
    elif es_becada and termino_beca <= inicio_beca:
        s.f_msg = ("error", "El término de la beca debe ser posterior al inicio.")
    else:
        estado = SIGUIENTE_PASO[s.f_rol][0]
        
        # 1. Intentar guardar en Supabase primero
        participante_db = guardar_participante_en_db(
            nombre, correo, s.f_tel.strip(), s.f_pais, s.f_rol, estado
        )
        if participante_db:
            
            # 2. Si fue exitoso, actualizar también la sesión local para que se vea al instante
            nuevo_id = participante_db["id"]
            s.participantes.append(dict(
                id=nuevo_id, nombre=nombre, correo=correo, telefono=s.f_tel.strip(),
                pais=s.f_pais, rol=s.f_rol, descripcion=s.f_desc.strip(), estado=estado,
                carta_nombre=carta.name if carta else None, carta=carta.getvalue() if carta else None))
            
            if es_becada:
                try:
                    asignar_beca(nuevo_id, motivo_beca, inicio_beca, termino_beca)
                except Exception as exc:
                    s.f_msg = (
                        "error",
                        f"{nombre} quedó registrada, pero no se pudo guardar su beca en Supabase: {exc}. "
                        "No vuelvas a registrar a la participante; asigna la beca desde Gestión de becas.",
                    )
                else:
                    s.f_msg = (
                        "ok",
                        f"{nombre} quedó registrada como becada con vigencia "
                        f"{fecha_corta(inicio_beca)} – {fecha_corta(termino_beca)}.",
                    )
            else:
                s.f_msg = ("ok", f"{nombre} quedó registrada como {s.f_rol.lower()} · siguiente paso: {estado.lower()}.")
            registrar_log("Registro de participante", f"Se agregó a {nombre} ({s.f_pais}) como {s.f_rol}.",
                          carta.name if carta else None, carta.getvalue() if carta else None)
            
            # Limpiar el formulario
            s.f_nombre = s.f_correo = s.f_tel = s.f_desc = ""
            s.f_rol = None
            s.f_beca_motivo = ""
            s.f_beca_inicio = hoy()
            s.f_beca_termino = sumar_meses(hoy(), 6)
            s.carta_n += 1
        else:
            s.f_msg = ("error", "No se pudo guardar en la base de datos. Intenta de nuevo.")
#Hasta aqui


def beca_actual(pid: int) -> dict | None:
    recs = [b for b in st.session_state.becas if b["participante_id"] == pid]
    return max(recs, key=lambda b: b["id"]) if recs else None


def estado_beca(b: dict) -> str:
    return "Activa" if beca_vigente({}, b, hoy()) else "Inactiva"


def detalle_inactiva(b: dict) -> str:
    return "Revocada" if b["estado"] == "Revocada" else "Vigencia terminada"


def asignar_beca(pid: int, motivo: str, inicio: date, termino: date) -> None:
    s = st.session_state
    beca = guardar_beca_db(cliente_supabase(), pid, motivo, inicio, termino, hoy())
    s.becas.append(beca)
    participante(pid)["estado"] = "Activa"
    registrar_log("Asignación de beca", f"Se otorgó beca a {participante(pid)['nombre']} por '{motivo}'.")


def revocar_beca(pid: int, motivo: str) -> None:
    s = st.session_state
    b = beca_actual(pid)
    if b is None:
        raise RuntimeError("No existe una asignación formal de beca para revocar.")
    revocada = revocar_beca_db(cliente_supabase(), b["id"], motivo, hoy())
    s.becas = [revocada if registro["id"] == b["id"] else registro for registro in s.becas]
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
        # Presente → Ausente
        s.asistencias.discard(k)
        s.ausencias.add(k)
        guardar_asistencia_en_db(aid, pid, False)
    elif k in s.ausencias:
        # Ausente → Sin marcar (Blanco)
        s.ausencias.discard(k)
        borrar_asistencia_db(aid, pid)  # <-- CORRECCIÓN: Borramos de la DB en lugar de enviar None
    else:
        # Sin marcar → Presente
        s.asistencias.add(k)
        guardar_asistencia_en_db(aid, pid, True)
        

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
                        for p in st.session_state.participantes
                        if estado_participante(p["estado"], estado_pago(p)) == "Activa") if v is not None]
    return round(sum(vals) / len(vals)) if vals else 0


def csv_asistencia(acts: list[dict]) -> bytes:
    filas = []
    for a in sorted(acts, key=lambda x: x["fecha"]):
        for p in st.session_state.participantes:
            m = marca(a["id"], p["id"])
            if m != "sin marcar" or estado_participante(p["estado"], estado_pago(p)) == "Activa":
                filas.append([fecha_txt(a["fecha"]), a["tipo"], a["nombre"], a["modalidad"], p["nombre"], p["rol"],
                              {"presente": "Presente", "ausente": "Ausente", "sin marcar": "Sin marcar"}[m]])
    return a_csv(["Fecha", "Tipo", "Actividad", "Modalidad", "Participante", "Rol", "Asistencia"], filas)


# ───────────────────────────────── DIÁLOGOS ──────────────────────────────────
@st.dialog("Registrar pago", width="large")
def dialogo_pago() -> None:
    elegibles = [p for p in st.session_state.participantes if estado_pago(p) != "Becado (exento)"]
    if not elegibles:
        st.info("No hay participantes disponibles para registrar un pago.")
        return
    opciones = {f"{p['nombre']} · {p['rol']}": p["id"] for p in elegibles}
    sel = st.selectbox("Participante", list(opciones))
    c1, c2 = st.columns(2)
    monto = c1.number_input("Monto ($)", min_value=1, step=1000, value=PRECIO_DEMO, format="%d")
    metodo = c2.selectbox("Método de pago", ["Transferencia", "PayPal", "Voucher"])
    c3, c4 = st.columns(2)
    fecha = c3.date_input("Fecha de pago", value=hoy(), format="DD/MM/YYYY")
    meses = c4.selectbox("Duración de la membresía (meses)", [1, 3, 6, 12], index=2)
    obligatorio = metodo == "Transferencia"
    archivo = st.file_uploader(
        "Comprobante de pago" if obligatorio else "Comprobante de pago (opcional)",
        type=["png", "jpg", "jpeg", "pdf"],
        help="Para transferencias bancarias es obligatorio adjuntar el comprobante.",
    )
    if st.button("Guardar pago", key="btn_guardar_pago"):
        if obligatorio and archivo is None:
            st.error("Adjunta el comprobante de la transferencia para continuar.")
        else:
            try:
                registrar_pago(opciones[sel], int(monto), metodo, fecha, int(meses), archivo)
            except Exception as exc:
                st.error(f"No se pudo registrar el pago en Supabase: {exc}")
            else:
                st.session_state.pagos_db_ok = True
                st.session_state.pagos_db_error = None
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
            try:
                registrar_donacion(donante.strip(), int(monto), fecha, archivo)
            except Exception as exc:
                st.error(f"No se pudo guardar la donación en Supabase: {exc}")
            else:
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
    try:
        contenido = descargar_comprobante(cliente_supabase(), SUPABASE_PAYMENTS_BUCKET, c["comprobante_url"])
    except Exception as exc:
        st.error(f"No se pudo descargar el comprobante desde Storage: {exc}")
        return
    mostrar_archivo(c["comprobante_nombre"], contenido, "Descargar comprobante")


@st.dialog("Historial financiero", width="large")
def dialogo_historial_fin() -> None:
    tabs = st.tabs(["Membresías", "Donaciones"])
    with tabs[0]:
        hist = sorted(
            st.session_state.pagos,
            key=lambda x: (x["fecha"], str(x.get("creado_en") or ""), str(x["id"])),
            reverse=True,
        )
        html(tabla_html(["Fecha", "Participante", "Monto", "Método", "Comprobante"],
                        [[fecha_txt(x["fecha"]), escape(participante(x["participante_id"])["nombre"]), plata(x["monto"]),
                          escape(x["metodo"]), "Sí" if x["comprobante_url"] else "—"] for x in hist]))
    with tabs[1]:
        dones = sorted(st.session_state.donaciones, key=lambda x: x["fecha"], reverse=True)
        html(tabla_html(["Fecha", "Donante", "Monto", "Comprobante"],
                        [[fecha_txt(x["fecha"]), escape(x["donante"]), plata(x["monto"]),
                          "Sí" if x["comprobante_url"] else "—"]
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
    """Diálogo para crear nueva actividad con persistencia en Supabase."""
    c1, c2 = st.columns(2)
    tipo = c1.selectbox("Tipo de actividad", TIPOS_ACTIVIDAD)
    modalidad = c2.selectbox("Modalidad", MODALIDADES)
    nombre = st.text_input("Nombre de la actividad (opcional)", 
                          placeholder="Ej. Marca personal")
    fecha = st.date_input("Fecha", value=hoy(), format="DD/MM/YYYY")
    descripcion = st.text_area("Descripción (opcional)", 
                              placeholder="Detalles adicionales...",
                              height=80)
    
    if st.button("Crear actividad", key="btn_crear_actividad"):
        if crear_actividad(tipo, nombre.strip(), fecha, modalidad, descripcion.strip()):
            st.session_state.flash = f"Actividad creada para el {fecha_txt(fecha)}."
            st.rerun()
        else:
            st.error("No se pudo crear la actividad. Intenta de nuevo.")


@st.dialog("Revocar beca")
def dialogo_revocar(pid: int) -> None:
    st.caption(participante(pid)["nombre"])
    motivo = st.text_input("Motivo de la revocación", placeholder="Ej. No cumple la asistencia mínima")
    if st.button("Revocar beca", key=f"btn_revocar_{pid}"):
        if not motivo.strip():
            st.error("Indica el motivo para dejar registro.")
        else:
            try:
                revocar_beca(pid, motivo.strip())
            except Exception as exc:
                st.error(f"No se pudo revocar la beca en Supabase: {exc}")
            else:
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
            try:
                asignar_beca(pid, "Renovación de beca", inicio, termino)
            except Exception as exc:
                st.error(f"No se pudo renovar la beca en Supabase: {exc}")
            else:
                st.session_state.flash = f"Beca renovada a {participante(pid)['nombre']}."
                st.rerun()


# ─────────────────────────────────── PÁGINAS ─────────────────────────────────
def pagina_panel() -> None:
    h = hoy()
    s = st.session_state
    P, filas = s.participantes, filas_pagos()
    activas = sum(estado_participante(p["estado"], estado_pago(p)) == "Activa" for p in P)
    alerta = [f for f in filas if f["vence"] and f["estado"] != "Becado (exento)" and 0 <= (f["vence"] - h).days <= DIAS_ALERTA]
    vencidas = [f for f in filas if f["estado"] == "Vencido"]
    ultimas = [(p, beca_actual(p["id"])) for p in P]
    becas_act = sum(beca_vigente(p, b, h) for p, b in ultimas)
    becas_rev = sum(bool(b and b["estado"] == "Revocada") for _, b in ultimas)
    k = (h.year, h.month)
    ing_mes, don_mes = total_mes(s.pagos, k), total_mes(s.donaciones, k)

    hero("Panel general", f"¡Hola, {NOMBRE_USUARIA}!", "Resumen de participantes, membresías e ingresos de la fundación.",
         [("Participantes activas", activas), ("Por vencer", len(alerta)), ("Vencidas", len(vencidas))])
    if not s.donaciones_db_ok:
        st.warning(f"No se pudieron cargar las donaciones de Supabase: {s.donaciones_db_error}")
        if st.button("Reintentar carga de donaciones", key="btn_reintentar_donaciones"):
            try:
                s.donaciones = cargar_donaciones_db(cliente_supabase())
            except Exception as exc:
                s.donaciones_db_error = str(exc)
                st.error(f"La conexión de donaciones sigue fallando: {exc}")
            else:
                s.donaciones_db_ok, s.donaciones_db_error = True, None
                st.rerun()

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
        html(f'<div class="sub">Membresías por vencer</div><div class="muted">Próximos {DIAS_ALERTA} días y ya vencidas</div>')
        prox = sorted([f for f in filas if f["vence"] and f["estado"] != "Becado (exento)" and (f["vence"] - h).days <= DIAS_ALERTA],
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
        if s.get("f_rol") == "Becada":
            st.markdown("**Asignación de beca**")
            st.text_input("Motivo de la beca", placeholder="Describe el motivo", key="f_beca_motivo")
            c1, c2 = st.columns(2)
            c1.date_input("Inicio de vigencia", value=hoy(), format="DD/MM/YYYY", key="f_beca_inicio")
            c2.date_input(
                "Término de vigencia", value=sumar_meses(hoy(), 6),
                format="DD/MM/YYYY", key="f_beca_termino",
            )
            if not s.get("becas_db_ok", False):
                st.warning("Primero ejecuta la migración de Becas en Supabase; la aplicación no guardará una becada sin registrar su vigencia.")
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
            td(cols[3], chip(p["rol"]))
            td(cols[4], escape(estado_participante(p["estado"], estado_pago(p))))
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
    filas = filas_pagos() if s.pagos_db_ok else []
    k = (h.year, h.month)
    hero("Finanzas", "Membresías, pagos y donaciones", "Control de vigencias, comprobantes y aportes recibidos.",
         [("Ingresos del mes", plata(total_mes(s.pagos, k))), ("Donaciones del mes", plata(total_mes(s.donaciones, k)))])

    if not s.pagos_db_ok:
        st.error(f"No se pudo cargar el historial de pagos desde Supabase: {s.pagos_db_error}")
        if st.button("Reintentar conexión de pagos", key="btn_reintentar_pagos"):
            try:
                s.pagos = cargar_pagos_db(cliente_supabase())
                s.membresias = crear_membresias(s.pagos)
            except Exception as exc:
                s.pagos_db_error = str(exc)
                st.error(f"La conexión sigue fallando: {exc}")
            else:
                s.pagos_db_ok, s.pagos_db_error = True, None
                st.rerun()

    b1, b2, b3, _ = st.columns([1, 1, 1.1, 2])
    if b1.button("+ Registrar pago", key="btn_nuevo_pago", width="stretch", disabled=not s.pagos_db_ok):
        dialogo_pago()
    if b2.button(
        "+ Registrar donación", key="btn_nueva_donacion", width="stretch",
        disabled=not s.donaciones_db_ok,
    ):
        dialogo_donacion()
    if b3.button("Historial financiero", key="btn_hist_fin", width="stretch", disabled=not s.pagos_db_ok):
        dialogo_historial_fin()

    cuenta = {e: sum(f["estado"] == e for f in filas) for e in ESTADOS}
    for col, m in zip(st.columns(5), [("clock", "Pendientes", str(cuenta["Pendiente"]), "sin pagos registrados"),
                                      ("check", "Al día", str(cuenta["Pagado"]), "membresías vigentes"),
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
            td(cols[1], chip(p["rol"]))
            td(cols[2], fecha_txt(f["inicio"]))
            td(cols[3], fecha_txt(f["vence"]))
            td(cols[4], chip(f["estado"]))
            if ultimo_comprobante(p["id"]):
                if cols[5].button("Ver archivo", key=f"mini_ver_{p['id']}"):
                    dialogo_ver(p["id"])
            else:
                td(cols[5], "—")
            sep()
        if not filas:
            st.caption("Aún no hay pagos registrados para mostrar.")


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
                           f'<div class="muted" style="font-weight:400">{chip(p["rol"])} · {escape(p.get("pais", "Chile"))}</div></div>')
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
    if not st.session_state.get("becas_db_ok", False):
        st.warning("No se pueden registrar becas hasta que la tabla Becas esté disponible en Supabase.")
        return
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
            try:
                asignar_beca(pid, motivo.strip(), inicio, termino)
            except Exception as exc:
                st.error(f"No se pudo guardar la beca en Supabase: {exc}")
            else:
                st.session_state.beca_n += 1
                st.session_state.flash = f"Beca asignada a {participante(pid)['nombre']}."
                st.rerun()


def pagina_becas() -> None:
    s = st.session_state
    registros = becas_para_listado(s.participantes, s.becas)
    registros.sort(key=lambda x: (not beca_vigente(x[0], x[1], hoy()), x[0]["id"]))
    activas = sum(beca_vigente(p, b, hoy()) for p, b in registros)
    hero("Becas", "Gestión de becas", "Asignación, vigencia y seguimiento de asistencia de las becadas.",
         [("Becas activas", activas), ("Inactivas", len(registros) - activas)])
    if not s.becas_db_ok:
        st.error(f"No se pudieron cargar las asignaciones de beca desde Supabase: {s.becas_db_error}")
        st.caption("Ejecuta la migración `supabase/migrations/20261113000000_create_becas.sql` en el SQL Editor de Supabase.")
        if st.button("Reintentar conexión de becas", key="btn_reintentar_becas"):
            try:
                s.becas = cargar_becas_db(cliente_supabase())
            except Exception as exc:
                s.becas_db_error = str(exc)
                st.error(f"La conexión sigue fallando: {exc}")
            else:
                s.becas_db_ok, s.becas_db_error = True, None
                st.rerun()

    izq, der = st.columns([2.15, 1])
    with izq, st.container(key="card_becas_tabla"):
        html('<div class="sub">Becadas</div>')
        anchos = [1.9, 1.1, 2.1, 1.3, 1.1, 1.1]
        cabecera(anchos, ["Nombre", "Asignación", "Vigencia (inicio – fin)", "% asistencia", "Estado", "Acción"])
        if not registros:
            st.caption("Todavía no hay becas registradas.")
        for p, b in registros:
            if b is None:
                est = "Becado (exento)"
                asignacion = "Por rol"
                vigencia = "Sin período formal"
            else:
                est = estado_beca(b)
                asignacion = fecha_corta(b["asignacion"])
                vigencia = f'{fecha_corta(b["inicio"])} – {fecha_corta(b["termino"])}'
            actividades_beca = actividades_de_beca(s.actividades, b, hoy())
            pct = pct_asistencia(p["id"], actividades_beca)
            cols = st.columns(anchos, vertical_alignment="center")
            td(cols[0], escape(p["nombre"]))
            td(cols[1], asignacion, "nw")
            td(cols[2], vigencia, "nw")
            celda(cols[3], f'<div class="td">{barra(pct)}</div>')
            td(cols[4], chip(est))
            if b is None:
                td(cols[5], "Sin registro formal")
            elif est == "Activa":
                if cols[5].button("Revocar", key=f"mini_rev_{p['id']}"):
                    dialogo_revocar(p["id"])
            elif cols[5].button("Renovar", key=f"mini_ren_{p['id']}", help=detalle_inactiva(b)):
                dialogo_renovar(p["id"])
            sep()
        if any(b is None for _, b in registros):
            st.info("Sin asignación formal se muestra la asistencia histórica sobre todas las actividades; con período formal, se calcula solo dentro de la vigencia.")
        st.caption("«Inactiva»: beca revocada o con la vigencia terminada. «Sin datos» indica que no hay asistencias marcadas para ese período.")
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
            td(cols[1], chip(p["rol"]))
            td(cols[2], escape(estado_participante(p["estado"], estado_pago(p))))
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
    activas = [p for p in P if estado_participante(p["estado"], estado_pago(p)) == "Activa"]
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
def pagina_acceso() -> None:
    hero("Acceso seguro", "Bienvenida", "Inicia sesión con la cuenta autorizada de tu equipo.")
    aviso = st.session_state.pop("auth_notice", None)
    if aviso:
        st.warning(aviso)

    if not supabase_url or not supabase_key:
        st.error("Faltan SUPABASE_URL o SUPABASE_KEY en el archivo .env.")
        return

    with st.container(key="card_login"):
        html('<div class="sub">Iniciar sesión</div>'
             '<div class="muted">Las cuentas deben estar creadas y confirmadas en Supabase Auth.</div>')
        with st.form("form_acceso"):
            correo = st.text_input("Correo electrónico", key="login_correo", autocomplete="email")
            contrasena = st.text_input("Contraseña", type="password", key="login_contrasena",
                                       autocomplete="current-password")
            ingresar = st.form_submit_button("Ingresar", width="stretch")

    if not ingresar:
        return

    try:
        cliente = iniciar_sesion_supabase(supabase_url, supabase_key, correo, contrasena)
    except ValueError as exc:
        st.error(str(exc))
    except AuthApiError:
        st.error("No se pudo iniciar sesión. Revisa las credenciales y confirma que la cuenta esté habilitada.")
    except (HTTPError, SupabaseException) as exc:
        detalle = str(exc)
        for secreto in (supabase_url, supabase_key):
            if secreto:
                detalle = detalle.replace(secreto, "[oculto]")
        st.error(f"No se pudo conectar con Supabase Auth ({type(exc).__name__}): {detalle}")
    except RuntimeError as exc:
        st.error(f"No se pudo iniciar la sesión: {exc}")
    else:
        st.session_state["_cliente_supabase"] = cliente
        st.session_state["usuario_email"] = correo.strip()
        st.session_state.pop("login_contrasena", None)
        st.rerun()


def cerrar_sesion() -> None:
    cliente = st.session_state.get("_cliente_supabase")
    aviso = None
    if isinstance(cliente, Client):
        try:
            cliente.auth.sign_out()
        except (AuthApiError, HTTPError, SupabaseException) as exc:
            aviso = f"La sesión local se cerró, pero Supabase no confirmó el cierre ({type(exc).__name__})."

    st.session_state.clear()
    if aviso:
        st.session_state["auth_notice"] = aviso


if not isinstance(st.session_state.get("_cliente_supabase"), Client):
    pagina_acceso()
    st.stop()

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
    usuario = st.session_state.get("usuario_email", NOMBRE_USUARIA)
    iniciales = "".join(w[0] for w in usuario.strip("[]").split()[:2]).upper() or "CC"
    html(f'<div class="user-card"><div class="av">{escape(iniciales)}</div><div><b>{escape(usuario)}</b><span>Sesión autorizada</span></div></div>')
    st.button("Cerrar sesión", key="btn_logout", width="stretch", on_click=cerrar_sesion)

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
