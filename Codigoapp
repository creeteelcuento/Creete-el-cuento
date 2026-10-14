"""
Créete el Cuento · Sistema de gestión interno (prototipo funcional)

Páginas incluidas: Panel general · Registrar participante · Membresías y pagos.
El menú lateral funciona con botones; el resto de las secciones muestran una
pantalla "próximamente".

DATOS: por ahora todo vive en memoria (st.session_state) con datos ficticios,
para que el prototipo corra sin base de datos. Las funciones de la sección
"CAPA DE DATOS" son el único lugar que habrá que cambiar para conectar Supabase.

Ejecutar:  streamlit run app.py
"""
from __future__ import annotations

import base64
import calendar
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
DIAS_ALERTA = 10                 # R-07: alerta cuando faltan 10 días o menos
PRECIO_DEMO = 25000              # monto ficticio solo para datos de ejemplo
ASISTENCIA_DEMO = 86             # placeholder hasta construir el módulo de asistencia
ROLES = ["Mentora", "Emprendedora", "Becada"]
# Colores (cámbialos aquí si quieres ajustar la paleta)
COLOR_FONDO = "#EDEDEA"      # fondo del área principal
COLOR_MENU = "#F5EED7"       # amarillo pastel del menú lateral
COLOR_BORDE = "#3A3A3A"      # bordes negros/carbón
COLOR_TEXTO = "#1F1F1F"      # letras
COLOR_ORO = "#D7AE00"        # dorado de la marca
COLOR_BOTON = "#E6C23A"      # amarillo de botones
ESTADOS = ["Pagado", "Vencido", "Por vencer", "Becado (exento)"]
MESES = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]
NAV = [
    ("Panel", "dashboard"), ("Participantes", "group"), ("Pagos", "credit_card"),
    ("Asistencia", "check"), ("Becas", "workspace_premium"), ("Seguimiento", "bar_chart"),
    ("Reportes", "description"), ("Historial", "schedule"),
]

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

/* ── barra lateral ── */
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

/* ── títulos ── */
.ttl {font-family:'Fraunces', serif !important; font-size:28px; font-weight:600; color:#2B2B2B; margin:0 0 18px 0; line-height:1.2;}
.head .ttl {margin-bottom:0;}
.ttl:after {content:""; display:block; width:56px; height:4px; background:@ORO; border-radius:3px; margin-top:6px;}
.head {display:flex; justify-content:space-between; align-items:center; margin-bottom:4px;}
.hello {display:flex; align-items:center; gap:14px; text-align:right; font-size:14px;}
.hello span {display:block; font-size:12px; color:#6B6B6B;}
.hello img {width:130px; height:62px; object-fit:cover !important; border:1.5px solid @BORDE; border-radius:14px; box-shadow:3px 3px 0 #F1DD8E;}

/* ── tarjetas ── */
[class*="st-key-card_"] {background:#fff; border:1.5px solid @BORDE; border-radius:16px; padding:18px; box-shadow:3px 3px 0 #F1DD8E; gap:.6rem;}
[class*="st-key-card_m_"] {min-height:120px;}
.st-key-card_ingresos, .st-key-card_por_vencer {min-height:calc(100vh - 275px);}
.st-key-card_form, .st-key-card_clasif {min-height:calc(100vh - 118px);}
.m-l {font-size:13px; color:#6B6B6B; min-height:36px; line-height:1.3;}
.m-v {font-size:30px; font-weight:800; line-height:1.1; white-space:nowrap;}
.m-v.long {font-size:23px; padding-top:5px;}
.sub {font-weight:700; font-size:14px; margin-bottom:4px;}
.muted {color:#6B6B6B; font-size:13px;}

/* ── botones ── */
.stButton > button, .stFormSubmitButton > button {border:1.5px solid @BORDE; background:@BOTON; color:@TEXTO; border-radius:12px; min-height:44px; box-shadow:2px 2px 0 @BORDE; padding:0 20px;}
.stButton > button:hover {background:#EDD05E; border-color:@BORDE; color:@TEXTO;}
.stButton > button p {font-weight:700; font-size:14px; color:@TEXTO;}
[class*="st-key-ver_"] button {background:transparent !important; border:0 !important; box-shadow:none !important; min-height:0; padding:0 !important; justify-content:flex-start;}
[class*="st-key-ver_"] button p {font-weight:400 !important; text-decoration:none;}
[class*="st-key-ver_"] button:hover p {text-decoration:underline;}

/* ── campos ── */
[data-testid="stWidgetLabel"] p {font-weight:700; font-size:13px;}
[data-testid="stTextInputRootElement"], [data-testid="stTextAreaRootElement"], [data-testid="stSelectbox"] [data-baseweb="select"] > div, [data-testid="stDateInputField"], [data-testid="stNumberInputContainer"] {border-radius:12px !important; border:1.5px solid #EBDDB0 !important; background:#FFFEFA !important;}
[data-testid="stTextInputRootElement"] {min-height:44px;}
[data-testid="stSelectbox"] div:has(> input), [data-testid="stDateInput"] div:has(> input) {border-radius:12px !important; border:1.5px solid #EBDDB0 !important; background:#FFFEFA !important;}
[class*="st-key-ver_"] {padding-top:3px;}
.st-key-card_alerta, .st-key-card_hist {min-height:112px;}
.st-key-btn_recordatorio {margin-top:14px;}
.info {background:#FBF0C8; color:@TEXTO; border-radius:10px; padding:10px 14px; font-size:13px; margin-bottom:10px;}

/* ── chips y clasificación ── */
.chip {display:inline-block; padding:3px 10px; border-radius:99px; font-size:12px; font-weight:700; border:1px solid #706F6F; color:@TEXTO; background:#FBF0C8; white-space:nowrap;}
.c-pagado {background:#D9EBC8;} .c-vencer {background:#FBE3B0;} .c-vencido {background:#F6C9B8;} .c-exento {background:#E8DDF0;}
.clasif {background:#FFFCEF; border:1.5px solid transparent; border-radius:12px; padding:12px 14px; margin-bottom:10px; font-size:14px;}
.clasif .chip {margin-bottom:6px;}
.clasif.sel {border-color:@BORDE; box-shadow:2px 2px 0 @ORO; background:#fff;}
.foto {width:100%; height:150px; object-fit:cover !important; border:1.5px solid @BORDE; border-radius:14px; box-shadow:3px 3px 0 #F1DD8E; margin-top:4px;}

/* ── gráfico ── */
.bars {display:flex; align-items:flex-end; gap:18px; height:calc(100vh - 430px); min-height:180px; padding:0 8px; border-bottom:2px solid #F5ECD3; margin-top:14px;}
.bars div {flex:1; border-radius:8px 8px 0 0;}
.lbls {display:flex; justify-content:space-around; font-size:12px; color:#6B6B6B; margin-top:8px;}

/* ── tablas ── */
.th {font-size:12px; font-weight:700; color:#6B6B6B; padding-bottom:6px;}
.hline {border-bottom:2px solid #F1E6C6; margin:0 0 2px 0;}
.td {font-size:14px; padding:8px 0;}
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
    """Pinta HTML compacto (sin saltos de línea para que Markdown no lo rompa)."""
    st.markdown(re.sub(r">\s+<", "><", s.strip()), unsafe_allow_html=True)


def titulo(texto: str) -> str:
    return f'<div class="ttl">{escape(texto)}</div>'


def plata(v: float) -> str:
    return "$ " + f"{v:,.0f}".replace(",", ".")


def fecha_txt(d: date | None) -> str:
    return d.strftime("%d/%m/%Y") if d else "—"


def sumar_meses(d: date, n: int) -> date:
    m = d.month - 1 + n
    a, m = d.year + m // 12, m % 12 + 1
    return date(a, m, min(d.day, calendar.monthrange(a, m)[1]))


def chip(estado: str) -> str:
    clase = {"Pagado": "c-pagado", "Por vencer": "c-vencer", "Vencido": "c-vencido",
             "Becado (exento)": "c-exento"}.get(estado, "")
    punto = "● " if estado != "Becado (exento)" else ""
    return f'<span class="chip {clase}">{punto}{escape(estado)}</span>'


def tabla_html(cabeceras: list[str], filas: list[list[str]]) -> str:
    th = "".join(f"<th>{escape(c)}</th>" for c in cabeceras)
    tr = "".join("<tr>" + "".join(f"<td>{c}</td>" for c in f) + "</tr>" for f in filas)
    return f'<table class="tbl"><tr>{th}</tr>{tr}</table>'


def voucher_demo(texto: str) -> bytes:
    """Imagen de ejemplo para los comprobantes ficticios."""
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


# ───────────────────────────── CAPA DE DATOS (en memoria) ─────────────────────
# Para conectar Supabase, reemplaza el cuerpo de estas funciones por consultas
# a las tablas participante, membresia y pago (el resto de la app no cambia).
def iniciar_datos() -> None:
    if "participantes" in st.session_state:
        return
    hoy = date.today()
    P = lambda i, n, rol, estado, beca=None: dict(  # noqa: E731
        id=i, nombre=n, correo=f"{n.lower().replace(' ', '')}@ejemplo.cl",
        telefono="+56 9 0000 000" + str(i), rol=rol, descripcion="", estado=estado, beca=beca)
    st.session_state.participantes = [
        P(1, "Participante A", "Emprendedora", "Activa"),
        P(2, "Participante B", "Emprendedora", "Activa"),
        P(3, "Participante C", "Emprendedora", "Activa"),
        P(4, "Participante D", "Becada", "Activa", "activa"),
        P(5, "Participante E", "Mentora", "En validación de perfil"),
        P(6, "Participante F", "Becada", "Beca revocada", "revocada"),
        P(7, "Participante G", "Emprendedora", "Activa"),
        P(8, "Participante H", "Emprendedora", "Activa"),
        P(9, "Participante I", "Emprendedora", "Activa"),
    ]
    # vencimientos de ejemplo: 3 y 8 días (alerta), 10, 21, uno lejano y uno vencido
    vencimientos = {1: hoy + timedelta(days=3), 7: hoy + timedelta(days=8), 8: hoy + timedelta(days=10),
                    9: hoy + timedelta(days=21), 2: hoy + timedelta(days=150), 3: hoy - timedelta(days=60)}
    st.session_state.membresias = {pid: dict(inicio=sumar_meses(v, -6), vencimiento=v)
                                   for pid, v in vencimientos.items()}
    # pagos de ejemplo: el pago vigente de cada membresía + historial creciente para el gráfico
    pagos = [(pid, sumar_meses(v, -6)) for pid, v in vencimientos.items()]
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


def participante(pid: int) -> dict:
    return next(p for p in st.session_state.participantes if p["id"] == pid)


def estado_pago(p: dict) -> str | None:
    """R-08: Pagado · Por vencer · Vencido · Becado (exento)."""
    if p["rol"] == "Becada" and p["beca"] == "activa":
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


def email_valido(c: str) -> bool:
    return re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", c) is not None


def guardar_participante() -> None:
    """R-01, R-02, R-03: registra, valida correo (formato y duplicado) y clasifica por rol."""
    s = st.session_state
    nombre, correo = s.f_nombre.strip(), s.f_correo.strip().lower()
    if not nombre or not correo or not s.f_rol:
        s.f_msg = ("error", "Completa nombre, correo y rol para guardar.")
    elif not email_valido(correo):
        s.f_msg = ("error", "El correo no tiene un formato válido.")
    elif any(p["correo"].lower() == correo for p in s.participantes):
        s.f_msg = ("error", "Ese correo ya está registrado: no se permiten duplicados.")
    else:
        estado = {"Mentora": "En validación de perfil", "Emprendedora": "Pendiente de pago",
                  "Becada": "En evaluación de beca"}[s.f_rol]
        nuevo = dict(id=max(p["id"] for p in s.participantes) + 1, nombre=nombre, correo=correo,
                     telefono=s.f_tel.strip(), rol=s.f_rol, descripcion=s.f_desc.strip(),
                     estado=estado, beca=None)
        s.participantes.append(nuevo)
        s.f_msg = ("ok", f"{nombre} quedó registrada como {s.f_rol.lower()} · siguiente paso: {estado.lower()}.")
        s.f_nombre = s.f_correo = s.f_tel = s.f_desc = ""
        s.f_rol = None


def registrar_pago(pid: int, monto: int, metodo: str, fecha: date, meses: int, archivo) -> None:
    """R-06, R-09: registra pago con comprobante, fija inicio y calcula el vencimiento."""
    s = st.session_state
    s.pagos.append(dict(id=len(s.pagos) + 1, participante_id=pid, fecha=fecha, monto=monto,
                        metodo=metodo, comprobante_nombre=archivo.name, comprobante=archivo.getvalue()))
    s.membresias[pid] = dict(inicio=fecha, vencimiento=sumar_meses(fecha, meses))
    participante(pid)["estado"] = "Activa"


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
    # SUPUESTO: la duración real de cada plan debe validarse con las fundadoras.
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


@st.dialog("Comprobante de pago")
def dialogo_ver(pid: int) -> None:
    c = ultimo_comprobante(pid)
    if not c:
        st.info("Esta participante no tiene comprobante cargado.")
        return
    st.caption(f"{participante(pid)['nombre']} · {fecha_txt(c['fecha'])} · {plata(c['monto'])} · {c['metodo']}")
    if c["comprobante_nombre"].lower().endswith("pdf"):
        st.download_button("Descargar PDF", c["comprobante"], file_name=c["comprobante_nombre"])
    else:
        st.image(c["comprobante"])


@st.dialog("Historial de pagos", width="large")
def dialogo_historial() -> None:
    hist = sorted(st.session_state.pagos, key=lambda x: (x["fecha"], x["id"]), reverse=True)
    html(tabla_html(["Fecha", "Participante", "Monto", "Método", "Comprobante"],
                    [[fecha_txt(x["fecha"]), escape(participante(x["participante_id"])["nombre"]), plata(x["monto"]),
                      escape(x["metodo"]), "Sí" if x["comprobante"] else "—"] for x in hist]))


# ─────────────────────────────────── PÁGINAS ─────────────────────────────────
def pagina_panel() -> None:
    hoy = date.today()
    html(f'<div class="head">{titulo("Panel general")}<div class="hello"><div><b>¡Hola, {escape(NOMBRE_USUARIA)}!</b>'
         f'<span>Qué bueno verte de nuevo</span></div><img src="{b64("equipo.jpg")}"></div></div>')

    P, filas = st.session_state.participantes, filas_pagos()
    activas = sum(p["estado"] == "Activa" for p in P)
    por_vencer = [f for f in filas if f["vence"] and 0 <= (f["vence"] - hoy).days <= DIAS_ALERTA]
    becas_act = sum(p["rol"] == "Becada" and p["beca"] == "activa" for p in P)
    becas_rev = sum(p["rol"] == "Becada" and p["beca"] == "revocada" for p in P)
    ingreso_mes = sum(x["monto"] for x in st.session_state.pagos
                      if (x["fecha"].year, x["fecha"].month) == (hoy.year, hoy.month))
    metricas = [("Participantes activas", str(activas)), (f"Por vencer ({DIAS_ALERTA} días)", str(len(por_vencer))),
                ("Asistencia promedio", f"{ASISTENCIA_DEMO}%"), ("Becas activas / revocadas", f"{becas_act} / {becas_rev}"),
                ("Ingresos del mes", plata(ingreso_mes))]
    for col, (lbl, val) in zip(st.columns(5), metricas):
        with col, st.container(key=f"card_m_{lbl}"):
            html(f'<div class="m-l">{escape(lbl)}</div><div class="m-v{" long" if len(val) > 7 else ""}">{escape(val)}</div>')

    izq, der = st.columns([1.36, 1])
    with izq, st.container(key="card_ingresos"):
        # ingresos de los últimos 6 meses, calculados desde los pagos
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
        if st.button("Enviar recordatorio", key="btn_recordatorio", use_container_width=True):
            n = len(prox)
            st.toast(f"Recordatorio registrado para {n} participante(s). (Simulado: aún no se envían correos.)")


def pagina_registro() -> None:
    html(titulo("Registrar participante"))
    izq, der = st.columns([1.36, 1])
    with izq, st.container(key="card_form"):
        c1, c2 = st.columns(2)
        c1.text_input("Nombre completo", placeholder="Ej. María Pérez", key="f_nombre")
        c2.text_input("Correo electrónico", placeholder="nombre@correo.com", key="f_correo")
        c1.text_input("Teléfono", placeholder="+56 9 0000 0000", key="f_tel")
        c2.selectbox("Rol", ROLES, index=None, placeholder="Mentora / Emprendedora / Becada", key="f_rol")
        st.text_area("Descripción profesional", placeholder="Trayectoria y especialidad", height=130, key="f_desc")
        html('<div class="info">El sistema valida el correo: formato correcto y sin duplicados.</div>')
        st.button("Guardar participante", key="btn_guardar_part", on_click=guardar_participante)
        msg = st.session_state.pop("f_msg", None)
        if msg:
            (st.success if msg[0] == "ok" else st.error)(msg[1])
    with der, st.container(key="card_clasif"):
        sel = st.session_state.get("f_rol")
        pasos = [("Mentora", "Validación de perfil por la coordinadora"), ("Emprendedora", "Pago directo de membresía"),
                 ("Becada", "Evaluación de beca")]
        cajas = "".join(f'<div class="clasif {"sel" if r == sel else ""}"><span class="chip">{r}</span><div>{t}</div></div>'
                        for r, t in pasos)
        html(f'<div class="sub" style="margin-bottom:8px">Clasificación y siguiente paso</div>{cajas}'
             f'<img class="foto" src="{b64("equipo.jpg")}">')
    with st.container(key="card_lista"):
        P = st.session_state.participantes
        html(f'<div class="sub">Participantes registradas ({len(P)})</div>')
        filas = [[escape(p["nombre"]), escape(p["correo"]), f'<span class="chip">{p["rol"]}</span>', escape(p["estado"])]
                 for p in reversed(P)]
        html(tabla_html(["Nombre", "Correo", "Rol", "Estado"], filas))


def pagina_pagos() -> None:
    c1, c2 = st.columns([1.5, 1], vertical_alignment="center")
    c1.markdown(titulo("Membresías y pagos"), unsafe_allow_html=True)
    if c2.button("+ Registrar pago por transferencia", key="btn_nuevo_pago", use_container_width=True):
        dialogo_pago()

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
        html('<div class="sub">Historial de pagos</div><div class="muted" style="font-size:14px">'
             'Fecha, monto, método de pago y comprobante por participante.</div>')
        if st.button("Ver historial", key="ver_historial"):
            dialogo_historial()


def pagina_pronto(nombre: str) -> None:
    html(titulo(nombre))
    with st.container(key="card_pronto"):
        html(f'<div class="sub">Sección en construcción</div><div class="muted" style="font-size:14px">'
             f'«{escape(nombre)}» se desarrolla en la siguiente etapa del proyecto.</div>')


# ─────────────────────────────── NAVEGACIÓN Y MAIN ───────────────────────────
iniciar_datos()
st.session_state.setdefault("pagina", "Panel")


def ir(destino: str) -> None:
    st.session_state.pagina = destino


with st.sidebar:
    html(f'<img class="logo" src="{b64("logo.png")}">')
    for nombre, icono in NAV:
        activa = st.session_state.pagina == nombre
        st.button(nombre, key=f"{'navon' if activa else 'nav'}_{nombre}", icon=f":material/{icono}:",
                  on_click=ir, args=(nombre,), use_container_width=True)

if "flash" in st.session_state:
    st.toast(st.session_state.pop("flash"))

pagina = st.session_state.pagina
if pagina == "Panel":
    pagina_panel()
elif pagina == "Participantes":
    pagina_registro()
elif pagina == "Pagos":
    pagina_pagos()
else:
    pagina_pronto(pagina)
