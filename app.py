import streamlit as st
import pandas as pd
import time
import tempfile
import os
from fpdf import FPDF

# ==========================================
# 1. CONFIGURACIÓN VISUAL Y VARIABLES GLOBALES
# ==========================================
st.set_page_config(page_title="JARVIS - Medidor de Eficiencias", layout="wide", initial_sidebar_state="expanded")

# Inicializar variables de estado
if "df_datos" not in st.session_state:
    st.session_state.df_datos = None
if "df_rrss" not in st.session_state:
    st.session_state.df_rrss = None
if "analisis_completado" not in st.session_state:
    st.session_state.analisis_completado = False
if "mostrar_guia" not in st.session_state:
    st.session_state.mostrar_guia = False

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
        padding: 15px; border-radius: 5px; height: 250px; overflow-y: auto;
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
# Si el usuario activa la guía, se bloquea la interfaz principal y se muestra esto como una ventana aparte.
if st.session_state.mostrar_guia:
    st.markdown("<div class='guide-container'>", unsafe_allow_html=True)
    st.markdown("<h1 style='color: #0f172a;'>📖 ¿Qué hacemos? - Manual del Sistema JARVIS</h1>", unsafe_allow_html=True)
    st.write("Bienvenido al centro de conocimiento del **Medidor de Eficiencias**. Aquí explicamos cómo operamos.")
    
    st.markdown("### 🎯 Objetivos")
    st.info("El objetivo principal del sistema es medir la efectividad real de las estrategias de comunicación pública, trascendiendo las métricas de vanidad (likes) para entender si realmente hubo una apropiación del mensaje, fomento del pensamiento crítico y fortalecimiento democrático.")
    
    st.markdown("### 🧩 Metodología")
    st.write("Utilizamos un enfoque **Mixto**:")
    st.markdown("- **Cuantitativo:** Análisis algorítmico de visualizaciones, alcance, interacciones y tasas de conversión mediante ingesta de bases de datos.\n- **Cualitativo:** Medición de comprensión de mensajes, capacidad de detectar desinformación (Fake News) y cambios en la percepción pública a través de encuestas estructuradas.")
    
    st.markdown("### 📉 Variables y Categorías de Medición")
    colA, colB = st.columns(2)
    with colA:
        st.write("**1. Impacto Táctico (RRSS):** Alcance, visualizaciones, comentarios, compartidos.")
        st.write("**2. Comprensión:** Porcentaje de acierto en el mensaje central de la campaña.")
    with colB:
        st.write("**3. Pensamiento Crítico:** Tasa de usuarios que verifican las fuentes.")
        st.write("**4. Defensa Democrática:** Capacidad del público para detectar Fake News.")
        
    st.markdown("### ⚙️ Análisis de Resultados")
    st.write("El motor JARVIS cruza los datos de alcance digital con los resultados cualitativos de las encuestas para determinar si una campaña fue simplemente 'viral' o si fue verdaderamente **'eficiente y transformadora'**.")
    
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("⬅️ Volver al Medidor de Eficiencias", type="primary"):
        st.session_state.mostrar_guia = False
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)
    st.stop() # Detiene la ejecución del resto del código para simular la ventana aparte

# ==========================================
# 3. FUNCIONES DE REDUNDANCIA, CÁLCULO Y PDF
# ==========================================
def generar_plantilla_csv():
    df_template = pd.DataFrame({
        "id_encuestado": [1, 2, 3, 4, 5],
        "alcance_impresiones": [1500, 200, 3400, 150, 800],
        "interacciones": [150, 20, 400, 5, 80],
        "comprension_mensaje_pct": [80, 95, 40, 100, 60],
        "verifica_fuentes": ["Si", "Si", "No", "Si", "No"],
        "detecta_fake_news": ["Si", "No", "No", "Si", "Si"]
    })
    return df_template.to_csv(index=False).encode('utf-8')

def generar_plantilla_rrss():
    df_template = pd.DataFrame({
        "fecha": ["2026-05-01", "2026-05-02", "2026-05-03", "2026-05-04"],
        "plataforma": ["Instagram", "Facebook", "TikTok", "Instagram"],
        "post_id": ["Post_001", "Post_002", "Post_003", "Post_004"],
        "alcance": [1500, 2000, 8500, 3200],
        "likes": [150, 80, 1200, 400],
        "comentarios": [20, 5, 150, 45],
        "compartidos": [10, 2, 400, 80]
    })
    return df_template.to_csv(index=False).encode('utf-8')

def calcular_metricas(df):
    metricas = {"alcance_total": 0, "tasa_interaccion": 0.0, "promedio_comprension": 0.0, "nivel_fake_news": "Desconocido"}
    try:
        if 'alcance_impresiones' in df.columns: metricas["alcance_total"] = int(df['alcance_impresiones'].sum())
        if 'interacciones' in df.columns and 'alcance_impresiones' in df.columns and metricas["alcance_total"] > 0:
            metricas["tasa_interaccion"] = round((int(df['interacciones'].sum()) / metricas["alcance_total"]) * 100, 2)
        if 'comprension_mensaje_pct' in df.columns:
            df['comprension_mensaje_pct'] = pd.to_numeric(df['comprension_mensaje_pct'], errors='coerce')
            metricas["promedio_comprension"] = round(df['comprension_mensaje_pct'].mean(), 2)
        if 'detecta_fake_news' in df.columns:
            porcentaje = (df['detecta_fake_news'].astype(str).str.lower().str.strip() == 'si').mean() * 100
            if porcentaje >= 70: metricas["nivel_fake_news"] = "Alto 🟢"
            elif porcentaje >= 40: metricas["nivel_fake_news"] = "Medio 🟡"
            else: metricas["nivel_fake_news"] = "Bajo 🔴"
    except Exception as e: st.sidebar.error(f"Error: {e}")
    return metricas

def generar_pdf_rrss(df):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, "JARVIS - REPORTE DE EFICIENCIA EN REDES SOCIALES", ln=True, align='C')
    pdf.ln(10)
    
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, "1. Resumen Global de Impacto", ln=True)
    pdf.set_font("Arial", '', 12)
    
    # Calcular totales de forma segura
    alcance_tot = int(df['alcance'].sum()) if 'alcance' in df.columns else 0
    likes_tot = int(df['likes'].sum()) if 'likes' in df.columns else 0
    coment_tot = int(df['comentarios'].sum()) if 'comentarios' in df.columns else 0
    comp_tot = int(df['compartidos'].sum()) if 'compartidos' in df.columns else 0
    
    pdf.cell(0, 8, f"- Alcance Total (Visualizaciones): {alcance_tot:,}", ln=True)
    pdf.cell(0, 8, f"- Total Likes: {likes_tot:,}", ln=True)
    pdf.cell(0, 8, f"- Total Comentarios: {coment_tot:,}", ln=True)
    pdf.cell(0, 8, f"- Total Compartidos: {comp_tot:,}", ln=True)
    
    pdf.ln(10)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, "2. Rendimiento por Plataforma", ln=True)
    pdf.set_font("Arial", '', 12)
    
    if 'plataforma' in df.columns and 'alcance' in df.columns:
        resumen_plat = df.groupby('plataforma')['alcance'].sum().reset_index()
        for _, row in resumen_plat.iterrows():
            pdf.cell(0, 8, f"- {row['plataforma']}: {int(row['alcance']):,} de alcance", ln=True)
    else:
        pdf.cell(0, 8, "No se detecto la columna 'plataforma' para agrupar.", ln=True)
        
    pdf.ln(20)
    pdf.set_font("Arial", 'I', 10)
    pdf.cell(0, 10, "Generado automaticamente por el Motor JARVIS - Medidor de Eficiencias.", ln=True)
    
    # Usar archivo temporal para garantizar que los bytes se codifiquen bien
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        pdf.output(tmp.name)
        with open(tmp.name, "rb") as f:
            pdf_bytes = f.read()
    os.remove(tmp.name)
    return pdf_bytes

# ==========================================
# 4. INTERFAZ PRINCIPAL
# ==========================================
st.markdown("<div class='jarvis-title'>🤖 JARVIS: Medidor de Eficiencias</div>", unsafe_allow_html=True)
st.markdown("<div class='subtitle'>Módulo Táctico: Voto Consciente y Pensamiento Crítico Juvenil</div><hr>", unsafe_allow_html=True)

with st.sidebar:
    # Botón que activa la ventana aparte
    if st.button("ℹ️ ¿Qué hacemos? (Ver Guía)", type="primary", use_container_width=True):
        st.session_state.mostrar_guia = True
        st.rerun()
        
    st.markdown("## 📊 Termómetro General")
    if st.session_state.df_datos is not None and st.session_state.analisis_completado:
        metricas_reales = calcular_metricas(st.session_state.df_datos)
        st.markdown(f"<div class='metric-box'><b>Alcance Digital Medido</b><br><span style='font-size:24px; color:#3b82f6;'>{metricas_reales['alcance_total']:,}</span></div><br>", unsafe_allow_html=True)
        col_a, col_b = st.columns(2)
        with col_a: st.markdown(f"<div class='metric-box'><b>✅ Interacción</b><br><span style='font-size:16px; color:#10b981;'>{metricas_reales['tasa_interaccion']}%</span></div>", unsafe_allow_html=True)
        with col_b: st.markdown(f"<div class='metric-box'><b>🧠 Comprensión</b><br><span style='font-size:16px; color:#8b5cf6;'>{metricas_reales['promedio_comprension']}%</span></div>", unsafe_allow_html=True)
        st.markdown(f"<div class='metric-box' style='margin-top:15px;'><b>🛡️ Detectan Fake News:</b> <span style='font-weight:bold;'>{metricas_reales['nivel_fake_news']}</span></div>", unsafe_allow_html=True)
    else:
        st.info("Sube datos en la pestaña 3 para alimentar el termómetro.")

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🎯 1. Objetivo", 
    "📈 2. Variables", 
    "📥 3. Ingesta de Encuestas", 
    "⚙️ 4. Procesamiento",
    "📱 5. Redes Sociales (Nuevo)"
])

with tab1: st.info("**Misión:** Evaluar si la estrategia logró impacto real en el pensamiento crítico juvenil.")
with tab2: st.table(pd.DataFrame({"Variable": ["Alcance", "Interacción", "Comprensión", "Fake News"], "Columna esperada": ["alcance_impresiones", "interacciones", "comprension_mensaje_pct", "detecta_fake_news"]}))

with tab3:
    st.markdown("### 📥 Ingesta de Datos: Encuestas de Opinión")
    st.download_button("📄 Plantilla CSV (Encuestas)", data=generar_plantilla_csv(), file_name="plantilla_encuestas.csv", mime="text/csv")
    archivo_encuesta = st.file_uploader("Cargar resultados de encuestas (CSV/Excel)", type=["csv", "xlsx"], key="encuestas")
    if archivo_encuesta is not None:
        try:
            st.session_state.df_datos = pd.read_csv(archivo_encuesta) if archivo_encuesta.name.endswith('.csv') else pd.read_excel(archivo_encuesta)
            st.session_state.analisis_completado = False
            st.success(f"Archivo cargado. ({len(st.session_state.df_datos)} registros).")
        except Exception as e: st.error(f"Error leyendo archivo: {e}")

with tab4:
    st.markdown("### ⚙️ Procesamiento de Datos de Opinión")
    if st.session_state.df_datos is None: st.warning("⚠️ Sube un archivo en la Pestaña 3.")
    else:
        if st.button("🚀 INICIAR ANÁLISIS DE EFICIENCIA", type="primary"):
            st.session_state.analisis_completado = True
            st.success("✅ **Análisis completado. El Termómetro General (izquierda) ha sido actualizado.**")

# --- NUEVA PESTAÑA 5: REDES SOCIALES ---
with tab5:
    st.markdown("### 📱 Central de Monitoreo: Redes Sociales")
    st.write("Sube aquí los reportes extraídos de Meta Business, Instagram Insights o TikTok Analytics.")
    
    st.download_button("📲 Descargar Plantilla CSV (Redes Sociales)", data=generar_plantilla_rrss(), file_name="plantilla_rrss.csv", mime="text/csv")
    
    archivo_rrss = st.file_uploader("Cargar reporte de Redes Sociales (CSV/Excel)", type=["csv", "xlsx"], key="rrss")
    
    if archivo_rrss is not None:
        try:
            df_rs = pd.read_csv(archivo_rrss) if archivo_rrss.name.endswith('.csv') else pd.read_excel(archivo_rrss)
            st.session_state.df_rrss = df_rs
            st.success(f"✅ Datos de RRSS cargados. ({len(df_rs)} publicaciones encontradas).")
        except Exception as e:
            st.error(f"Error procesando redes sociales: {e}")
            
    if st.session_state.df_rrss is not None:
        st.markdown("---")
        st.markdown("#### 📊 Gráficas de Rendimiento")
        
        df_rs = st.session_state.df_rrss
        colA, colB = st.columns(2)
        
        with colA:
            st.write("**Alcance por Plataforma**")
            if 'plataforma' in df_rs.columns and 'alcance' in df_rs.columns:
                alcance_plat = df_rs.groupby('plataforma')['alcance'].sum()
                st.bar_chart(alcance_plat)
            else: st.warning("Faltan columnas 'plataforma' o 'alcance'.")
            
        with colB:
            st.write("**Evolución de Interacciones (Likes)**")
            if 'fecha' in df_rs.columns and 'likes' in df_rs.columns:
                # Agrupar por fecha por si hay varios posts el mismo día
                likes_fecha = df_rs.groupby('fecha')['likes'].sum()
                st.line_chart(likes_fecha)
            else: st.warning("Faltan columnas 'fecha' o 'likes'.")
            
        st.markdown("---")
        st.markdown("#### 📑 Generación de Informe Ejecutivo")
        st.info("Presiona el botón para empaquetar estos resultados en un documento formal PDF.")
        
        try:
            pdf_bytes = generar_pdf_rrss(df_rs)
            st.download_button(
                label="⬇️ Descargar Reporte PDF de Redes Sociales",
                data=pdf_bytes,
                file_name="Reporte_Eficiencias_RRSS_JARVIS.pdf",
                mime="application/pdf",
                type="primary"
            )
        except Exception as e:
            st.error(f"Error generando el PDF: Asegúrate de que las columnas coincidan con la plantilla. Detalle: {e}")
