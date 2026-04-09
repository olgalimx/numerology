import unicodedata
from datetime import datetime
import streamlit as st
import google.generativeai as genai


# --- PROTECCIÓN DE API KEY ---
# En Streamlit Cloud, esto se configura en "Settings > Secrets"
#api_key = st.secrets["GOOGLE_API_KEY"]
api_key = "AIzaSyB16igGs2ewPzal3jQNB5xiqcthtlTUzf8"
# Intento de carga robusta
"""if "GOOGLE_API_KEY" in st.secrets:
    api_key = st.secrets["GOOGLE_API_KEY"]
else:
    st.error("⚠️ La clave 'GOOGLE_API_KEY' no se encuentra en los Secrets.")
    st.write("Variables detectadas:", list(st.secrets.to_dict().keys()))
    st.stop() # Detiene la ejecución para que no salga el error feo"""

genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-flash-latest')


# Tabla pitagórica
PITAGORICA = {
    1: "AJS",
    2: "BKT",
    3: "CLU",
    4: "DMV",
    5: "ENW",
    6: "FOX",
    7: "GPY",
    8: "HQZ",
    9: "IR"
}

# Invertir diccionario
LETRA_A_NUM = {letra: num for num, letras in PITAGORICA.items() for letra in letras}

VOCALES = set("AEIOU")

# -------------------------
# Funciones auxiliares
# -------------------------

def quitar_acentos(texto):
    texto = unicodedata.normalize('NFD', texto)
    texto = ''.join(c for c in texto if unicodedata.category(c) != 'Mn')
    return texto.upper()

def es_vocal(letra, palabra):
    if letra in VOCALES:
        return True
    if letra == "Y":
        return True if all(l not in VOCALES for l in palabra.replace("Y", "")) else False
    return False

def reducir_numero(n):
    while n > 9 and n not in (11, 22, 33):
        n = sum(int(d) for d in str(n))
    return n

def valor_nombre(nombre, tipo="total"):
    nombre = quitar_acentos(nombre)
    total = 0

    for palabra in nombre.split():
        for letra in palabra:
            if letra not in LETRA_A_NUM:
                continue

            if tipo == "vocales" and not es_vocal(letra, palabra):
                continue
            if tipo == "consonantes" and es_vocal(letra, palabra):
                continue

            total += LETRA_A_NUM[letra]

    return reducir_numero(total)

# -------------------------
# NUEVA FUNCIÓN: Life Path
# -------------------------

def calcular_mision_vida(fecha_nacimiento):
    """
    fecha_nacimiento en formato 'YYYY-MM-DD'
    """
    fecha = datetime.strptime(fecha_nacimiento, "%Y-%m-%d")

    suma = sum(int(d) for d in fecha.strftime("%Y%m%d"))
    return reducir_numero(suma)

# -------------------------
# Función principal
# -------------------------

def perfil_numerologico(nombre_completo, fecha_nacimiento):
    fecha = datetime.strptime(fecha_nacimiento, "%Y-%m-%d")

    expresion = valor_nombre(nombre_completo, "total")
    alma = valor_nombre(nombre_completo, "vocales")
    personalidad = valor_nombre(nombre_completo, "consonantes")
    cumple = reducir_numero(fecha.day)
    mision = calcular_mision_vida(fecha_nacimiento)

    return {
        "expresion": expresion,
        "alma": alma,
        "personalidad": personalidad,
        "birthday": cumple,
        "mision_vida": mision
    }


# Aquí importarías tu motor: from motor_numerologico import calcular_perfil

# Configuración de la página
st.set_page_config(page_title="Espejo Numerológico", page_icon="✨")


st.title("✨ Espejo Numerológico")
st.write("Descubre tu perfil desde una mirada empática y positiva.")

# Formulario de entrada
with st.form("datos_usuario"):
    nombre = st.text_input("Nombre completo")
    fecha = st.date_input("Fecha de nacimiento")
    boton = st.form_submit_button("Generar mi perfil")

if boton:
    with st.spinner("Calculando tus vibraciones..."):
        # 1. Llamas a tu motor (ejemplo hipotético)
        # resultados = calcular_perfil(nombre, fecha)
        fecha_texto = fecha.strftime("%Y-%m-%d")
        resultados_mock = perfil_numerologico(nombre, fecha_texto) # Reemplazar por tu motor
        
        # 2. Creas el Prompt
        prompt = prompt_instruccion = f"""
        Actúa como un guía empático. Usa los siguientes datos numerológicos: {resultados_motor}.
        Tu respuesta DEBE estar formateada en Markdown siguiendo esta estructura:

        1. Un título inspirador basado en el número principal, que es la misión de vida o Life Path.
        2. Una sección titulada '## Tu Esencia' usando viñetas para las fortalezas.
        3. Una sección titulada '## El Desafío como Oportunidad' con un tono muy suave y constructivo.
        4. Finaliza con una frase corta en un bloque de cita (> ) que sirva como mantra.
        5. Canaliza un mensaje inspirador y esperanzador para el consultante
        Usa negritas para resaltar las palabras con mayor carga positiva.
        """
        # 3. Llamas a Gemini
        response = model.generate_content(prompt)
        
        # 4. Muestras el resultado (Streamlit renderiza Markdown por defecto)
        st.markdown("---")
        st.markdown(response.text)
