import streamlit as st
import pandas as pd
import hashlib
import json
import os
import plotly.express as px

# --- CONFIGURACIÓN DE MEMORIA FÍSICA ---
# Cambiamos el nombre para empezar con una bóveda 100% limpia y compatible
ARCHIVO_MEMORIA = "memoria_sandbox_v3.json" 
SAL_SECRETA = "Tr#9q!Lp$2*mZ&8vX@1y_Sandbox_Riesgo_2026_UltraSecreto"

def cargar_memoria():
    if os.path.exists(ARCHIVO_MEMORIA):
        with open(ARCHIVO_MEMORIA, "r") as f:
            return json.load(f)
    return {}

def guardar_memoria(datos):
    with open(ARCHIVO_MEMORIA, "w") as f:
        json.dump(datos, f)

# 1. CONFIGURACIÓN DE LA PÁGINA
st.set_page_config(page_title="Motor de Riesgo Anti-Fraude", page_icon="🛡️", layout="wide")

# --- ESTILOS CSS PERSONALIZADOS ---
st.markdown("""
    <style>
        .main-header { font-size: 2.5rem; color: #1E3A8A; font-weight: 700; margin-bottom: 0px;}
        .sub-header { font-size: 1.2rem; color: #64748B; margin-bottom: 2rem;}
        .stTabs [data-baseweb="tab-list"] { gap: 24px; }
        .stTabs [data-baseweb="tab"] { font-size: 1.1rem; font-weight: 600; }
    </style>
""", unsafe_allow_html=True)

# 2. CARGA DE BASE DE DATOS
if 'database' not in st.session_state:
    st.session_state['database'] = cargar_memoria()

def tokenizar_dato(valor):
    if pd.isna(valor) or valor == "": 
        return ""
    dato_salado = str(valor).strip().lower() + SAL_SECRETA
    return hashlib.sha256(dato_salado.encode()).hexdigest()

# 3. BARRA LATERAL (SIDEBAR) CORPORATIVA
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2592/2592317.png", width=80)
    st.title("Estado del Sistema")
    st.divider()
    total_en_memoria = len(st.session_state['database'])
    st.metric(label="Registros Tokenizados en Bóveda", value=total_en_memoria)
    st.caption("🔒 Seguridad SHA-256 + Salting activo.")
    st.divider()
    st.info("💡 **Tip para la demo:** Cambia entre las pestañas a la derecha para operar el Sandbox.")

# 4. ENCABEZADO PRINCIPAL
st.markdown('<p class="main-header">🛡️ Motor de Riesgo y Privacidad (Sandbox)</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Plataforma académica para tokenización de datos confidenciales y prevención de fraude.</p>', unsafe_allow_html=True)

# 5. SISTEMA DE PESTAÑAS (TABS)
tab_carga, tab_consulta, tab_dashboard = st.tabs([
    "📤 Carga y Tokenización de Datos", 
    "🔍 Motor de Consultas (Scoring)", 
    "📊 Dashboard Estadístico"
])

# --- PESTAÑA 1: CARGA DE DATOS ---
with tab_carga:
    col_izq, col_der = st.columns([1, 1])
    
    with col_izq:
        st.subheader("1. Configurar Parámetros de Riesgo")
        st.markdown("Clasifica los datos antes de inyectarlos al sistema.")
        opciones_riesgo = {
            "OK (Buen Dato)": {"status": "OK", "score": 0, "color": "🟢"},
            "Posible Fraude (No confirmado)": {"status": "Posible Fraude", "score": 50, "color": "🟡"},
            "Fraude: Cuenta Mula": {"status": "Cuenta Mula", "score": 75, "color": "🟠"},
            "Fraude: Onboarding": {"status": "Fraude Onboarding", "score": 75, "color": "🟠"},
            "Fraude: Transaccional": {"status": "Fraude Transaccional", "score": 99, "color": "🔴"}
        }
        categoria_seleccionada = st.selectbox("Categoría de riesgo para este lote:", list(opciones_riesgo.keys()))
    
    with col_der:
        st.subheader("2. Subir Base de Datos")
        archivo_subido = st.file_uploader("Sube tu archivo .xlsx (email, telefono, dni)", type=["xlsx"])
    
    if archivo_subido is not None:
        if st.button("Procesar, Tokenizar y Guardar 🚀", use_container_width=True):
            with st.spinner('Procesando datos y aplicando criptografía...'):
                df = pd.read_excel(archivo_subido)
                columnas_encontradas = [col for col in ["email", "telefono", "dni"] if col in df.columns]
                
                if not columnas_encontradas:
                    st.error("❌ El archivo no contiene columnas válidas.")
                else:
                    registros_nuevos = 0
                    riesgo_asignado = opciones_riesgo[categoria_seleccionada]
                    
                    for col in columnas_encontradas:
                        for dato in df[col]:
                            token = tokenizar_dato(dato)
                            if token:
                                st.session_state['database'][token] = riesgo_asignado
                                registros_nuevos += 1
                    
                    guardar_memoria(st.session_state['database'])
                    st.success(f"✅ ¡Operación exitosa! {registros_nuevos} datos procesados de las columnas: {', '.join(columnas_encontradas)}")
                    st.info("👉 Ve a la pestaña 'Dashboard Estadístico' o 'Motor de Consultas' para ver los resultados.")

# --- PESTAÑA 2: MOTOR DE CONSULTAS ---
with tab_consulta:
    st.subheader("Consultar Nivel de Riesgo (Scoring)")
    st.markdown("Ingresa un dato real. El motor generará el Hash seguro en tiempo real para buscar su score.")
    
    col_c1, col_c2, col_c3 = st.columns(3)
    with col_c1:
        email_input = st.text_input("Consultar Email")
    with col_c2:
        telefono_input = st.text_input("Consultar Teléfono")
    with col_c3:
        dni_input = st.text_input("Consultar DNI")
        
    if st.button("🔍 Ejecutar Consulta Segura", use_container_width=True):
        token_buscado = None
        if email_input: token_buscado = tokenizar_dato(email_input)
        elif telefono_input: token_buscado = tokenizar_dato(telefono_input)
        elif dni_input: token_buscado = tokenizar_dato(dni_input)
        
        if not token_buscado:
            st.warning("⚠️ Debes ingresar al menos un dato para ejecutar la consulta.")
        else:
            st.session_state['database'] = cargar_memoria()
            resultado = st.session_state['database'].get(token_buscado)
            
            st.markdown("### 📄 Reporte de Inteligencia")
            st.code(f"HASH IDENTIFICADOR (SHA-256):\n{token_buscado}", language="markdown")
            
            if resultado:
                r_col1, r_col2 = st.columns(2)
                # Usamos .get('color', '') por si acaso falta para que no rompa
                color_icono = resultado.get('color', '') 
                r_col1.metric(label="Clasificación de Estado", value=f"{resultado['status']} {color_icono}")
                r_col2.metric(label="Score de Riesgo (0-100)", value=resultado['score'])
                
                st.progress(resultado['score'] / 100)
            else:
                st.error("❌ Dato limpio. No existen registros de riesgo en la bóveda para esta identidad.")

# --- PESTAÑA 3: DASHBOARD ESTADÍSTICO ---
with tab_dashboard:
    st.subheader("Análisis Global de Riesgo")
    
    if len(st.session_state['database']) == 0:
        st.info("El Sandbox está vacío. Ve a la pestaña 'Carga de Datos' para inyectar información.")
    else:
        conteo = {}
        for info in st.session_state['database'].values():
            # Usamos .get() de forma segura
            nombre = f"{info['status']} {info.get('color', '')}"
            conteo[nombre] = conteo.get(nombre, 0) + 1
            
        df_chart = pd.DataFrame(list(conteo.items()), columns=["Categoría", "Cantidad"])
        
        col_g1, col_g2 = st.columns([2, 1])
        
        with col_g1:
            fig = px.pie(df_chart, values='Cantidad', names='Categoría', hole=0.5, 
                         title="Distribución de Entidades por Riesgo")
            fig.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig, use_container_width=True)
            
        with col_g2:
            st.markdown("### Resumen")
            st.dataframe(df_chart, use_container_width=True, hide_index=True)
