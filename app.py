import unicodedata
from datetime import date, datetime
import streamlit as st
import pandas as pd
import google.generativeai as genai

# Definimos el rango permitido (desde 1900 hasta finales de este siglo)
fecha_minima = date(1900, 1, 1)
fecha_maxima = date(2100, 12, 31)


# --- PROTECCIÓN DE API KEY ---
api_key = st.secrets["GOOGLE_API_KEY"]

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

import streamlit as st

# Versión optimizada y robusta
mensaje_limpio = """
<div style="
    background-color: #FDFBF7; 
    padding: 20px; 
    border: 2px solid #D4AF37; 
    border-radius: 10px;
    font-family: 'serif';
">
    <h2 style="color: #B8860B; text-align: center; margin-top: 0;">🏛️ Tu Privacidad es Sagrada</h2>
    
    <p style="text-align: center; font-style: italic; color: #5D6D7E; font-size: 1.1em;">
        "Esta herramienta ha sido diseñada bajo el principio de <b>anonimato total</b>."
    </p>

    <hr style="border: 0; border-top: 1px solid #D4AF37;">

    <ul style="list-style-type: '✨ '; color: #2C3E50; font-size: 15px;">
        <li><b>Efimeridad Numérica:</b> Los nombres y fechas ingresados solo existen durante el cálculo.</li>
        <li><b>Sin Registros:</b> No almacenamos tu información personal. Tu rastro se borra con el viento de Delfos.</li>
    </ul>

    <div style="background-color: #FFF9E6; padding: 15px; border-radius: 8px; margin-top: 20px;">
        <p style="font-weight: bold; color: #8E6D1A; text-align: center; margin-bottom: 5px;">⚖️ AVISO IMPORTANTE</p>
        <p style="font-size: 14px; color: #2C3E50; margin-bottom: 10px;">
            El Oráculo es gratuito para descifrar tu vibración. Para mantener la armonía, contamos con un <b>cupo limitado de consultas diarias</b>.
        </p>
        <p style="font-size: 15px; text-align: center; color: #B8860B; font-weight: bold;">
            <i>Si has alcanzado el límite, las frecuencias han completado su ciclo. ¡Vuelve más tarde!</i>
        </p>
    </div>
</div>
"""

st.markdown(mensaje_limpio, unsafe_allow_html=True)





# -------------------------
# FUNCIONES AUXILIARES
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



# Configuración de la página
st.set_page_config(page_title="Oráculo de Delfos", page_icon="✨")
st.title("🏛️ Oráculo de Delfos")

# --- UBICACIÓN A: Justo después del título (Visibilidad inmediata) ---
#st.markdown(mensaje_oraculo, unsafe_allow_html=True)

st.write("Descubre tu perfil desde una mirada empática y positiva. Es importante que introduzcas tu nombre tal y como aparece en tu certificado de nacimiento.")

# FORMULARIO DE ENTRADA
with st.form("datos_usuario"):
    nombre = st.text_input("Nombre completo")
    fecha = st.date_input(
    "Selecciona o introduce directamente tu fecha de nacimiento en formato año-mes-día",
    value=date(2000, 1, 1), 
    min_value=fecha_minima,
    max_value=fecha_maxima
    )
    boton = st.form_submit_button("Generar mi perfil")

if boton:
    with st.spinner("Calculando tu perfil..."):
        try:
            # 1. Llamada al motor
        
            fecha_texto = fecha.strftime("%Y-%m-%d")
            resultados_mock = perfil_numerologico(nombre, fecha_texto) 

            # 2. Crear el Prompt
            prompt = prompt_instruccion = f"""
            Actúa como un guía empático. Usa los siguientes datos numerológicos: {resultados_mock}.
            Tu respuesta DEBE estar formateada en Markdown siguiendo esta estructura:
            0. Muestra el nombre del core number y su valor antes de hacer la lectura maravillosa de su perfil.
            1. Un título inspirador basado en el número principal, que es la misión de vida o Life Path.
            2. Una sección titulada '## Tu Esencia' usando viñetas para las fortalezas.
            3. Explica, de forma breve y clara, el concepto de luz y sombra del potencial de misión de vida o life path, 
                como una invitación a reflexionar sobre el estado en que se encuentre el consultante al momento de la consulta. 
            4. Una sección titulada '## El Desafío como Oportunidad' con un tono muy suave y constructivo.
            5. Finaliza con una frase corta en un bloque de cita (> ) que sirva como mantra.
            6. Canaliza un mensaje inspirador y esperanzador para el consultante
                Usa negritas para resaltar las palabras con mayor carga positiva.
            """
            # 3. Llamada a Gemini
            response = model.generate_content(prompt)
        
            # 4. Muestra el resultado (Streamlit renderiza Markdown por defecto)
            st.markdown("---")
            st.markdown(response.text)
        except Exception as e:
            # Si el error es por exceso de uso (Código 429)
            if "429" in str(e) or "ResourceExhausted" in str(e):
                st.error("🏛️ **El Oráculo necesita un breve descanso.**")
                st.info("Para mantener este servicio gratuito, hay un límite de consultas por minuto. Por favor, vuelve a intentarlo más tarde.")
            else:
                # Otros errores (conexión, etc.)
                st.error(f"Hubo una interrupción en la señal estelar: {e}")
        
#Para mostrar el contador de visitas
st.write("---")
col1, col2, col3 = st.columns([1, 1, 1])

with col2:
    # Este enlace genera un badge que dice "Visitas" a la izquierda
    user_repo = "olgalimx/numerology" 
    url_final = f"https://img.shields.io/endpoint?url=https%3A%2F%2Fhits.dwyl.com%2F{user_repo}.json&label=Visitas&color=gold&style=flat-square"
    st.markdown(f"[![Visitas]({url_final})](https://hits.dwyl.com/{user_repo})")
    
#st.markdown("---")
#if st.button("🏛️ Regresar al inicio del Templo"):
#    st.rerun()
