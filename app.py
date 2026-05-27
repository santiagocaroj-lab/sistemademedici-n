import streamlit as st
import pandas as pd
import time
import tempfile
import os
from fpdf import FPDF
import PyPDF2
import docx

# ==========================================
# 1. CONFIGURACIÓN VISUAL Y VARIABLES GLOBALES
# ==========================================
st.set_page_config(page_title="JARVIS - Medidor de Eficiencias", layout="wide", initial_sidebar_state="expanded")

# Inicializar variables de estado
if "df_datos" not in st.session_state: st.session_state.df_datos = None
if "df_rrss" not in st.session_state: st.session_state.df_rrss = None
if "doc_procesado" not in st.session_state: st.session_state.doc_procesado = None
if "analisis_completado" not in st.session_state: st.session_state.analisis_completado = False
if "mostrar_guia" not in st.session_state: st.session_state.mostrar_guia = False

st.markdown("""
    <style>
    .jarvis-title {
        font-size: 36px; font-weight: 900; color: #0f172a;
        border-left: 10px solid #3b82f6; padding-left: 15px;
        font-family: 'Courier New', Courier, monospace;
    }
    .subtitle {
        font-size: 20px; font-weight: bold; color: #475569;
        margin-bottom: 20px;
    }
    .metric-box {
        background-color: #f8fafc; border: 1px solid #cbd5e1; border-radius: 8px; padding: 15px; text-align: center;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.05);
    }
    .status-log {
        background-color: #1e293b; color: #10b981; font-family: 'Courier New';
        padding: 15px; border-radius: 5px; height: 200px; overflow-y: auto;
    }
    .guide-container {
        background-color: #ffffff; padding: 30px; border-radius: 10px;
        box-shadow: 0px 4px 15px rgba(0,0,0,0.1); border-top: 5px solid #3b82f6;
    }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. VENTANA APARTE: "¿QUÉ HACEMOS?"
# ==========================================
if st.session_state.mostrar_guia:
    st.markdown("<div class='guide-container'>", unsafe_allow_html=True)
    st.markdown("<h1 style='color: #0f172a;'>📖 ¿Qué hacemos? - Manual del Sistema JARVIS</h1>", unsafe_allow_html=True)
    st.write("Bienvenido al centro de conocimiento del **Medidor de Eficiencias**. Aquí explicamos cómo operamos.")
    st.markdown("### 🎯 Objetivos")
    st.info("Medir la efectividad real de las estrategias de comunicación pública, trascendiendo las métricas de vanidad (likes) para entender si realmente hubo una apropiación del mensaje, fomento del pensamiento crítico y fortalecimiento democrático.")
    st.markdown("### 🧩 Metodología")
    st.write("Enfoque **Mixto**:")
    st.markdown("- **Cuantitativo:** Análisis algorítmico de visualizaciones, alcance e interacciones (Redes Sociales y Encuestas).\n- **Cualitativo:** Lectura asistida de documentos (PDF/Word) para rastrear percepciones ciudadanas y comprensión de mensajes.")
    st.markdown("### 📉 Variables y Categorías de Medición")
    colA, colB = st.columns(2)
    with colA:
        st.write("**1. Impacto Táctico (RRSS):** Alcance, visualizaciones, comentarios.")
        st.write("**2. Comprensión:** Porcentaje de acierto en encuestas.")
    with colB:
        st.write("**3. Pensamiento Crítico:** Usuarios que verifican fuentes (Lectura de documentos).")
        st.write("**4. Defensa Democrática:** Capacidad de detectar Fake News.")
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("⬅️ Volver al Medidor de Eficiencias", type="primary"):
        st.session_state.mostrar_guia = False
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# ==========================================
# 3. FUNCIONES DE LECTURA Y PROCESAMIENTO
# ==========================================
def generar_plantilla_csv():
    return pd.DataFrame({"id_encuestado": [1, 2], "alcance_impresiones": [1500, 200], "interacciones": [150, 20], "comprension_mensaje_pct": [80, 95], "verifica_fuentes": ["Si", "No"], "detecta_fake_news": ["Si", "No"]}).to_csv(index=False).encode('utf-8')

def generar_plantilla_rrss():
    return pd.DataFrame({"fecha": ["2026-05-01", "2026-05-02"], "plataforma": ["Instagram", "Facebook"], "alcance": [1500, 2000], "likes": [150, 80], "comentarios": [20, 5]}).to_csv(index=False).encode('utf-8')

def extraer_texto_pdf(archivo):
    texto = ""
    pdf_reader = PyPDF2.PdfReader(archivo)
    for page in pdf_reader.pages:
        texto += page.extract_text() + "\n"
    return texto

def extraer_texto_docx(archivo):
    doc = docx.Document(archivo)
    return "\n".join([para.text for para in doc.paragraphs])

def calcular_metricas(df):
    metricas = {"alcance_total": 0, "tasa_interaccion": 0.0, "promedio_comprension": 0.0, "nivel_fake_news": "Desconocido"}
    try:
        if 'alcance_impresiones' in df.columns: metricas["alcance_total"] = int(df['alcance_impresiones'].sum())
        if 'interacciones' in df.columns and metricas["alcance_total"] > 0:
            metricas["tasa_interaccion"] = round((int(df['interacciones'].sum()) / metricas["alcance_total"]) * 100, 2)
        if 'comprension_mensaje_pct' in df.columns:
            df['comprension_mensaje_pct'] = pd.to_numeric(df['comprension_mensaje_pct'], errors='coerce')
            metricas["promedio_comprension"] = round(df['comprension_mensaje_pct'].mean(), 2)
        if 'detecta_fake_news' in df.columns:
            pct = (df['detecta_fake_news'].astype(str).str.lower().str.strip() == 'si').mean() * 100
            metricas["nivel_fake_news"] = "Alto 🟢" if pct >= 70 else ("Medio 🟡" if pct >= 40 else "Bajo 🔴")
    except: pass
    return metricas

def generar_pdf_rrss(df):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, "JARVIS - REPORTE DE REDES SOCIALES", ln=True, align='C')
    pdf.ln(10)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, "1. Resumen Global", ln=True)
    pdf.set_font("Arial", '', 12)
    
    alcance_tot = int(df['alcance'].sum()) if 'alcance' in df.columns else 0
    likes_tot = int(df['likes'].sum()) if 'likes' in df.columns else 0
    
    pdf.cell(0, 8, f"- Alcance Total: {alcance_tot:,}", ln=True)
    pdf.cell(0, 8, f"- Total Likes: {likes_tot:,}", ln=True)
    
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        pdf.output(tmp.name)
        with open(tmp.name, "rb") as f: bytes_pdf = f.read()
    os.remove(tmp.name)
    return bytes_pdf

# ==========================================
# 4. INTERFAZ PRINCIPAL
# ==========================================
st.markdown("<div class='jarvis-title'>🤖 JARVIS: Medidor de Eficiencias</div>", unsafe_allow_html=True)
st.markdown("<div class='subtitle'>Módulo Táctico: Voto Consciente y Pensamiento Crítico Juvenil</div><hr>", unsafe_allow_html=True)

with st.sidebar:
    if st.button("ℹ️ ¿Qué hacemos? (Ver Guía)", type="primary", use_container_width=True):
        st.session_state.mostrar_guia = True
        st.rerun()
        
    st.markdown("## 📊 Termómetro General")
    if st.session_state.df_datos is not None and st.session_state.analisis_completado:
        metricas_reales = calcular_metricas(st.session_state.df_datos)
        st.markdown(f"<div class='metric-box'><b>Alcance Digital</b><br><span style='font-size:24px; color:#3b82f6;'>{metricas_reales['alcance_total']:,}</span></div><br>", unsafe_allow_html=True)
        col_a, col_b = st.columns(2)
        with col_a: st.markdown(f"<div class='metric-box'><b>✅ Interacción</b><br><span style='font-size:16px; color:#10b981;'>{metricas_reales['tasa_interaccion']}%</span></div>", unsafe_allow_html=True)
        with col_b: st.markdown(f"<div class='metric-box'><b>🧠 Comprensión</b><br><span style='font-size:16px; color:#8b5cf6;'>{metricas_reales['promedio_comprension']}%</span></div>", unsafe_allow_html=True)
        st.markdown(f"<div class='metric-box' style='margin-top:15px;'><b>🛡️ Fake News:</b> <span style='font-weight:bold;'>{metricas_reales['nivel_fake_news']}</span></div>", unsafe_allow_html=True)
    else:
        st.info("Sube datos en la pestaña 3 para alimentar el termómetro.")

tab1, tab2, tab3, tab4 = st.tabs(["🎯 1. Objetivo", "📈 2. Variables", "📥 3. Incorporación de información", "⚙️ 4. Procesamiento"])

with tab1: st.info("**Misión:** Evaluar si la estrategia logró impacto real en el pensamiento crítico juvenil.")
with tab2: st.table(pd.DataFrame({"Variable": ["Alcance", "Interacción", "Comprensión", "Fake News"], "Columna esperada": ["alcance_impresiones", "interacciones", "comprension_mensaje_pct", "detecta_fake_news"]}))

# --- PESTAÑA 3: INCORPORACIÓN UNIFICADA DE INFORMACIÓN ---
with tab3:
    st.markdown("### 📥 Centro de Ingesta de Información")
    st.write("Sube aquí cualquier tipo de información: encuestas, métricas de redes sociales o documentos no estructurados (Word/PDF).")
    
    # Sub-pestañas internas para organizar mejor sin abrumar al usuario
    subtab_encuestas, subtab_rrss, subtab_docs = st.tabs(["📊 Encuestas (Excel/CSV)", "📱 Redes Sociales (Excel/CSV)", "📄 Documentos (PDF/Word)"])
    
    with subtab_encuestas:
        st.markdown("#### 1. Resultados de Encuestas")
        st.download_button("📄 Bajar Plantilla", data=generar_plantilla_csv(), file_name="plantilla_encuestas.csv", mime="text/csv")
        archivo_encuesta = st.file_uploader("Sube el Excel o CSV de encuestas:", type=["csv", "xlsx"], key="encuestas")
        if archivo_encuesta is not None:
            try:
                st.session_state.df_datos = pd.read_csv(archivo_encuesta) if archivo_encuesta.name.endswith('.csv') else pd.read_excel(archivo_encuesta)
                st.success(f"¡Encuestas cargadas con éxito! ({len(st.session_state.df_datos)} registros).")
            except Exception as e: st.error(f"Error: {e}")

    with subtab_rrss:
        st.markdown("#### 2. Reportes de Redes Sociales")
        st.download_button("📲 Bajar Plantilla", data=generar_plantilla_rrss(), file_name="plantilla_rrss.csv", mime="text/csv")
        archivo_rrss = st.file_uploader("Sube el Excel o CSV de Meta/Instagram/TikTok:", type=["csv", "xlsx"], key="rrss")
        if archivo_rrss is not None:
            try:
                st.session_state.df_rrss = pd.read_csv(archivo_rrss) if archivo_rrss.name.endswith('.csv') else pd.read_excel(archivo_rrss)
                st.success(f"¡Redes Sociales cargadas! ({len(st.session_state.df_rrss)} publicaciones).")
            except Exception as e: st.error(f"Error: {e}")

    with subtab_docs:
        st.markdown("#### 3. Lectura Inteligente de Documentos")
        st.info("Sube informes, notas, o entrevistas en formato PDF o Word. JARVIS extraerá el texto y lo analizará con base en lo que tú le pidas.")
        archivo_doc = st.file_uploader("Cargar documento (PDF o Word):", type=["pdf", "docx"], key="docs")
        
        # Parámetros tipo "Garzón"
        st.markdown("##### 🧠 Parámetros de Apoyo")
        parametros = st.text_area("¿Qué debo buscar en este documento? (Ej: 'Encuentra si los jóvenes mencionan la palabra corrupción', 'Resume las críticas a la política'):", placeholder="Escribe tus instrucciones aquí...")
        
        if archivo_doc and st.button("Leer e Interpretar Documento", type="primary"):
            try:
                with st.spinner("Extrayendo texto del documento..."):
                    if archivo_doc.name.endswith('.pdf'):
                        texto_extraido = extraer_texto_pdf(archivo_doc)
                    else:
                        texto_extraido = extraer_texto_docx(archivo_doc)
                    
                    st.session_state.doc_procesado = {"nombre": archivo_doc.name, "texto": texto_extraido, "parametros": parametros}
                    
                st.success("✅ Documento leído correctamente. Ve a la pestaña '4. Procesamiento' para ver el análisis.")
            except Exception as e:
                st.error(f"Ocurrió un error al leer el archivo. Intenta con otro documento válido. Detalle: {e}")

# --- PESTAÑA 4: PROCESAMIENTO Y ANÁLISIS ---
with tab4:
    st.markdown("### ⚙️ Centro de Análisis y Procesamiento")
    
    # Análisis de Datos Estructurados (Encuestas)
    if st.session_state.df_datos is not None:
        if st.button("🚀 INICIAR ANÁLISIS DE ENCUESTAS", type="primary"):
            st.session_state.analisis_completado = True
            st.success("✅ **Análisis de Encuestas completado. Termómetro General actualizado (Ver izquierda).**")
    
    # Análisis de Redes Sociales
    if st.session_state.df_rrss is not None:
        st.markdown("---")
        st.markdown("#### 📊 Rendimiento en Redes Sociales")
        df_rs = st.session_state.df_rrss
        colA, colB = st.columns(2)
        with colA:
            if 'plataforma' in df_rs.columns and 'alcance' in df_rs.columns:
                st.bar_chart(df_rs.groupby('plataforma')['alcance'].sum())
        with colB:
            if 'fecha' in df_rs.columns and 'likes' in df_rs.columns:
                st.line_chart(df_rs.groupby('fecha')['likes'].sum())
                
        pdf_bytes = generar_pdf_rrss(df_rs)
        st.download_button("⬇️ Descargar Reporte PDF de Redes", data=pdf_bytes, file_name="Reporte_RRSS.pdf", mime="application/pdf")

    # Análisis de Documentos con Parámetros (Estilo Garzón)
    if st.session_state.doc_procesado is not None:
        st.markdown("---")
        st.markdown(f"#### 🧠 Análisis Documental: {st.session_state.doc_procesado['nombre']}")
        
        parametros_usados = st.session_state.doc_procesado['parametros']
        if not parametros_usados: parametros_usados = "Ninguno especificado. Se realizará un escaneo general."
        
        st.write(f"**Parámetros de búsqueda indicados:** _{parametros_usados}_")
        
        # Simulación de respuesta IA basada en el texto (Para que funcione 100% sin API Keys por ahora)
        texto = st.session_state.doc_procesado['texto']
        palabras_clave = len(texto.split())
        
        st.markdown("<div class='status-log'>", unsafe_allow_html=True)
        st.markdown(f"> Iniciando Copiloto de Lectura...<br>", unsafe_allow_html=True)
        time.sleep(1)
        st.markdown(f"> Extrayendo datos... Se detectaron {palabras_clave} palabras en el documento.<br>", unsafe_allow_html=True)
        time.sleep(1)
        st.markdown(f"> Cruzando texto con los parámetros: '{parametros_usados}'...<br>", unsafe_allow_html=True)
        time.sleep(1.5)
        st.markdown(f"> <b>RESULTADO DEL ANÁLISIS MOCKUP:</b><br>", unsafe_allow_html=True)
        st.markdown(f"> <i>El documento aborda temas relacionados con la comunicación y participación. Según sus parámetros, se sugiere prestar especial atención a los párrafos centrales donde se nota una leve inclinación hacia la falta de contraste de información (Fake News).</i><br>", unsafe_allow_html=True)
        st.markdown(f"<br>> ✅ Lectura Finalizada.", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    if (st.session_state.df_datos is None) and (st.session_state.df_rrss is None) and (st.session_state.doc_procesado is None):
        st.warning("⚠️ No hay información en el sistema. Ve a la Pestaña 3 y sube algunos archivos.")
