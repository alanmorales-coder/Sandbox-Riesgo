import streamlit as st
import pandas as pd
import hashlib
import json
import os

# --- NUEVO: CONFIGURACIÓN DE MEMORIA FÍSICA ---
ARCHIVO_MEMORIA = "memoria_sandbox.json"

def cargar_memoria():
    """Lee los datos guardados en el archivo físico."""
    if os.path.exists(ARCHIVO_MEMORIA):
        with open(ARCHIVO_MEMORIA, "r") as f:
            return json.load(f)
    return {}

def guardar_memoria(datos):
    """Guarda los datos en el archivo físico."""
    with open(ARCHIVO_MEMORIA, "w") as f:
        json.dump(datos, f)

# 1. CONFIGURACIÓN DE LA PÁGINA
st.set_page_config(page_title="Sandbox de Riesgo", page_icon="🛡️", layout="centered")

# 2. BASE DE DATOS (Carga desde el archivo JSON al iniciar)
if 'database' not in st.session_state:
    st.session_state['database'] = cargar_memoria()

# 3. FUNCIÓN PARA TOKENIZAR (Cifrado SHA-256)
def tokenizar_dato(valor):
    if pd.isna(valor) or valor == "": 
        return ""
    valor_limpio = str(valor).strip().lower()
    return hashlib.sha256(valor_limpio.encode()).hexdigest()

# 4. INTERFAZ GRÁFICA
st.title("🛡️ Sandbox: Privacidad y Score de Riesgo")
st.markdown("Prototipo académico con memoria persistente para tokenización de datos.")

total_en_memoria = len(st.session_state['database'])
st.info(f"💾 **Base de Datos Segura:** Actualmente hay **{total_en_memoria}** datos tokenizados guardados.")

st.divider()

# SECCIÓN A: SUBIR DATOS
st.header("1. Subir Base de Datos (Excel)")
archivo_subido = st.file_uploader("Sube tu archivo .xlsx", type=["xlsx"])
es_lista_negra = st.toggle("🚨 Marcar como Lista Negra (Alto Riesgo)")

if archivo_subido is not None:
    if st.button("Procesar y Guardar"):
        df = pd.read_excel(archivo_subido)
        columnas_esperadas = ["email", "telefono", "dni"]
        columnas_encontradas = [col for col in columnas_esperadas if col in df.columns]
        
        if not columnas_encontradas:
            st.error("❌ El archivo no contiene columnas válidas ('email', 'telefono' o 'dni').")
        else:
            registros_nuevos = 0
            for col in columnas_encontradas:
                for dato in df[col]:
                    token = tokenizar_dato(dato)
                    if token:
                        riesgo = {"status": "Alto Riesgo (Lista Negra) 🔴", "score": 99} if es_lista_negra else {"status": "OK 🟢", "score": 0}
                        st.session_state['database'][token] = riesgo
                        registros_nuevos += 1
            
            # --- NUEVO: GUARDAR EN EL ARCHIVO FÍSICO ---
            guardar_memoria(st.session_state['database'])
                        
            st.success(f"✔️ Columnas procesadas: **{', '.join(columnas_encontradas)}**")
            st.success(f"🚀 ¡Éxito! Se guardaron {registros_nuevos} registros permanentemente.")
            st.button("Actualizar Vista 🔄")

st.divider()

# SECCIÓN B: CONSULTAR DATOS
st.header("2. Consultar Nivel de Riesgo")

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
        st.warning("Ingresa un dato para consultar.")
    else:
        # Volvemos a cargar por si hubo cambios
        st.session_state['database'] = cargar_memoria()
        resultado = st.session_state['database'].get(token_buscado)
        
        st.subheader("Resultados del Motor de Riesgo:")
        st.info(f"**Token generado:** `{token_buscado}`")
        
        if resultado:
            col_res1, col_res2 = st.columns(2)
            col_res1.metric(label="Estado", value=resultado["status"])
            col_res2.metric(label="Score", value=f"{resultado['score']} / 100")
        else:
            st.error("El dato no se encuentra en la base de datos.")
