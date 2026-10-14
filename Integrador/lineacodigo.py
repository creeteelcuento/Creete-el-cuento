"""
Créete el Cuento · Sistema de gestión interno (prototipo funcional)

Páginas incluidas: Panel · Participantes (registro) · Pagos · Asistencia · Becas · Seguimiento · Reportes · Historial.
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
from datetime import date, timedelta
from html import escape
from pathlib import Path

import streamlit as st

# ─────────────────────────────── CONFIGURACIÓN ───────────────────────────────
st.set_page_config(page_title="Créete el Cuento · Gestión", page_icon="💡", layout="wide")

ASSETS = Path(__file__).parent / "assets"
NOMBRE_USUARIA = "[Nombre]"      # cámbialo por el nombre de la coordinadora
DIAS_ALERTA = 15                 # alerta de vencimiento: faltan 15 días o menos
PRECIO_DEMO = 25000              # monto ficticio solo para datos de ejemplo

ROLES = ["Mentora", "Emprendedora", "Becada", "Red de psicólogos", "Red de coaches"]
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
MESES_LARGO = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre",
               "Octubre", "Noviembre", "Diciembre"]
NAV = [
    ("Panel", "dashboard"), ("Participantes", "group"), ("Pagos", "credit_card"),
    ("Asistencia", "check"), ("Becas", "workspace_premium"), ("Seguimiento", "bar_chart"),
    ("Reportes", "description"), ("Historial", "schedule"),
]
COLOR_FONDO = "#EDEDEA"
COLOR_MENU = "#F5EED7"
COLOR_BORDE = "#3A3A3A"
COLOR_TEXTO = "#1F1F1F"
COLOR_ORO = "#D7AE00"
COLOR_BOTON = "#E6C23A"

# ─────────────────────────────────── ESTILOS ─────────────────────────────────
CSS = """
@font-face {font-family:'Nunito Sans'; font-weight:400; src:url(app/static/fonts/nunito-sans-latin-400-normal.woff2) format('woff2');}
@font-face {font-family:'Nunito Sans'; font-weight:600; src:url(app/static/fonts/nunito-sans-latin-600-normal.woff2) format('woff2');}
@font-face {font-family:'Nunito Sans'; font-weight:700; src:url(app/static/fonts/nunito-sans-latin-700-normal.woff2) format('woff2');}
@font-face {font-family:'Nunito Sans'; font-weight:800; src:url(app/static/fonts/nunito-sans-latin-800-normal.woff2) format('woff2');}
@font-face {font-family:'Fraunces'; font-weight:600; src:url(app/static/fonts/fraunces-latin-600-normal.woff2) format('woff2');}
.stApp, .stApp :where(p, span, div, label, button, input, textarea, li, td, th, a, small):not([data-testid="stIconMaterial"]) {font-family:'Nunito Sans', sans-serif;}
.stApp {background:@FONDO; color:@TEXTO;}
[data-testid="stDialog"], [data-testid="stDialog"] :where(p, span, div, label, button, input, h1, h2, h3):not([data-testid="stIconMaterial"]) {font-family:'Nunito Sans', sans-serif;}
[data-testid="stDialog"] [role="dialog"] {background:#FFFDF5; border:1.5px solid @BORDE; border-radius:16px; box-shadow:4px 4px 0 #F1DD8E;}
[data-testid="stDialog"] h2 {font-family:'Fraunces', serif !important; font-weight:600; color:#2B2B2B;}
[data-testid="stFileUploaderDropzone"] {background:#FFFEFA; border:2px dashed @ORO; border-radius:14px;}
[data-testid="stFileUploaderDropzone"] button {background:@BOTON; border:1.5px solid @BORDE; color:@TEXTO; border-radius:12px; box-shadow:2px 2px 0 @BORDE;}
.stApp p, .stApp label {color:@TEXTO;}
#MainMenu, footer, .stAppDeployButton {display:none !important;}
header[data-testid="stHeader"] {background:transparent; height:0; pointer-events:none;}
[data-testid="stToolbar"], [data-testid="stDecoration"] {display:none !important;}
.block-container {padding:1.5rem 2rem 3rem 2rem; max-width:100%;}
[data-testid="stHorizontalBlock"] {gap:14px;}
[data-testid="stVerticalBlock"] {gap:.7rem;}

section[data-testid="stSidebar"] {background:@MENU; border-right:2px solid @BORDE; width:220px !important; min-width:220px !important;}
section[data-testid="stSidebar"] > div:first-child {width:220px !important; background:@MENU;}
[data-testid="stSidebarHeader"], [data-testid="stSidebarCollapseButton"], [data-testid="stSidebarResizeHandle"] {display:none !important;}
[data-testid="stSidebarContent"] {padding:0 !important; border-right:2px solid @BORDE; box-sizing:border-box;}
[data-testid="stSidebarUserContent"] {padding:1rem 6px 2rem 6px;}
section[data-testid="stSidebar"] [data-testid="stVerticalBlock"] {gap:5px;}
.logo {display:block; height:84px; margin:10px 0 18px 4px;}
section[data-testid="stSidebar"] [class*="st-key-nav_"] button, section[data-testid="stSidebar"] [class*="st-key-navon_"] button {width:100%; min-height:44px; justify-content:flex-start; background:transparent; border:1.5px solid transparent; border-radius:12px; box-shadow:none; color:@TEXTO; padding:0 12px;}
section[data-testid="stSidebar"] [class*="st-key-nav_"] button > div, section[data-testid="stSidebar"] [class*="st-key-navon_"] button > div {justify-content:flex-start; gap:10px;}
section[data-testid="stSidebar"] [class*="st-key-nav_"] button p, section[data-testid="stSidebar"] [class*="st-key-navon_"] button p {font-weight:600; font-size:14px; color:@TEXTO;}
section[data-testid="stSidebar"] [class*="st-key-nav_"] button:hover {background:#FFF9E3; border-color:#E6D68E;}
section[data-testid="stSidebar"] [class*="st-key-navon_"] button, section[data-testid="stSidebar"] [class*="st-key-navon_"] button:hover {background:#FFFFFF; border-color:@BORDE; box-shadow:2px 2px 0 @ORO;}
[data-testid="stIconMaterial"] {color:@ORO !important;}

.ttl {font-family:'Fraunces', serif !important; font-size:28px; font-weight:600; color:#2B2B2B; margin:0 0 18px 0; line-height:1.2;}
.head .ttl {margin-bottom:0;}
.ttl:after {content:""; display:block; width:56px; height:4px; background:@ORO; border-radius:3px; margin-top:6px;}
.head {display:flex; justify-content:space-between; align-items:center; margin-bottom:4px;}
.hello {display:flex; align-items:center; gap:14px; text-align:right; font-size:14px;}
.hello span {display:block; font-size:12px; color:#6B6B6B;}
.hello img {width:130px; height:62px; object-fit:cover !important; border:1.5px solid @BORDE; border-radius:14px; box-shadow:3px 3px 0 #F1DD8E;}

[class*="st-key-card_"] {background:#fff; border:1.5px solid @BORDE; border-radius:16px; padding:18px; box-shadow:3px 3px 0 #F1DD8E; gap:.6rem;}
[class*="st-key-card_m_"] {min-height:120px;}
.st-key-card_ingresos, .st-key-card_por_vencer {min-height:calc(100vh - 275px);}
.st-key-card_form, .st-key-card_clasif {min-height:calc(100vh - 118px);}
.st-key-card_asis_tabla, .st-key-card_qr {min-height:calc(100vh - 240px);}
.st-key-card_becas_tabla, .st-key-card_becas_form {min-height:calc(100vh - 150px);}
.st-key-card_alerta, .st-key-card_hist {min-height:112px;}
.m-l {font-size:13px; color:#6B6B6B; min-height:36px; line-height:1.3;}
.m-v {font-size:30px; font-weight:800; line-height:1.1; white-space:nowrap;}
.m-v.long {font-size:23px; padding-top:5px;}
.sub {font-weight:700; font-size:14px; margin-bottom:4px;}
.muted {color:#6B6B6B; font-size:13px;}

.stButton > button, .stFormSubmitButton > button {border:1.5px solid @BORDE; background:@BOTON; color:@TEXTO; border-radius:12px; min-height:44px; box-shadow:2px 2px 0 @BORDE; padding:0 20px;}
.stButton > button:hover {background:#EDD05E; border-color:@BORDE; color:@TEXTO;}
.stButton > button p {font-weight:700; font-size:14px; color:@TEXTO;}
.stDownloadButton > button {border:1.5px solid @BORDE; background:#fff; color:@TEXTO; border-radius:12px; min-height:44px; box-shadow:2px 2px 0 @ORO; padding:0 20px;}
.stDownloadButton > button:hover {background:#FFF9E3; border-color:@BORDE; color:@TEXTO;}
.stDownloadButton > button p {font-weight:700; font-size:14px; color:@TEXTO;}
[class*="st-key-ver_"] button {background:transparent !important; border:0 !important; box-shadow:none !important; min-height:0; padding:0 !important; justify-content:flex-start;}
[class*="st-key-ver_"] button p {font-weight:400 !important; text-decoration:none;}
[class*="st-key-ver_"] button:hover p {text-decoration:underline;}
[class*="st-key-ver_"] {padding-top:3px;}
.st-key-btn_recordatorio {margin-top:14px;}

[data-testid="stWidgetLabel"] p {font-weight:700; font-size:13px;}
[data-testid="stTextInputRootElement"], [data-testid="stTextAreaRootElement"], [data-testid="stSelectbox"] [data-baseweb="select"] > div, [data-testid="stMultiSelect"] [data-baseweb="select"] > div, [data-testid="stDateInputField"], [data-testid="stNumberInputContainer"] {border-radius:12px !important; border:1.5px solid #EBDDB0 !important; background:#FFFEFA !important;}
[data-testid="stTextInputRootElement"] {min-height:44px;}
[data-testid="stSelectbox"] div:has(> input), [data-testid="stDateInput"] div:has(> input), [data-testid="stMultiSelect"] div:has(> input) {border-radius:12px !important; border:1.5px solid #EBDDB0 !important; background:#FFFEFA !important;}
[data-baseweb="tag"] {background:#FBF0C8 !important; color:@TEXTO !important; border:1px solid #706F6F; border-radius:99px !important;}
.info {background:#FBF0C8; color:@TEXTO; border-radius:10px; padding:10px 14px; font-size:13px; margin-bottom:10px;}

.chip {display:inline-block; padding:3px 10px; border-radius:99px; font-size:12px; font-weight:700; border:1px solid #706F6F; color:@TEXTO; background:#FBF0C8; white-space:nowrap;}
.c-pagado, .c-activa {background:#D9EBC8;} .c-vencer {background:#FBE3B0;} .c-vencido {background:#F6C9B8;} .c-exento {background:#E8DDF0;} .c-inact {background:#E4E4DF;}
.clasif {background:#FFFCEF; border:1.5px solid transparent; border-radius:12px; padding:10px 14px; margin-bottom:8px; font-size:14px;}
.clasif .chip {margin-bottom:5px;}
.clasif.sel {border-color:@BORDE; box-shadow:2px 2px 0 @ORO; background:#fff;}
.foto {width:100%; height:110px; object-fit:cover !important; border:1.5px solid @BORDE; border-radius:14px; box-shadow:3px 3px 0 #F1DD8E; margin-top:4px;}

.bars {display:flex; align-items:flex-end; gap:18px; height:calc(100vh - 430px); min-height:180px; padding:0 8px; border-bottom:2px solid #F5ECD3; margin-top:14px;}
.bars div {flex:1; border-radius:8px 8px 0 0;}
.lbls {display:flex; justify-content:space-around; font-size:12px; color:#6B6B6B; margin-top:8px;}
.pctrow {display:flex; align-items:center; gap:10px; padding:9px 0;}
.pctrow b {font-size:13px; min-width:40px; text-align:right;}
.bar {flex:1; height:10px; background:#F8F1DE; border-radius:9px; overflow:hidden;}
.bar i {display:block; height:10px; background:#E0BC3E; border-radius:9px;}
.qrbox svg {width:190px; height:190px; margin:10px auto; display:block;}
.qrbox {text-align:center;}

.th {font-size:12px; font-weight:700; color:#6B6B6B; padding-bottom:6px;}
.hline {border-bottom:2px solid #F1E6C6; margin:0 0 2px 0;}
.td {font-size:14px; padding:8px 0;}
.nw {white-space:nowrap;}
.th {white-space:nowrap;}
.tbl {width:100%; border-collapse:collapse;}
.tbl th {text-align:left; padding:10px; font-size:12px; color:#6B6B6B; border-bottom:2px solid @BORDE;}
.tbl td {padding:10px; border-bottom:1px solid #EFE6C8; font-size:14px;}
.fila {border-bottom:1px solid #F5EEDB; margin:0;}
"""
CSS = (CSS.replace("@FONDO", COLOR_FONDO).replace("@MENU", COLOR_MENU).replace("@BORDE", COLOR_BORDE)
       .replace("@TEXTO", COLOR_TEXTO).replace("@ORO", COLOR_ORO).replace("@BOTON", COLOR_BOTON))
st.markdown("<style>" + re.sub(r"\s*\n\s*", " ", CSS) + "</style>", unsafe_allow_html=True)


# ─────────────────────────────────── UTILIDADES ──────────────────────────────
def b64(nombre: str) -> str:
    ruta = ASSETS / nombre
    if not ruta.exists():
        return ""
    mime = "image/png" if nombre.endswith("png") else "image/jpeg"
    return f"data:{mime};base64," + base64.b64encode(ruta.read_bytes()).decode()


def html(s: str) -> None:
    st.markdown(re.sub(r">\s+<", "><", s.strip()), unsafe_allow_html=True)


def titulo(texto: str) -> str:
    return f'<div class="ttl">{escape(texto)}</div>'


def plata(v: float) -> str:
    return "$ " + f"{v:,.0f}".replace(",", ".")


def fecha_txt(d: date | None) -> str:
    return d.strftime("%d/%m/%Y") if d else "—"


def fecha_corta(d: date | None) -> str:
    return d.strftime("%d/%m/%y") if d else "—"


def sumar_meses(d: date, n: int) -> date:
    m = d.month - 1 + n
    a, m = d.year + m // 12, m % 12 + 1
    return date(a, m, min(d.day, calendar.monthrange(a, m)[1]))


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
        return '<div class="pctrow"><span class="muted">Sin actividades</span></div>'
    return f'<div class="pctrow"><div class="bar"><i style="width:{pct}%"></i></div><b>{pct}%</b></div>'


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


def codigo_qr(pid: int) -> str:
    return f"CEC-{pid:04d}"


def qr_png(texto: str) -> bytes | None:
    try:
        import qrcode
    except ImportError:
        return None
    buf = io.BytesIO()
    qrcode.make(texto).save(buf, "PNG")
    return buf.getvalue()


# ───────────────────────────── CAPA DE DATOS (en memoria) ─────────────────────
def registrar_log(accion: str, detalle: str, archivo_nombre: str | None = None, archivo_bytes: bytes | None = None) -> None:
    s = st.session_state
    if "historial_logs" not in s:
        s.historial_logs = []
    s.historial_logs.insert(0, dict(
        fecha=date.today(),
        hora=date.today().strftime("%H:%M"),
        accion=accion,
        detalle=detalle,
        archivo_nombre=archivo_nombre,
        archivo_bytes=archivo_bytes
    ))


def iniciar_datos() -> None:
    if "participantes" in st.session_state:
        return
    hoy = date.today()
    P = lambda i, n, rol, estado: dict(  # noqa: E731
        id=i, nombre=n, correo=f"{n.lower().replace(' ', '')}@ejemplo.cl", telefono="+56 9 0000 00" + f"{i:02d}",
        rol=rol, descripcion="", estado=estado, carta_nombre=None, carta=None)
    st.session_state.participantes = [
        P(1, "Participante A", "Emprendedora", "Activa"),
        P(2, "Participante B", "Emprendedora", "Activa"),
        P(3, "Participante C", "Emprendedora", "Activa"),
        P(4, "Participante D", "Becada", "Activa"),
        P(5, "Participante E", "Mentora", "En validación de perfil"),
        P(6, "Participante F", "Becada", "Beca revocada"),
        P(7, "Participante G", "Emprendedora", "Activa"),
        P(8, "Participante H", "Emprendedora", "Activa"),
        P(9, "Participante I", "Emprendedora", "Activa"),
        P(10, "Participante J", "Becada", "Activa"),
        P(11, "Participante K", "Becada", "Beca vencida"),
    ]
    for pid in (1, 2):
        p = next(x for x in st.session_state.participantes if x["id"] == pid)
        p["carta_nombre"], p["carta"] = "carta_compromiso_demo.png", voucher_demo("Carta de compromiso")

    venc = {1: hoy + timedelta(days=3), 7: hoy + timedelta(days=8), 8: hoy + timedelta(days=10),
            9: hoy + timedelta(days=21), 2: hoy + timedelta(days=150), 3: hoy - timedelta(days=60)}
    st.session_state.membresias = {pid: dict(inicio=sumar_meses(v, -6), vencimiento=v) for pid, v in venc.items()}
    pagos = [(pid, sumar_meses(v, -6)) for pid, v in venc.items()]
    ids = [1, 2, 3, 7, 8, 9]
    for meses_atras, cantidad in [(5, 2), (4, 3), (3, 3), (2, 5), (1, 6), (0, 8)]:
        a_, m_ = divmod(hoy.year * 12 + hoy.month - 1 - meses_atras, 12)
        for k in range(cantidad):
            dia = min(2 + 3 * k, hoy.day if meses_atras == 0 else 28)
            pagos.append((ids[k % len(ids)], date(a_, m_ + 1, dia)))
    st.session_state.pagos = [
        dict(id=i + 1, participante_id=pid, fecha=f, monto=PRECIO_DEMO, metodo="Transferencia",
             comprobante_nombre="comprobante_demo.png", comprobante=voucher_demo(f"Pago #{i + 1}"))
        for i, (pid, f) in enumerate(pagos)
    ]
    
    # Inicializar donaciones
    st.session_state.donaciones = [
        dict(id=1, donante="Empresa Colaboradora S.A.", monto=150000, fecha=hoy - timedelta(days=20), comprobante_nombre="donacion_1.pdf", comprobante=voucher_demo("Donación corporativa"))
    ]

    B = lambda i, pid, desde, hasta, estado, motivo: dict(  # noqa: E731
        id=i, participante_id=pid, motivo=motivo, asignacion=desde, inicio=desde, termino=hasta, estado=estado)
    st.session_state.becas = [
        B(1, 4, hoy - timedelta(days=90), hoy + timedelta(days=90), "Activa", "Situación económica"),
        B(2, 10, hoy - timedelta(days=60), hoy + timedelta(days=120), "Activa", "Emprendimiento en etapa inicial"),
        B(3, 6, hoy - timedelta(days=120), hoy + timedelta(days=60), "Revocada", "Beca inicial"),
        B(4, 11, hoy - timedelta(days=300), hoy - timedelta(days=30), "Activa", "Beca inicial"),
    ]

    defs = [(63, "Taller", "Finanzas básicas", "Online"), (56, "Mentoría", "Mentoría 1 a 1", "Online"),
            (49, "Taller", "Marca personal", "Online"), (42, "Charla", "Charla inspiradora", "Presencial"),
            (35, "Coaching", "Sesión de coaching", "Online"), (28, "Taller", "Marketing digital", "Online"),
            (21, "Mentoría", "Mentoría 1 a 1", "Online"), (14, "Taller", "Marca personal", "Presencial"),
            (7, "Coaching", "Sesión de coaching", "Online"), (2, "Taller", "Finanzas básicas", "Online")]
    st.session_state.actividades = [dict(id=i + 1, tipo=t, nombre=n, fecha=hoy - timedelta(days=d), modalidad=m)
                                    for i, (d, t, n, m) in enumerate(defs)]
    nivel = {1: 9, 2: 7, 3: 5, 4: 9, 6: 4, 7: 8, 8: 6, 9: 7, 10: 8, 11: 5}
    st.session_state.asistencias = {(a["id"], pid) for a in st.session_state.actividades for pid, nv in nivel.items()
                                    if (pid * 7 + a["id"] * 3) % 10 < nv}
    
    # Log por defecto
    st.session_state.historial_logs = [
        dict(fecha=hoy - timedelta(days=1), hora="12:00", accion="Registro de participante", detalle="Se registró a Participante A como Emprendedora.", archivo_nombre=None, archivo_bytes=None),
        dict(fecha=hoy - timedelta(days=2), hora="15:30", accion="Asignación de beca", detalle="Se otorgó beca a Participante D.", archivo_nombre=None, archivo_bytes=None)
    ]


def participante(pid: int) -> dict:
    return next(p for p in st.session_state.participantes if p["id"] == pid)


def estado_pago(p: dict) -> str | None:
    b = beca_actual(p["id"])
    if b and estado_beca(b) == "Activa":
        return "Becado (exento)"
    m = st.session_state.membresias.get(p["id"])
    if not m:
        return None
    dias = (m["vencimiento"] - date.today()).days
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
    s.pagos.append(dict(id=len(s.pagos) + 1, participante_id=pid, fecha=fecha, monto=monto,
                        metodo=metodo, comprobante_nombre=archivo.name, comprobante=archivo.getvalue()))
    s.membresias[pid] = dict(inicio=fecha, vencimiento=sumar_meses(fecha, meses))
    participante(pid)["estado"] = "Activa"
    p_nom = participante(pid)['nombre']
    registrar_log("Registro de pago", f"Se registró pago de {plata(monto)} para {p_nom}.", archivo.name, archivo.getvalue())


def registrar_donacion(donante: str, monto: int, fecha: date, archivo) -> None:
    s = st.session_state
    s.donaciones.append(dict(id=len(s.donaciones) + 1, donante=donante, monto=monto, fecha=fecha,
                             comprobante_nombre=archivo.name if archivo else None, comprobante=archivo.getvalue() if archivo else None))
    registrar_log("Registro de donación", f"Se registró donación de {plata(monto)} por '{donante}'.", archivo.name if archivo else None, archivo.getvalue() if archivo else None)


def email_valido(c: str) -> bool:
    return re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", c) is not None


def guardar_participante() -> None:
    s = st.session_state
    nombre, correo = s.f_nombre.strip(), s.f_correo.strip().lower()
    carta = s.get(f"f_carta_{s.carta_n}")
    if not nombre or not correo or not s.f_rol:
        s.f_msg = ("error", "Completa nombre, correo y rol para guardar.")
    elif not email_valido(correo):
        s.f_msg = ("error", "El correo no tiene un formato válido.")
    elif any(p["correo"].lower() == correo for p in s.participantes):
        s.f_msg = ("error", "Ese correo ya está registrado: no se permiten duplicados.")
    else:
        estado = SIGUIENTE_PASO[s.f_rol][0]
        s.participantes.append(dict(
            id=max(p["id"] for p in s.participantes) + 1, nombre=nombre, correo=correo, telefono=s.f_tel.strip(),
            rol=s.f_rol, descripcion=s.f_desc.strip(), estado=estado,
            carta_nombre=carta.name if carta else None, carta=carta.getvalue() if carta else None))
        extra = "" if carta else " · falta la carta de compromiso"
        s.f_msg = ("ok", f"{nombre} quedó registrada como {s.f_rol.lower()} · siguiente paso: {estado.lower()}{extra}.")
        
        # Registrar en el log de acciones
        registrar_log("Registro de participante", f"Se agregó a {nombre} como {s.f_rol}.", carta.name if carta else None, carta.getvalue() if carta else None)

        s.f_nombre = s.f_correo = s.f_tel = s.f_desc = ""
        s.f_rol = None
        s.carta_n += 1


def beca_actual(pid: int) -> dict | None:
    recs = [b for b in st.session_state.becas if b["participante_id"] == pid]
    return max(recs, key=lambda b: b["id"]) if recs else None


def estado_beca(b: dict) -> str:
    return "Activa" if b["estado"] == "Activa" and b["termino"] >= date.today() else "Inactiva"


def detalle_inactiva(b: dict) -> str:
    return "Revocada" if b["estado"] == "Revocada" else "Vigencia terminada"


def asignar_beca(pid: int, motivo: str, inicio: date, termino: date) -> None:
    s = st.session_state
    s.becas.append(dict(id=max([b["id"] for b in s.becas] + [0]) + 1, participante_id=pid, motivo=motivo,
                        asignacion=date.today(), inicio=inicio, termino=termino, estado="Activa"))
    participante(pid)["estado"] = "Activa"
    p_nom = participante(pid)['nombre']
    registrar_log("Asignación de beca", f"Se otorgó beca a {p_nom} por '{motivo}'.")


def revocar_beca(pid: int, motivo: str) -> None:
    b = beca_actual(pid)
    b["estado"], b["motivo_revocacion"], b["fecha_revocacion"] = "Revocada", motivo, date.today()
    participante(pid)["estado"] = "Beca revocada"
    p_nom = participante(pid)['nombre']
    registrar_log("Revocación de beca", f"Se revocó la beca a {p_nom}. Motivo: {motivo}")


def actividades_filtradas(tipo: str = "Todas", fecha_filtro: date | None = None, modalidad: str = "Todas") -> list[dict]:
    return [a for a in st.session_state.actividades
            if tipo in ("Todas", a["tipo"]) and modalidad in ("Todas", a["modalidad"])
            and (fecha_filtro is None or a["fecha"] == fecha_filtro)]


def pct_asistencia(pid: int, acts: list[dict]) -> int | None:
    if not acts:
        return None
    return round(100 * sum((a["id"], pid) in st.session_state.asistencias for a in acts) / len(acts))


def asistencia_promedio() -> int:
    P = [p for p in st.session_state.participantes if p["estado"] == "Activa"]
    vals = [v for v in (pct_asistencia(p["id"], st.session_state.actividades) for p in P) if v is not None]
    return round(sum(vals) / len(vals)) if vals else 0


def registrar_asistencia(tipo: str, nombre: str, fecha: date, modalidad: str, pids: list[int]) -> None:
    s = st.session_state
    aid = max(a["id"] for a in s.actividades) + 1 if s.actividades else 1
    s.actividades.append(dict(id=aid, tipo=tipo, nombre=nombre or tipo, fecha=fecha, modalidad=modalidad))
    s.asistencias |= {(aid, pid) for pid in pids}
    registrar_log("Registro de asistencia", f"Se registró asistencia para la actividad '{nombre or tipo}' ({len(pids)} asistentes).")


def csv_asistencia(acts: list[dict]) -> bytes:
    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow(["Fecha", "Tipo", "Actividad", "Modalidad", "Participante", "Rol", "Asistió"])
    for a in sorted(acts, key=lambda x: x["fecha"]):
        for p in st.session_state.participantes:
            if p["estado"] == "Activa" or (a["id"], p["id"]) in st.session_state.asistencias:
                w.writerow([fecha_txt(a["fecha"]), a["tipo"], a["nombre"], a["modalidad"], p["nombre"], p["rol"],
                            "Sí" if (a["id"], p["id"]) in st.session_state.asistencias else "No"])
    return buf.getvalue().encode("utf-8-sig")


def escanear() -> None:
    s = st.session_state
    codigo, s.qr_code = s.qr_code.strip().upper(), ""
    m = re.fullmatch(r"CEC-(\d+)", codigo)
    if not m:
        s.qr_msg = ("error", "Código no reconocido. Debe verse como CEC-0001.")
    elif not any(p["id"] == int(m.group(1)) for p in s.participantes):
        s.qr_msg = ("error", f"No existe ninguna participante con el código {codigo}.")
    else:
        pid = int(m.group(1))
        s.asistencias.add((s.qr_act, pid))
        p_nom = participante(pid)['nombre']
        s.qr_msg = ("ok", f"Asistencia registrada: {p_nom}.")
        registrar_log("Escaneo QR Asistencia", f"Se registró asistencia por QR para {p_nom}.")


# ───────────────────────────────── DIÁLOGOS ──────────────────────────────────
@st.dialog("Registrar pago por transferencia", width="large")
def dialogo_pago() -> None:
    elegibles = [p for p in st.session_state.participantes if estado_pago(p) != "Becado (exento)"]
    opciones = {f"{p['nombre']} · {p['rol']}": p["id"] for p in elegibles}
    sel = st.selectbox("Participante", list(opciones))
    c1, c2 = st.columns(2)
    monto = c1.number_input("Monto ($)", min_value=0, step=1000, value=PRECIO_DEMO)
    metodo = c2.selectbox("Método de pago", ["Transferencia", "PayPal", "Voucher"])
    c3, c4 = st.columns(2)
    fecha = c3.date_input("Fecha de pago", value=date.today(), format="DD/MM/YYYY")
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
    fecha = c2.date_input("Fecha de donación", value=date.today(), format="DD/MM/YYYY")
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


@st.dialog("Historial de pagos y donaciones", width="large")
def dialogo_historial() -> None:
    tabs = st.tabs(["Membresías", "Donaciones"])
    with tabs[0]:
        hist = sorted(st.session_state.pagos, key=lambda x: (x["fecha"], x["id"]), reverse=True)
        html(tabla_html(["Fecha", "Participante", "Monto", "Método", "Comprobante"],
                        [[fecha_txt(x["fecha"]), escape(participante(x["participante_id"])["nombre"]), plata(x["monto"]),
                          escape(x["metodo"]), "Sí" if x["comprobante"] else "—"] for x in hist]))
    with tabs[1]:
        dones = sorted(st.session_state.donaciones, key=lambda x: x["fecha"], reverse=True)
        html(tabla_html(["Fecha", "Donante", "Monto", "Comprobante"],
                        [[fecha_txt(x["fecha"]), escape(d["donante"]), plata(d["monto"]), "Sí" if d["comprobante"] else "—"] for x in dones]))


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
            registrar_log("Subida de documento", f"Se actualizó la carta de compromiso de {p['nombre']}.", archivo.name, archivo.getvalue())
            st.session_state.flash = f"Carta de compromiso guardada para {p['nombre']}."
            st.rerun()


@st.dialog("Registrar asistencia", width="large")
def dialogo_asistencia() -> None:
    c1, c2 = st.columns(2)
    tipo = c1.selectbox("Tipo de actividad", TIPOS_ACTIVIDAD)
    modalidad = c2.selectbox("Modalidad", MODALIDADES)
    nombre = st.text_input("Nombre de la actividad (opcional)", placeholder="Ej. Marca personal")
    fecha = st.date_input("Fecha", value=date.today(), format="DD/MM/YYYY")
    P = st.session_state.participantes
    asistentes = st.multiselect("Asistentes", [p["id"] for p in P], placeholder="Elige a las participantes",
                                format_func=lambda i: f"{participante(i)['nombre']} · {participante(i)['rol']}")
    if st.button("Guardar asistencia", key="btn_guardar_asist"):
        if not asistentes:
            st.error("Elige al menos una participante.")
        else:
            registrar_asistencia(tipo, nombre.strip(), fecha, modalidad, asistentes)
            st.session_state.flash = f"Asistencia registrada: {tipo.lower()} del {fecha_txt(fecha)} ({len(asistentes)} participantes)."
            st.rerun()


def formulario_beca(k: str) -> None:
    n = st.session_state.beca_n
    con_beca = {b["participante_id"] for b in st.session_state.becas if estado_beca(b) == "Activa"}
    elegibles = [p["id"] for p in st.session_state.participantes if p["id"] not in con_beca]
    pid = st.selectbox("Participante", elegibles, index=None, placeholder="Elige a la participante", key=f"b_{k}_p{n}",
                       format_func=lambda i: f"{participante(i)['nombre']} · {participante(i)['rol']}")
    motivo = st.text_input("Motivo", placeholder="Describe el motivo", key=f"b_{k}_m{n}")
    html('<div style="font-weight:700;font-size:13px;margin-bottom:2px">Período de vigencia</div>')
    c1, c2 = st.columns(2)
    inicio = c1.date_input("Inicio", value=date.today(), format="DD/MM/YYYY", key=f"b_{k}_i{n}")
    termino = c2.date_input("Término", value=sumar_meses(date.today(), 6), format="DD/MM/YYYY", key=f"b_{k}_t{n}")
    if st.button("Guardar", key=f"btn_beca_{k}", width="stretch"):
        if pid is None or not motivo.strip():
            st.error("Elige a la participante e indica el motivo.")
        elif termino <= inicio:
            st.error("El término debe ser posterior al inicio.")
        else:
            asignar_beca(pid, motivo.strip(), inicio, termino)
            st.session_state.beca_n += 1
            st.session_state.flash = f"Beca asignada a {participante(pid)['nombre']}."
            st.rerun()


@st.dialog("Asignar beca", width="large")
def dialogo_asignar_beca() -> None:
    formulario_beca("dlg")


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
    inicio = c1.date_input("Nuevo inicio", value=date.today(), format="DD/MM/YYYY")
    termino = c2.date_input("Nuevo término", value=sumar_meses(date.today(), 6), format="DD/MM/YYYY")
    if st.button("Renovar beca", key=f"btn_renovar_{pid}"):
        if termino <= inicio:
            st.error("El término debe ser posterior al inicio.")
        else:
            asignar_beca(pid, "Renovación de beca", inicio, termino)
            st.session_state.flash = f"Beca renovada a {participante(pid)['nombre']}."
            st.rerun()


# ─────────────────────────────────── PÁGINAS ─────────────────────────────────
def pagina_panel() -> None:
    hoy = date.today()
    html(f'<div class="head">{titulo("Panel general")}<div class="hello"><div><b>¡Hola, {escape(NOMBRE_USUARIA)}!</b>'
         f'<span>Qué bueno verte de nuevo</span></div><img src="{b64("equipo.jpg")}"></div></div>')

    P, filas = st.session_state.participantes, filas_pagos()
    activas = sum(p["estado"] == "Activa" for p in P)
    por_vencer = [f for f in filas if f["vence"] and 0 <= (f["vence"] - hoy).days <= DIAS_ALERTA]
    ultimas = [b for b in (beca_actual(p["id"]) for p in P) if b]
    becas_act = sum(estado_beca(b) == "Activa" for b in ultimas)
    becas_rev = sum(b["estado"] == "Revocada" for b in ultimas)
    
    ingreso_mes = sum(x["monto"] for x in st.session_state.pagos
                      if (x["fecha"].year, x["fecha"].month) == (hoy.year, hoy.month))
    donacion_mes = sum(x["monto"] for x in st.session_state.donaciones
                       if (x["fecha"].year, x["fecha"].month) == (hoy.year, hoy.month))
    
    metricas = [("Participantes activas", str(activas)), (f"Por vencer ({DIAS_ALERTA} days)", str(len(por_vencer))),
                ("Asistencia promedio", f"{asistencia_promedio()}%"), ("Becas activas / rev.", f"{becas_act} / {becas_rev}"),
                ("Ingresos y Donac. mes", plata(ingreso_mes + donacion_mes))]
    for col, (lbl, val) in zip(st.columns(5), metricas):
        with col, st.container(key=f"card_m_{lbl}"):
            html(f'<div class="m-l">{escape(lbl)}</div><div class="m-v{" long" if len(val) > 7 else ""}">{escape(val)}</div>')

    izq, der = st.columns([1.36, 1])
    with izq, st.container(key="card_ingresos"):
        meses = []
        for i in range(5, -1, -1):
            a, m = divmod(hoy.year * 12 + hoy.month - 1 - i, 12)
            meses.append((a, m + 1))
        tot = [sum(x["monto"] for x in st.session_state.pagos if (x["fecha"].year, x["fecha"].month) == k) for k in meses]
        mx = max(tot) or 1
        tonos = ["#FBF0C8", "#F6E2A5", "#FBF0C8", "#E0BC3E", "#F6E2A5", "#E0BC3E"]
        barras = "".join(f'<div style="height:{max(4, round(t / mx * 100))}%;background:{c}" title="{plata(t)}"></div>'
                         for t, c in zip(tot, tonos))
        etiquetas = "".join(f"<span>{MESES[m - 1]}</span>" for _, m in meses)
        html(f'<div class="sub">Ingresos por membresías</div><div class="bars">{barras}</div><div class="lbls">{etiquetas}</div>')
    with der, st.container(key="card_por_vencer"):
        html('<div class="sub">Membresías por vencer</div>')
        prox = sorted([f for f in filas if f["vence"] and 0 <= (f["vence"] - hoy).days <= 30], key=lambda f: f["vence"])
        if not prox:
            st.caption("No hay vencimientos en los próximos 30 días.")
        for f in prox[:6]:
            d = (f["vence"] - hoy).days
            clase = "c-vencer" if d <= DIAS_ALERTA else ""
            html(f'<div style="display:flex;justify-content:space-between;align-items:center;padding:5px 0"><span>{escape(f["p"]["nombre"])}</span>'
                 f'<span class="chip {clase}">{d} días</span></div>')
        if st.button("Enviar recordatorio", key="btn_recordatorio", width="stretch"):
            st.toast(f"Recordatorio registrado para {len(prox)} participante(s). (Simulado: aún no se envían correos.)")


def pagina_registro() -> None:
    html(titulo("Registrar participante"))
    izq, der = st.columns([1.36, 1])
    with izq, st.container(key="card_form"):
        c1, c2 = st.columns(2)
        c1.text_input("Nombre completo", placeholder="Ej. María Pérez", key="f_nombre")
        c2.text_input("Correo electrónico", placeholder="nombre@correo.com", key="f_correo")
        c1.text_input("Teléfono", placeholder="+56 9 0000 0000", key="f_tel")
        c2.selectbox("Rol", ROLES, index=None, placeholder="Elige un rol", key="f_rol")
        st.text_area("Descripción profesional", placeholder="Trayectoria y especialidad", height=110, key="f_desc")
        st.file_uploader("Carta de compromiso (imagen o documento)", type=CARTA_TIPOS, key=f"f_carta_{st.session_state.carta_n}",
                         help="Puedes subirla ahora o más tarde desde la lista de participantes.")
        html('<div class="info">El sistema valida el correo: formato correcto y sin duplicados.</div>')
        st.button("Guardar participante", key="btn_guardar_part", on_click=guardar_participante)
        msg = st.session_state.pop("f_msg", None)
        if msg:
            (st.success if msg[0] == "ok" else st.error)(msg[1])
    with der, st.container(key="card_clasif"):
        sel = st.session_state.get("f_rol")
        cajas = "".join(f'<div class="clasif {"sel" if r == sel else ""}"><span class="chip">{r}</span><div>{SIGUIENTE_PASO[r][1]}</div></div>'
                        for r in ROLES)
        html(f'<div class="sub" style="margin-bottom:8px">Clasificación y siguiente paso</div>{cajas}'
             f'<img class="foto" src="{b64("equipo.jpg")}">')

    with st.container(key="card_lista"):
        P = st.session_state.participantes
        html(f'<div class="sub">Participantes registradas ({len(P)})</div>')
        anchos = [1.6, 2.2, 1.5, 1.9, 1.2]
        for col, t in zip(st.columns(anchos), ["Nombre", "Correo", "Rol", "Estado", "Carta de compromiso"]):
            col.markdown(f'<div class="th">{t}</div>', unsafe_allow_html=True)
        st.markdown('<div class="hline"></div>', unsafe_allow_html=True)
        for p in reversed(P):
            cols = st.columns(anchos, vertical_alignment="center")
            cols[0].markdown(f'<div class="td">{escape(p["nombre"])}</div>', unsafe_allow_html=True)
            cols[1].markdown(f'<div class="td">{escape(p["correo"])}</div>', unsafe_allow_html=True)
            cols[2].markdown(f'<div class="td"><span class="chip">{escape(p["rol"])}</span></div>', unsafe_allow_html=True)
            cols[3].markdown(f'<div class="td">{escape(p["estado"])}</div>', unsafe_allow_html=True)
            if p["carta"]:
                if cols[4].button("Ver carta", key=f"ver_carta_{p['id']}"):
                    dialogo_ver_carta(p["id"])
            elif cols[4].button("Subir carta", key=f"ver_subir_{p['id']}"):
                dialogo_subir_carta(p["id"])
            st.markdown('<div class="fila"></div>', unsafe_allow_html=True)


def pagina_pagos() -> None:
    c1, c2, c3 = st.columns([2, 1, 1], vertical_alignment="center")
    c1.markdown(titulo("Membresías, Pagos y Donaciones"), unsafe_allow_html=True)
    if c2.button("+ Registrar pago", key="btn_nuevo_pago", width="stretch"):
        dialogo_pago()
    if c3.button("+ Registrar donación", key="btn_nueva_donacion", width="stretch"):
        dialogo_donacion()

    html('<div style="display:flex;gap:10px;margin:-6px 0 4px 0">' + "".join(chip(e) for e in ESTADOS) + "</div>")

    with st.container(key="card_tabla"):
        anchos = [2, 1.1, 1.2, 1.5, 1.2]
        for col, t in zip(st.columns(anchos), ["Participante", "Inicio", "Vencimiento", "Estado", "Comprobante"]):
            col.markdown(f'<div class="th">{t}</div>', unsafe_allow_html=True)
        st.markdown('<div class="hline"></div>', unsafe_allow_html=True)
        for f in filas_pagos():
            p = f["p"]
            cols = st.columns(anchos, vertical_alignment="center")
            cols[0].markdown(f'<div class="td">{escape(p["nombre"])}</div>', unsafe_allow_html=True)
            cols[1].markdown(f'<div class="td">{fecha_txt(f["inicio"])}</div>', unsafe_allow_html=True)
            cols[2].markdown(f'<div class="td">{fecha_txt(f["vence"])}</div>', unsafe_allow_html=True)
            cols[3].markdown(f'<div class="td">{chip(f["estado"])}</div>', unsafe_allow_html=True)
            if ultimo_comprobante(p["id"]):
                if cols[4].button("Ver archivo", key=f"ver_{p['id']}"):
                    dialogo_ver(p["id"])
            else:
                cols[4].markdown('<div class="td">—</div>', unsafe_allow_html=True)
            st.markdown('<div class="fila"></div>', unsafe_allow_html=True)

    a, b = st.columns(2)
    with a, st.container(key="card_alerta"):
        html(f'<div class="sub">Alerta automática</div><div class="muted" style="font-size:14px">'
             f'Aviso en el panel cuando falten {DIAS_ALERTA} días o menos para el vencimiento.</div>')
    with b, st.container(key="card_hist"):
        html('<div class="sub">Historial financiero completo</div><div class="muted" style="font-size:14px">'
             'Consulta pagos, membresías y donaciones registradas con comprobantes.</div>')
        if st.button("Ver historial financiero", key="ver_historial"):
            dialogo_historial()


def pagina_asistencia() -> None:
    s = st.session_state
    acts_todas = s.actividades

    c1, c2, c3 = st.columns([3.4, 0.9, 1.5], vertical_alignment="center")
    c1.markdown(titulo("Asistencia"), unsafe_allow_html=True)
    
    # Asistencia simplificada: Solo un selector de tipo y un campo de fecha idéntico a los demás
    f1, f2, f3, _ = st.columns([1.5, 1.6, 1.4, 1.1])
    tipo = f1.selectbox("Actividad", ["Todas"] + TIPOS_ACTIVIDAD, label_visibility="collapsed", key="fa_tipo",
                        format_func=lambda x: f"Actividad: {x}")
    
    # Cuadro uniforme con calendario desplegable directo (sin botones extras de activar/desactivar)
    fecha_filtro = f2.date_input("Fecha específica", value=None, format="DD/MM/YYYY", label_visibility="collapsed", key="fa_fecha_sel", help="Selecciona una fecha específica")

    modalidad = f3.selectbox("Modalidad", ["Todas"] + MODALIDADES, label_visibility="collapsed", key="fa_mod",
                             format_func=lambda x: f"Modalidad: {x}")
    
    acts = actividades_filtradas(tipo, fecha_filtro, modalidad)

    c2.download_button("Exportar", csv_asistencia(acts), file_name="asistencia.csv", mime="text/csv", key="btn_exportar")
    if c3.button("Registrar asistencia", key="btn_reg_asistencia", width="stretch"):
        dialogo_asistencia()

    izq, der = st.columns([1.5, 1])
    with izq, st.container(key="card_asis_tabla"):
        anchos = [2, 1.8, 2.6]
        for col, t in zip(st.columns(anchos), ["Participante", "Actividad", "% asistencia"]):
            col.markdown(f'<div class="th">{t}</div>', unsafe_allow_html=True)
        st.markdown('<div class="hline"></div>', unsafe_allow_html=True)
        hay = False
        for p in s.participantes:
            pct = pct_asistencia(p["id"], acts)
            if pct is None or p["estado"] != "Activa":
                continue
            hay = True
            asistio = [t for t in TIPOS_ACTIVIDAD if any(a["tipo"] == t and (a["id"], p["id"]) in s.asistencias for a in acts)]
            cols = st.columns(anchos, vertical_alignment="center")
            cols[0].markdown(f'<div class="td">{escape(p["nombre"])}</div>', unsafe_allow_html=True)
            resumen = ", ".join(asistio[:2]) + (f" +{len(asistio) - 2}" if len(asistio) > 2 else "")
            cols[1].markdown(f'<div class="td">{escape(resumen) or "—"}</div>', unsafe_allow_html=True)
            cols[2].markdown(barra(pct), unsafe_allow_html=True)
            st.markdown('<div class="fila"></div>', unsafe_allow_html=True)
        if not hay:
            st.caption("No hay actividades con esos filtros.")
        st.caption(f"{len(acts)} actividad(es) en el filtro. El porcentaje es: asistió ÷ actividades registradas.")

    with der, st.container(key="card_qr"):
        html('<div class="sub" style="text-align:center">Escanear QR de la participante</div>'
             '<div class="qrbox"><svg viewBox="0 0 100 100"><rect x="1.5" y="1.5" width="97" height="97" rx="10" fill="#FFFEFA" stroke="#E0BC3E" stroke-width="3"/>'
             '<rect x="14" y="14" width="22" height="22" fill="#D7AE00"/><rect x="64" y="14" width="22" height="22" fill="#D7AE00"/>'
             '<rect x="14" y="64" width="22" height="22" fill="#D7AE00"/><rect x="44" y="44" width="12" height="12" fill="#E0BC3E"/>'
             '<rect x="64" y="64" width="10" height="10" fill="#E0BC3E"/><rect x="44" y="14" width="10" height="10" fill="#E0BC3E"/></svg>'
             '<div class="muted" style="font-size:14px">o registro manual</div></div>')
        if s.actividades:
            recientes = [a["id"] for a in sorted(s.actividades, key=lambda x: (x["fecha"], x["id"]), reverse=True)][:15]
            por_id = {a["id"]: a for a in s.actividades}
            st.selectbox("Actividad para el escaneo", recientes, key="qr_act",
                         format_func=lambda i: f"{por_id[i]['tipo']} · {por_id[i]['nombre']} · {fecha_corta(por_id[i]['fecha'])}")
            st.text_input("Código leído (lector QR + Enter)", placeholder="CEC-0001", key="qr_code", on_change=escanear)
            msg = s.pop("qr_msg", None)
            if msg:
                (st.success if msg[0] == "ok" else st.error)(msg[1])
        if st.button("Registro manual", key="btn_manual", width="stretch"):
            dialogo_asistencia()
        with st.expander("Generar el QR de una participante"):
            pid = st.selectbox("Participante", [p["id"] for p in s.participantes], key="qr_part",
                               format_func=lambda i: participante(i)["nombre"])
            png = qr_png(codigo_qr(pid))
            if png:
                st.image(png, width=150, caption=codigo_qr(pid))
                st.download_button("Descargar QR", png, file_name=f"{codigo_qr(pid)}.png", mime="image/png", key="btn_dl_qr")
            else:
                st.info("Para generar QR instala el paquete: pip install qrcode[pil]")


def pagina_becas() -> None:
    s = st.session_state
    c1, c2 = st.columns([3, 1], vertical_alignment="center")
    c1.markdown(titulo("Gestión de becas"), unsafe_allow_html=True)
    if c2.button("Asignar beca", key="btn_asignar_beca", width="stretch"):
        dialogo_asignar_beca()

    izq, der = st.columns([2.15, 1])
    with izq, st.container(key="card_becas_tabla"):
        html('<div class="sub">Becadas</div>')
        anchos = [1.9, 1.1, 2.2, 0.9, 1.1, 1.3]
        for col, t in zip(st.columns(anchos), ["Nombre", "Asignación", "Vigencia (inicio – fin)", "% asist.", "Estado", "Acción"]):
            col.markdown(f'<div class="th">{t}</div>', unsafe_allow_html=True)
        st.markdown('<div class="hline"></div>', unsafe_allow_html=True)
        registros = [(p, beca_actual(p["id"])) for p in s.participantes]
        registros = sorted([(p, b) for p, b in registros if b], key=lambda x: (estado_beca(x[1]) != "Activa", x[0]["id"]))
        if not registros:
            st.caption("Todavía no hay becas registradas.")
        for p, b in registros:
            est = estado_beca(b)
            hasta = min(b["termino"], date.today())
            pct = pct_asistencia(p["id"], [a for a in s.actividades if b["inicio"] <= a["fecha"] <= hasta])
            cols = st.columns(anchos, vertical_alignment="center")
            cols[0].markdown(f'<div class="td">{escape(p["nombre"])}</div>', unsafe_allow_html=True)
            cols[1].markdown(f'<div class="td nw">{fecha_corta(b["asignacion"])}</div>', unsafe_allow_html=True)
            cols[2].markdown(f'<div class="td nw">{fecha_corta(b["inicio"])} – {fecha_corta(b["termino"])}</div>', unsafe_allow_html=True)
            cols[3].markdown(f'<div class="td">{"—" if pct is None else f"{pct}%"}</div>', unsafe_allow_html=True)
            cols[4].markdown(f'<div class="td">{chip(est)}</div>', unsafe_allow_html=True)
            if est == "Activa":
                if cols[5].button("Revocar", key=f"ver_rev_{p['id']}"):
                    dialogo_revocar(p["id"])
            elif cols[5].button("Renovar", key=f"ver_ren_{p['id']}", help=detalle_inactiva(b)):
                dialogo_renovar(p["id"])
            st.markdown('<div class="fila"></div>', unsafe_allow_html=True)
        st.caption("Estado «Inactiva»: beca revocada o con la vigencia terminada. El % de asistencia se mide dentro de la vigencia.")
    with der, st.container(key="card_becas_form"):
        html('<div class="sub">Asignar o revocar beca</div>')
        formulario_beca("card")


def pagina_seguimiento() -> None:
    html(titulo("Seguimiento e impacto de participantes"))
    with st.container(key="card_seg"):
        html('<div class="sub">Métricas de avance y participación</div>')
        P = st.session_state.participantes
        anchos = [2, 1.5, 1.8, 1.5]
        for col, t in zip(st.columns(anchos), ["Participante", "Rol", "Estado actual", "Asistencia Global"]):
            col.markdown(f'<div class="th">{t}</div>', unsafe_allow_html=True)
        st.markdown('<div class="hline"></div>', unsafe_allow_html=True)
        for p in P:
            pct = pct_asistencia(p["id"], st.session_state.actividades)
            cols = st.columns(anchos, vertical_alignment="center")
            cols[0].markdown(f'<div class="td">{escape(p["nombre"])}</div>', unsafe_allow_html=True)
            cols[1].markdown(f'<div class="td"><span class="chip">{escape(p["rol"])}</span></div>', unsafe_allow_html=True)
            cols[2].markdown(f'<div class="td">{escape(p["estado"])}</div>', unsafe_allow_html=True)
            cols[3].markdown(f'<div class="td">{"—" if pct is None else f"{pct}%"}</div>', unsafe_allow_html=True)
            st.markdown('<div class="fila"></div>', unsafe_allow_html=True)


def pagina_reportes() -> None:
    html(titulo("Reportes y métricas"))
    c1, c2 = st.columns(2)
    with c1, st.container(key="card_rep_1"):
        html('<div class="sub">Resumen Financiero y Donaciones</div>')
        total_recaudado = sum(x["monto"] for x in st.session_state.pagos)
        total_donaciones = sum(x["monto"] for x in st.session_state.donaciones)
        st.metric("Ingresos históricos (Membresías)", plata(total_recaudado))
        st.metric("Total histórico (Donaciones)", plata(total_donaciones))
        st.metric("Total general recaudado", plata(total_recaudado + total_donaciones))
    with c2, st.container(key="card_rep_2"):
        html('<div class="sub">Resumen Operativo</div>')
        total_act = len(st.session_state.actividades)
        st.metric("Actividades realizadas", total_act)
        st.metric("Asistencia general promedio", f"{asistencia_promedio()}%")


def pagina_historial() -> None:
    html(titulo("Historial de acciones de coordinadoras (Auditoría)"))
    with st.container(key="card_historial_gen"):
        html('<div class="sub">Registro cronológico de actividades relevantes y descarga de respaldos</div>')
        logs = st.session_state.get("historial_logs", [])
        if not logs:
            st.info("No hay acciones registradas aún.")
        for idx, log in enumerate(logs):
            c1, c2, c3, c4 = st.columns([1.2, 1.8, 3.5, 1.5], vertical_alignment="center")
            c1.markdown(f'<div class="td nw"><b>{fecha_txt(log["fecha"])} {log["hora"]}</b></div>', unsafe_allow_html=True)
            c2.markdown(f'<div class="td"><span class="chip">{escape(log["accion"])}</span></div>', unsafe_allow_html=True)
            c3.markdown(f'<div class="td">{escape(log["detalle"])}</div>', unsafe_allow_html=True)
            if log["archivo_bytes"] and log["archivo_nombre"]:
                c4.download_button("Descargar archivo", log["archivo_bytes"], file_name=log["archivo_nombre"], key=f"dl_log_{idx}")
            else:
                c4.markdown('<div class="td">—</div>', unsafe_allow_html=True)
            st.markdown('<div class="fila"></div>', unsafe_allow_html=True)


# ─────────────────────────────── NAVEGACIÓN Y MAIN ───────────────────────────
iniciar_datos()
st.session_state.setdefault("pagina", "Panel")
st.session_state.setdefault("carta_n", 0)
st.session_state.setdefault("beca_n", 0)


def ir(destino: str) -> None:
    st.session_state.pagina = destino


with st.sidebar:
    html(f'<img class="logo" src="{b64("logo.png")}">')
    for nombre, icono in NAV:
        activa = st.session_state.pagina == nombre
        st.button(nombre, key=f"{'navon' if activa else 'nav'}_{nombre}", icon=f":material/{icono}:",
                  on_click=ir, args=(nombre,), width="stretch")

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
    "Historial": pagina_historial
}
pagina = st.session_state.pagina
if pagina in PAGINAS:
    PAGINAS[pagina]()
else:
    pagina_pronto(pagina)