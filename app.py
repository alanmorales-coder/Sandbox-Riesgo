import streamlit as st
import pandas as pd
import hashlib

# 1. CONFIGURACIÓN DE LA PÁGINA
st.set_page_config(page_title="Sandbox de Riesgo", page_icon="🛡️", layout="centered")

# 2. BASE DE DATOS EN MEMORIA (Usamos "session_state" para que no se borre al usar la app)
if 'database' not in st.session_state:
    st.session_state['database'] = {}

# 3. FUNCIÓN PARA TOKENIZAR (Cifrado SHA-256)
def tokenizar_dato(valor):
    if pd.isna(valor) or valor == "": 
        return ""
    valor_limpio = str(valor).strip().lower()
    return hashlib.sha256(valor_limpio.encode()).hexdigest()

# 4. INTERFAZ GRÁFICA
st.title("🛡️ Sandbox: Privacidad y Score de Riesgo")
st.markdown("Prototipo académico para tokenización de datos (Email, Teléfono, DNI) y consulta de riesgo.")

st.divider()

# SECCIÓN A: SUBIR DATOS
st.header("1. Subir Base de Datos (Excel)")
archivo_subido = st.file_uploader("Sube tu archivo .xlsx", type=["xlsx"])
es_lista_negra = st.toggle("🚨 Marcar estos datos como Lista Negra (Alto Riesgo)")

if archivo_subido is not None:
    if st.button("Procesar y Tokenizar Archivo"):
        # Leer el excel
        df = pd.read_excel(archivo_subido)
        registros_guardados = 0
        columnas_esperadas = ["email", "telefono", "dni"]
        
        # Procesar columnas
        for col in columnas_esperadas:
            if col in df.columns:
                for dato in df[col]:
                    token = tokenizar_dato(dato)
                    if token:
                        riesgo = {"status": "Alto Riesgo (Lista Negra) 🔴", "score": 99} if es_lista_negra else {"status": "OK 🟢", "score": 0}
                        st.session_state['database'][token] = riesgo
                        registros_guardados += 1
                        
        st.success(f"¡Éxito! Se tokenizaron y guardaron {registros_guardados} registros en la bóveda segura.")

st.divider()

# SECCIÓN B: CONSULTAR DATOS
st.header("2. Consultar Nivel de Riesgo")
st.markdown("Ingresa un dato para simular la consulta. El sistema lo convertirá en token y buscará su riesgo sin exponer el dato real.")

col1, col2, col3 = st.columns(3)
with col1:
    email_input = st.text_input("Email")
with col2:
    telefono_input = st.text_input("Teléfono")
with col3:
    dni_input = st.text_input("DNI")

if st.button("🔍 Consultar Score"):
    token_buscado = None
    
    if email_input: token_buscado = tokenizar_dato(email_input)
    elif telefono_input: token_buscado = tokenizar_dato(telefono_input)
    elif dni_input: token_buscado = tokenizar_dato(dni_input)
    
    if not token_buscado:
        st.warning("Por favor, ingresa al menos un dato para consultar.")
    else:
        # Buscar en la memoria
        resultado = st.session_state['database'].get(token_buscado)
        
        st.subheader("Resultados del Motor de Riesgo:")
        st.info(f"**Token generado (SHA-256):** `{token_buscado}`")
        
        if resultado:
            col_res1, col_res2 = st.columns(2)
            col_res1.metric(label="Estado", value=resultado["status"])
            col_res2.metric(label="Score de Riesgo", value=f"{resultado['score']} / 100")
        else:
            st.error("El dato no se encuentra en nuestras bases de datos.")
