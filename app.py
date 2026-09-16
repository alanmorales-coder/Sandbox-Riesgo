import streamlit as st
import pandas as pd
import hashlib
import json
import os

# --- CONFIGURACIÓN DE MEMORIA FÍSICA ---
ARCHIVO_MEMORIA = "memoria_sandbox_segura.json" # Cambiamos el nombre para empezar con la nueva seguridad

# --- NUEVO: LA "SAL" CRIPTOGRÁFICA (SALTING) ---
# Esta es la palabra secreta. En un banco real esto se guarda bajo llave, no en el código.
SAL_SECRETA = "Tr#9q!Lp$2*mZ&8vX@1y_Sandbox_Riesgo_2026_UltraSecreto"

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

# 2. CARGA DE BASE DE DATOS
if 'database' not in st.session_state:
    st.session_state['database'] = cargar_memoria()

# 3. FUNCIÓN PARA TOKENIZAR (Ahora con SALTING)
def tokenizar_dato(valor):
    if pd.isna(valor) or valor == "": 
        return ""
    valor_limpio = str(valor).strip().lower()
    
    # Aquí ocurre la magia: unimos el dato real con nuestra SAL secreta
    dato_salado = valor_limpio + SAL_SECRETA
    
    # Aplicamos el SHA-256 al dato ya mezclado
    return hashlib.sha256(dato_salado.encode()).hexdigest()

# 4. INTERFAZ GRÁFICA
st.title("🛡️ Sandbox: Privacidad y Score de Riesgo")
st.markdown("Prototipo académico con **Salting Criptográfico (SHA-256)** para prevención de fraude y tokenización de datos confidenciales.")

# --- SECCIÓN DE ESTADÍSTICAS ---
total_en_memoria = len(st.session_state['database'])
st.info(f"💾 **Base de Datos Segura:** Actualmente hay **{total_en_memoria}** datos guardados en el Sandbox.")

if total_en_memoria > 0:
    with st.expander("📊 Ver distribución de riesgos (Gráfico)"):
        # Contar cuántos datos hay de cada categoría
        conteo_riesgos = {}
        for info in st.session_state['database'].values():
            estado = info["status"]
            conteo_riesgos[estado] = conteo_riesgos.get(estado, 0) + 1
        
        # Generar gráfico de barras
        df_chart = pd.DataFrame(list(conteo_riesgos.items()), columns=["Categoría", "Cantidad"])
        st.bar_chart(df_chart.set_index("Categoría"))

st.divider()

# SECCIÓN A: SUBIR DATOS
st.header("1. Subir Base de Datos (Excel)")
st.markdown("Sube un archivo `.xlsx`. Puede contener solo `email`, solo `telefono`, solo `dni`, o las tres columnas juntas.")
archivo_subido = st.file_uploader("Sube tu archivo .xlsx", type=["xlsx"])

# --- MENÚ DESPLEGABLE DE RIESGO ---
opciones_riesgo = {
    "OK (Buen Dato)": {"status": "OK 🟢", "score": 0},
    "Posible Fraude (No confirmado)": {"status": "Posible Fraude 🟡", "score": 50},
    "Fraude: Cuenta Mula": {"status": "Cuenta Mula 🟠", "score": 75},
    "Fraude: Onboarding": {"status": "Fraude Onboarding 🟠", "score": 75},
    "Fraude: Transaccional": {"status": "Fraude Transaccional 🔴", "score": 99}
}

categoria_seleccionada = st.selectbox(
    "Selecciona la categoría de riesgo para los datos de este archivo:", 
    list(opciones_riesgo.keys())
)

if archivo_subido is not None:
    if st.button("Procesar y Guardar"):
        df = pd.read_excel(archivo_subido)
        columnas_esperadas = ["email", "telefono", "dni"]
        columnas_encontradas = [col for col in columnas_esperadas if col in df.columns]
        
        if not columnas_encontradas:
            st.error("❌ El archivo no contiene columnas válidas ('email', 'telefono' o 'dni').")
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
                        
            st.success(f"✔️ Columnas procesadas con éxito: **{', '.join(columnas_encontradas)}**")
            st.success(f"🚀 Se guardaron {registros_nuevos} registros clasificados como '{categoria_seleccionada}'.")
            st.button("Actualizar Vista 🔄")

st.divider()

# SECCIÓN B: CONSULTAR DATOS
st.header("2. Consultar Nivel de Riesgo")
st.markdown("Ingresa un dato real. El sistema le añadirá la 'Sal' criptográfica invisible, lo tokenizará de forma segura y buscará su score en la bóveda.")

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
        st.session_state['database'] = cargar_memoria()
        resultado = st.session_state['database'].get(token_buscado)
        
        st.subheader("Resultados del Motor de Riesgo:")
        st.info(f"**Token generado (SHA-256 + Salting):** `{token_buscado}`")
        
        if resultado:
            col_res1, col_res2 = st.columns(2)
            col_res1.metric(label="Estado", value=resultado["status"])
            col_res2.metric(label="Score de Riesgo", value=f"{resultado['score']} / 100")
        else:
            st.error("El dato consultado no se encuentra en la base de datos.")
