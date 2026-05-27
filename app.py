import streamlit as st
import pandas as pd
import time
import io

# ==========================================
# 1. CONFIGURACIÓN VISUAL Y VARIABLES GLOBALES
# ==========================================
st.set_page_config(page_title="JARVIS - Termómetro de Opinión Pública", layout="wide", initial_sidebar_state="expanded")

# Inicializar variables de estado para almacenar datos reales
if "df_datos" not in st.session_state:
    st.session_state.df_datos = None
if "analisis_completado" not in st.session_state:
    st.session_state.analisis_completado = False

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
    .gemini-box {
        background-color: #f0fdf4; border: 2px solid #10a37f; border-radius: 8px; padding: 15px; margin-bottom: 15px;
        color: #064e3b; font-size: 14px;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown("<div class='jarvis-title'>🤖 JARVIS: Termómetro de Opinión Pública</div>", unsafe_allow_html=True)
st.markdown("<div class='subtitle'>Módulo Táctico: Voto Consciente y Pensamiento Crítico Juvenil (Quindío)</div><hr>", unsafe_allow_html=True)

# ==========================================
# 2. FUNCIONES DE REDUNDANCIA Y CÁLCULO
# ==========================================
def generar_plantilla_csv():
    """Genera un DataFrame de ejemplo para que el usuario sepa qué formato subir."""
    df_template = pd.DataFrame({
        "id_encuestado": [1, 2, 3, 4, 5],
        "alcance_impresiones": [1500, 200, 3400, 150, 800],
        "interacciones": [150, 20, 400, 5, 80],
        "comprension_mensaje_pct": [80, 95, 40, 100, 60],
        "verifica_fuentes": ["Si", "Si", "No", "Si", "No"],
        "detecta_fake_news": ["Si", "No", "No", "Si", "Si"]
    })
    return df_template.to_csv(index=False).encode('utf-8')

def calcular_metricas(df):
    """Calcula métricas reales con manejo de errores por si faltan columnas."""
    metricas = {
        "alcance_total": 0,
        "tasa_interaccion": 0.0,
        "promedio_comprension": 0.0,
        "nivel_fake_news": "Desconocido"
    }
    try:
        if 'alcance_impresiones' in df.columns:
            metricas["alcance_total"] = int(df['alcance_impresiones'].sum())
            
        if 'interacciones' in df.columns and 'alcance_impresiones' in df.columns and metricas["alcance_total"] > 0:
            total_interacciones = int(df['interacciones'].sum())
            metricas["tasa_interaccion"] = round((total_interacciones / metricas["alcance_total"]) * 100, 2)
            
        if 'comprension_mensaje_pct' in df.columns:
            # Convertimos a numérico ignorando errores (textos se vuelven NaN)
            df['comprension_mensaje_pct'] = pd.to_numeric(df['comprension_mensaje_pct'], errors='coerce')
            metricas["promedio_comprension"] = round(df['comprension_mensaje_pct'].mean(), 2)
            
        if 'detecta_fake_news' in df.columns:
            # Contamos cuántos dijeron "Si" (normalizando a minúsculas para evitar errores)
            detectan = df['detecta_fake_news'].astype(str).str.lower().str.strip() == 'si'
            porcentaje_detecta = detectan.mean() * 100
            if porcentaje_detecta >= 70: metricas["nivel_fake_news"] = "Alto 🟢"
            elif porcentaje_detecta >= 40: metricas["nivel_fake_news"] = "Medio 🟡"
            else: metricas["nivel_fake_news"] = "Bajo 🔴"
            
    except Exception as e:
        st.sidebar.error(f"Error calculando métricas: {e}")
        
    return metricas

# ==========================================
# 3. PANEL LATERAL (SIDEBAR) - DATOS REALES
# ==========================================
with st.sidebar:
    st.markdown("## 📊 Termómetro Global")
    
    if st.session_state.df_datos is not None and st.session_state.analisis_completado:
        st.caption("Indicadores basados en DATOS REALES")
        # Calculamos basándonos en el archivo subido
        metricas_reales = calcular_metricas(st.session_state.df_datos)
        
        st.markdown(f"<div class='metric-box'><b>Alcance Digital Medido</b><br><span style='font-size:24px; color:#3b82f6;'>{metricas_reales['alcance_total']:,}</span><br><small>Visualizaciones unicas</small></div><br>", unsafe_allow_html=True)
        
        col_a, col_b = st.columns(2)
        with col_a: 
            st.markdown(f"<div class='metric-box'><b>✅ Interacción</b><br><span style='font-size:18px; color:#10b981;'>{metricas_reales['tasa_interaccion']}%</span></div>", unsafe_allow_html=True)
        with col_b: 
            st.markdown(f"<div class='metric-box'><b>🧠 Comprensión</b><br><span style='font-size:18px; color:#8b5cf6;'>{metricas_reales['promedio_comprension']}%</span></div>", unsafe_allow_html=True)
            
        st.markdown(f"<div class='metric-box' style='margin-top:15px;'><b>🛡️ Detección Fake News:</b> <span style='font-weight:bold;'>{metricas_reales['nivel_fake_news']}</span></div>", unsafe_allow_html=True)
    else:
        st.caption("Esperando ingesta de datos...")
        st.info("Sube un archivo en la pestaña 'Instrumentos de Medición' y ejecuta el análisis para ver las métricas.")

    st.markdown("---")
    st.markdown("### ⏱️ Fase Actual")
    fase_actual = st.selectbox("Seleccionar momento de evaluación:", ["1. ANTES (Línea Base)", "2. DURANTE (Seguimiento)", "3. DESPUÉS (Impacto Final)"], index=1)

# ==========================================
# 4. NÚCLEO DE LA METODOLOGÍA (TABS)
# ==========================================
tab1, tab2, tab3, tab4 = st.tabs([
    "🎯 1. Objetivo y Diseño", 
    "📈 2. Variables", 
    "📥 3. Instrumentos e Ingesta", 
    "⚙️ 4. Procesamiento de Datos"
])

with tab1:
    st.markdown("### 🎯 Objetivo del Sistema de Evaluación")
    st.info("**Misión:** Evaluar si la estrategia logró impacto real en el pensamiento crítico juvenil (No solo medir likes).")

with tab2:
    st.markdown("### 📉 Matriz de Variables")
    st.write("Esta pestaña te recuerda lo que el sistema busca medir en los archivos CSV que subas.")
    datos_matriz = {
        "Variable": ["Alcance", "Interacción", "Comprensión", "Fake News"],
        "Columna esperada (CSV)": ["alcance_impresiones", "interacciones", "comprension_mensaje_pct", "detecta_fake_news"]
    }
    st.table(pd.DataFrame(datos_matriz))

with tab3:
    st.markdown("### 📥 Ingesta de Datos Reales")
    st.write("Sube los resultados de tus encuestas o métricas de redes sociales.")
    
    # Redundancia: Facilitar plantilla para evitar errores de formato
    csv_plantilla = generar_plantilla_csv()
    st.download_button(label="📄 Descargar Plantilla CSV de Ejemplo", data=csv_plantilla, file_name="plantilla_evaluacion.csv", mime="text/csv")
    
    archivo_subido = st.file_uploader("Cargar resultados (Solo formato CSV o Excel)", type=["csv", "xlsx"])
    
    if archivo_subido is not None:
        try:
            # Procesamiento redundante para evitar crash si el archivo está corrupto
            if archivo_subido.name.endswith('.csv'):
                df_temp = pd.read_csv(archivo_subido)
            elif archivo_subido.name.endswith('.xlsx'):
                df_temp = pd.read_excel(archivo_subido)
                
            st.session_state.df_datos = df_temp
            st.session_state.analisis_completado = False # Reiniciamos el estado
            st.success(f"✅ Archivo '{archivo_subido.name}' cargado correctamente en la memoria temporal. ({len(df_temp)} registros encontrados).")
            st.dataframe(df_temp.head(5)) # Mostrar una vista previa
            
        except Exception as e:
            st.error(f"❌ Error crítico leyendo el archivo. Asegúrate de que no esté dañado. Detalles del error: {e}")

with tab4:
    st.markdown("### ⚙️ Centro de Procesamiento de Datos Reales")
    
    if st.session_state.df_datos is None:
        st.warning("⚠️ No hay datos en el sistema. Ve a la pestaña '3. Instrumentos e Ingesta' y sube un archivo.")
    else:
        st.write(f"📊 **Base de datos lista:** {len(st.session_state.df_datos)} registros en espera de procesamiento.")
        
        if st.button("🚀 INICIAR ANÁLISIS DE IMPACTO", type="primary"):
            progress_bar = st.progress(0)
            log_container = st.empty()
            logs = ["Iniciando motor de procesamiento JARVIS..."]
            
            def actualizar_log(mensaje):
                logs.append(mensaje)
                log_text = "<br>".join([f"> {l}" for l in logs[-8:]])
                log_container.markdown(f"<div class='status-log'>{log_text}</div>", unsafe_allow_html=True)
                
            try:
                # Simulación de tiempo para efecto visual, pero aplicando a datos reales
                actualizar_log("Verificando integridad estructural del dataframe...")
                time.sleep(1)
                columnas = list(st.session_state.df_datos.columns)
                actualizar_log(f"Columnas detectadas: {', '.join(columnas)}")
                progress_bar.progress(30)
                
                time.sleep(1)
                actualizar_log("Calculando métricas cuantitativas (Alcance e Interacción)...")
                progress_bar.progress(60)
                
                time.sleep(1)
                actualizar_log("Procesando variables cualitativas (Pensamiento Crítico y Fake News)...")
                
                # Ejecutamos la función de cálculo real
                metricas_finales = calcular_metricas(st.session_state.df_datos)
                progress_bar.progress(100)
                
                st.session_state.analisis_completado = True
                
                actualizar_log("✅ **ANÁLISIS COMPLETADO. Actualizando Termómetro Global (Panel Izquierdo).**")
                
                # Mostrar resumen de hallazgos
                st.success("Cálculos completados sin errores.")
                st.markdown("#### 📑 Resumen Rápido del Impacto")
                st.write(f"- El alcance total procesado fue de **{metricas_finales['alcance_total']}**.")
                st.write(f"- La comprensión promedio detectada en la población fue del **{metricas_finales['promedio_comprension']}%**.")
                st.info("Revisa el panel lateral para ver el tablero visual actualizado.")
                
            except Exception as e:
                actualizar_log(f"❌ ERROR DURANTE EL PROCESAMIENTO: {e}")
                st.error("Hubo un fallo analizando los datos. Verifica que el archivo cumpla con los nombres de columna de la plantilla.")