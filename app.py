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


#Cálculo de la misión de vida
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
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@400;600&display=swap');
    </style>

    <div style="text-align: center; padding: 10px;">
        <h1 style="
            color: #5A0FBF; 
            font-family: 'Cinzel', serif; 
            text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
            letter-spacing: 4px;          
        ">
            🏛️ El Oráculo de Delfos
        </h1>
        <p style="color: #708090; font-style: italic; margin-top: -10px; font-size: 18px;">
            Desde tiempos antiguos, los números han sido vistos como símbolos que revelan lo invisible.
            A partir de tu nombre y tu fecha de nacimiento, es posible reconocer patrones que hablan de tu
            esencia, tus ciclos y tus aprendizajes. 
            Este oráculo no dicta tu destino… solo te muestra un reflejo para que puedas mirarte con mayor claridad.
            Conócete a ti mismo. Tú diriges tu historia.
        </p>
    </div>
    """, 
    unsafe_allow_html=True
)

# Definimos el contenido con CSS adaptable
html_responsivo = """
<div style="
    background-color: #FDFBF7; 
    padding: 15px; 
    border: 2px solid #4B0082; 
    border-radius: 12px; 
    font-family: serif; 
    color: #2C3E50;
    max-width: 95%; /* Evita que choque con los bordes del móvil */
    margin: auto;
">
    <h2 style="color: #4B0082; text-align: center; font-size: 22px;">🌫️ Tu Privacidad es Sagrada</h2>
    
    <p style="text-align: center; font-style: italic; font-size: 16px;">
        "Anonimato total en cada cálculo."
    </p>

    <hr style="border: 0; border-top: 1px solid #C0C0C0;">

    <div style="font-size: 14px;">
        <p>🤫 <b>Efimeridad:</b> Los datos solo existen durante el cálculo.</p>
        <p>🛡️ <b>Sin Registros:</b> Tu rastro se borra con el viento de Delfos.</p>
    </div>

    <div style="background-color: #F4F0FA; padding: 12px; border-radius: 8px; border: 1px solid #4B0082;">
        <p style="font-weight: bold; color: #4B0082; text-align: center; font-size: 15px; margin-bottom: 5px;">⚖️ AVISO IMPORTANTE</p>
        <p style="font-size: 13px; line-height: 1.4;">
            El Oráculo es gratuito. Para mantener la armonía, el modelo tiene un cupo limitado de consultas diarias.
        </p>
        <p style="font-size: 14px; text-align: center; color: #4B0082; font-weight: bold; margin-top: 8px;">
            Si alcanzaste el límite, las frecuencias han completado su ciclo. ¡Vuelve más tarde!
        </p>
    </div>
</div>
"""

# USAMOS st.components.v1.html PERO CON AJUSTES
# El truco es calcular el height necesario o usar scrolling=True
st.components.v1.html(html_responsivo, height=500, scrolling=True)


# --- UBICACIÓN A: Justo después del título (Visibilidad inmediata) ---
st.write("Descubre tu perfil desde una mirada empática y positiva. Es importante que introduzcas tu nombre tal y como aparece en tu certificado de nacimiento.")

# FORMULARIO DE ENTRADA
with st.form("datos_usuario"):
    nombre = st.text_input("Nombre completo")
    fecha = st.date_input(
    "Selecciona o introduce directamente tu fecha de nacimiento en formato año-mes-día, por favor verifica que sea correcta.",
    value=date(2000, 1, 1), 
    min_value=fecha_minima,
    max_value=fecha_maxima
    )
    boton = st.form_submit_button("Generar mi perfil")

if boton:
    with st.spinner("Espera un momento, estoy calculando tu perfil..."):
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
            7. Menciona los análisis adicionales de desafíos y pináculos que puedes hacer, así como el análisis de compatibilidad
               con otras personas basado en su perfil numerológico, e invitalos a hacer clic en el botón que se incluye en la 
               página al final, no lo incluyas tú, este botón ya está incorporado en la página.
               
            """
            # 3. Llamada a Gemini
            response = model.generate_content(prompt)
        
            # 4. Muestra el resultado (Streamlit renderiza Markdown por defecto)
            st.markdown("---")
            #st.markdown(response.text)
            st.markdown(f"""
                <div style="
                    color: #C9A646;
                    font-family: 'Georgia', serif;
                    font-size: 20px;
                    line-height: 1.8;
                    text-align: justify;
                    margin-top: 30px;
            ">
                {response.text}
                </div>
            """, unsafe_allow_html=True)


        
        except Exception as e:
            # Si el error es por exceso de uso (Código 429)
            if "429" in str(e) or "ResourceExhausted" in str(e):
                st.error("🏛️ **El Oráculo necesita un breve descanso.**")
                st.info("Para mantener este servicio gratuito, hay un límite de consultas por minuto. Por favor, vuelve a intentarlo más tarde.")
            else:
                # Otros errores (conexión, etc.)
                st.error(f"Hubo una interrupción en la señal estelar: {e}")

st.write("---") # Una línea divisoria sutil
st.write("¿Deseas profundizar en tu partitura numérica?")
st.link_button("Solicitar lectura completa sin ningún costo", "mailto:oraculo.delfos.orion@gmail.com")


#Para mostrar el contador de visitas
st.write("---")
col1, col2, col3 = st.columns([1, 1, 1])

with col2:
    # Este enlace genera un badge que dice "Visitas" a la izquierda
    user_repo = "olgalimx/numerology" 
    url_final = f"https://img.shields.io/endpoint?url=https%3A%2F%2Fhits.dwyl.com%2F{user_repo}.json&label=Visitas&color=gold&style=flat-square"
    st.markdown(f"[![Visitas]({url_final})](https://hits.dwyl.com/{user_repo})")
    
