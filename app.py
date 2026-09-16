import streamlit as st
import pandas as pd
import hashlib

# 1. CONFIGURACIÓN DE LA PÁGINA
st.set_page_config(page_title="Sandbox de Riesgo", page_icon="🛡️", layout="centered")

# 2. BASE DE DATOS EN MEMORIA (Conserva los datos mientras no recargues la página)
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
st.markdown("Prototipo académico para tokenización de datos y consulta de riesgo.")

# ¡NUEVO! Mostrar cuántos datos hay en la bóveda
total_en_memoria = len(st.session_state['database'])
st.info(f"💾 **Memoria Activa:** Actualmente hay **{total_en_memoria}** datos tokenizados en la bóveda de este Sandbox.")

st.divider()

# SECCIÓN A: SUBIR DATOS
st.header("1. Subir Base de Datos (Excel)")
st.markdown("Puedes subir un archivo que tenga las 3 columnas (`email`, `telefono`, `dni`) **o solo alguna de ellas**.")
archivo_subido = st.file_uploader("Sube tu archivo .xlsx", type=["xlsx"])
es_lista_negra = st.toggle("🚨 Marcar estos datos como Lista Negra (Alto Riesgo)")

if archivo_subido is not None:
    if st.button("Procesar y Tokenizar Archivo"):
        # Leer el excel
        df = pd.read_excel(archivo_subido)
        
        columnas_esperadas = ["email", "telefono", "dni"]
        # Filtramos para ver cuáles de las columnas esperadas realmente están en el Excel
        columnas_encontradas = [col for col in columnas_esperadas if col in df.columns]
        
        if not columnas_encontradas:
            st.error("❌ El archivo no contiene ninguna columna válida. Debe tener al menos el encabezado 'email', 'telefono' o 'dni'.")
        else:
            registros_nuevos = 0
            
            # Procesamos SOLAMENTE las columnas que el sistema encontró
            for col in columnas_encontradas:
                for dato in df[col]:
                    token = tokenizar_dato(dato)
                    if token:
                        riesgo = {"status": "Alto Riesgo (Lista Negra) 🔴", "score": 99} if es_lista_negra else {"status": "OK 🟢", "score": 0}
                        st.session_state['database'][token] = riesgo
                        registros_nuevos += 1
                        
            st.success(f"✔️ Se detectaron las columnas: **{', '.join(columnas_encontradas)}**")
            st.success(f"🚀 ¡Éxito! Se añadieron {registros_nuevos} nuevos registros tokenizados a la memoria.")
            st.button("Actualizar Contador 🔄") # Un botón simple para recargar la vista y ver el contador subir

st.divider()

# SECCIÓN B: CONSULTAR DATOS
st.header("2. Consultar Nivel de Riesgo")
st.markdown("Ingresa un dato para simular la consulta. El sistema lo convertirá en token y buscará su riesgo.")

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
            st.error("El dato no se encuentra en la bóveda. Score de Riesgo: Desconocido.")
