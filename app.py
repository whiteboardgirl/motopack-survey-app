import os
import streamlit as st
import openai
from googletrans import Translator
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import requests
import nltk

# Download the VADER lexicon for sentiment analysis
nltk.download('vader_lexicon')

# Load secrets from environment variables
openai.api_key = os.getenv('OPENAI_API_KEY')
webhook_url = os.getenv('MAKE_WEBHOOK_URL')

# Initialize the Translator
translator = Translator()

# Initialize Sentiment Analyzer (for Spanish)
def analyze_sentiment(text):
    try:
        translated_text = translator.translate(text, dest='en').text
    except Exception:
        translated_text = text  # Fallback to the original text if translation fails
    
    sentiment_analyzer = SentimentIntensityAnalyzer()
    return sentiment_analyzer.polarity_scores(str(translated_text))

def generate_conclusion(sentiments, nombre, apellido):
    positive = sum(sent['pos'] for sent in sentiments)
    negative = sum(sent['neg'] for sent in sentiments)
    
    if positive > negative:
        sentiment_conclusion = "Overall, the responses are positive, indicating a generally optimistic outlook."
    elif negative > positive:
        sentiment_conclusion = "Overall, the responses are negative, indicating some concerns or difficulties."
    else:
        sentiment_conclusion = "The responses are neutral, suggesting a balanced perspective."
    
    return f"{nombre} {apellido}: {sentiment_conclusion}"

def send_data_to_make(data):
    if not webhook_url:
        st.error("Webhook URL is not set. Please check your environment variables.")
        return
    
    response = requests.post(webhook_url, json=data)
    
    if response.status_code == 200:
        st.success("Data successfully sent to Make.com")
    else:
        st.error("Failed to send data to Make.com")

def main():
    st.title("Registro para Adquirir una Moto")
    st.write(
        "¡Hola! Bienvenido/a a Motopack. Llenar este registro te tomará 5 minutos.\n\n"
        "Te recomendamos que antes de registrarte acá, vayas a la sección de "
        "[CÓMO FUNCIONA](https://www.motopack.co/servicio).\n\n"
        "Si cumples los requisitos y te gusta el modelo, ¡Adelante!"
    )

    # Form fields
    nombre = st.text_input("Nombre(s) *")
    apellido = st.text_input("Apellido(s) *")
    fecha_nacimiento = st.date_input("Fecha de nacimiento *", format="DD/MM/YYYY")
    tipo_documento = st.selectbox("Tipo de Documento de Identidad *", [
        "Indocumentado", 
        "Cédula de Ciudadania Venezolana", 
        "Cédula de Extranjeria", 
        "Pasaporte Legal Vigente", 
        "PEP", 
        "PPT", 
        "Cédula de Ciudadania Colombiana" ])
    numero_documento = st.text_input("Número de Documento de Identidad *")
    sexo = st.selectbox("Sexo", ["Masculino", "Femenino"])
    celular = st.text_input("Celular (con Whatsapp) *")
    ciudad_residencia = st.selectbox("Ciudad de Residencia *", ["Armenia", "Barranquilla", "Bogotá", "Bucaramanga", "Cali", "Cartagena", "Chia, Cundinamarca", "Cajica", "Cucuta", "Envigado, Antioquia", "Facatativa", "Floridablanca", "Funza", "Fusagasuga", "Ibagué", "Itagui", "Jamundi", "Manizales", "Medellín", "Monteria", "Neiva", "Otra ciudad", "Pasto", "Pereira", "Popayan", "Rioacha", "Sabaneta", "Santa Marta", "Soacha", "Suba", "Tunja", "Villavicienco", "Zipaquira" ])
    direccion_residencia = st.text_input("Dirección de Residencia *")
    barrio_residencia = st.text_input("Barrio de Residencia")
    correo_electronico = st.text_input("Correo Electrónico *")
    fuente_conocimiento = st.selectbox("¿Cómo supiste acerca de Motopack? *", ["Referido Motopack", "Alianza Rappi", "Grupo Whastapp Domiciliarios", "Redes Sociales", "Otro Medio"])
    otro_medio = st.text_input("Otro medio") if fuente_conocimiento == "Otro" else ""
    referente = st.text_input("Referente")
    alquilar_comprar = st.selectbox("¿Quieres alquilar o comprar moto? *", ["Aún no sé si quiero alquilar o comprar", "Alquilar", "Comprar"])
    licencia_conduccion = st.selectbox("¿Tienes licencia de Conducción? *", ["No", "Sí, tengo licencia de otro país", "Sí, tengo licencia venezolana", "Sí, tengo licencia colombiana"])
    personas_dependientes = st.selectbox("¿Cuántas personas dependen económicamente de ti? *", ["0", "1", "2", "3", "Más de 3"])
    nivel_escolaridad = st.selectbox("Nivel de Escolaridad", ["Sin escolaridad", "Primaria", "Técnico / Tecnólogo", "Secundaria (Bachillerato)", "Universitaria"])
    prestamos_actuales = st.selectbox("¿Tienes algún préstamo o crédito actualmente? *", ["No tengo", "Sí, con un familiar o amigo", "Sí, con una entidad bancaria o financiera", "Sí, con un préstamo informal o "gota a gota""])
    codeudor = st.selectbox("¿Tienes un Co-Deudor(a) Colombiano(a)?", ["Sí", "No"])
    rappitendero = st.selectbox("¿Eres un Rappitendero?", ["Sí", "No"])
    ingresos_mensuales = st.selectbox("¿Cuáles son tus ingresos mensuales actuales? *", ["$0 a $500.000", "$500.000 a $1.000.000", "$1.000.000 a $1.500.000", "$1.500.000 a $2.000.000", "Más de $2.000.000"])
    movilizacion_actual = st.text_area("¿Actualmente cómo te movilizas? *")
    acepto_politica = st.checkbox("Acepto la política de tratamiento de datos de Motopack SAS BIC. * Ver acá: https://www.motopack.co/politica-de-tratamiento-de-datos")

    if not acepto_politica:
        st.error("Debes aceptar la política de tratamiento de datos para continuar.")
        return

    # LLM conversation questions
    business_description = st.text_area("¿Puedes contarme un poco sobre tu negocio y cómo comenzaste?")
    business_experience = st.number_input("¿Cuánto tiempo has estado en tu negocio actual? (en años)", min_value=0, max_value=50)
    business_type = st.selectbox("¿Cuál es el tipo principal de negocio que manejas?", ["Entregas", "Transporte personal", "Otro"])
    current_transportation = st.text_input("¿Actualmente utilizas algún medio de transporte para tu negocio? Si es así, ¿cuál?")

    income_level = st.number_input("¿Cuál es tu ingreso mensual promedio?", min_value=0)
    financial_management = st.text_area("¿Cómo manejas tus finanzas actualmente?")
    payment_comfort = st.selectbox("¿Qué tan cómodo te sentirías haciendo pagos regulares para la renta de una motocicleta?", ["Muy cómodo", "Algo cómodo", "No muy cómodo", "Incomodo"])

    motorcycle_purpose = st.text_area("¿Para qué planeas utilizar la motocicleta principalmente?")
    estimated_usage = st.number_input("¿Cuántas horas al día planeas utilizar la motocicleta?", min_value=0, max_value=24)
    distance_traveled = st.number_input("¿Cuál es la distancia promedio que planeas recorrer diariamente con la motocicleta? (en km)", min_value=0)

    stress_management = st.text_area("¿Cómo manejas el estrés cuando las cosas no salen como lo planeaste?")
    responsibility = st.text_area("¿Cómo te aseguras de cumplir con tus compromisos financieros y laborales?")
    previous_experience = st.text_area("¿Has tenido alguna experiencia previa en la gestión de pagos a plazos o alquiler de equipos?")

    business_goals = st.text_area("¿Cuáles son tus objetivos a corto y largo plazo para tu negocio?")
    impact_of_motorcycle = st.text_area("¿Cómo crees que una motocicleta podría cambiar las cosas para tu negocio?")
    future_plans = st.text_area("¿Dónde te ves a ti mismo y a tu negocio en los próximos 2-3 años?")

    expectations = st.text_area("¿Qué esperas obtener del programa de alquiler de motocicletas?")
    concerns = st.text_area("¿Tienes alguna preocupación sobre el proceso de alquiler de una motocicleta?")
    suggestions = st.text_area("¿Tienes alguna sugerencia sobre cómo podríamos mejorar nuestro programa de alquiler?")

    if st.button("Submit", use_container_width=True):
        # Collect all answers
        form_data = {
            "nombre": nombre,
            "apellido": apellido,
            "fecha_nacimiento": fecha_nacimiento.strftime("%d/%m/%Y"),
            "tipo_documento": tipo_documento,
            "numero_documento": numero_documento,
            "sexo": sexo,
            "celular": celular,
            "ciudad_residencia": ciudad_residencia,
            "direccion_residencia": direccion_residencia,
            "barrio_residencia": barrio_residencia,
            "correo_electronico": correo_electronico,
            "fuente_conocimiento": fuente_conocimiento,
            "otro_medio": otro_medio,
            "referente": referente,
            "alquilar_comprar": alquilar_comprar,
            "licencia_conduccion": licencia_conduccion,
            "personas_dependientes": personas_dependientes,
            "nivel_escolaridad": nivel_escolaridad,
            "prestamos_actuales": prestamos_actuales,
            "codeudor": codeudor,
            "rappitendero": rappitendero,
            "ingresos_mensuales": ingresos_mensuales,
            "movilizacion_actual": movilizacion_actual,
            "acepto_politica": acepto_politica,
            "business_description": business_description,
            "business_experience": business_experience,
            "business_type": business_type,
            "current_transportation": current_transportation,
            "income_level": income_level,
            "financial_management": financial_management,
            "payment_comfort": payment_comfort,
            "motorcycle_purpose": motorcycle_purpose,
            "estimated_usage": estimated_usage,
            "distance_traveled": distance_traveled,
            "stress_management": stress_management,
            "responsibility": responsibility,
            "previous_experience": previous_experience,
            "business_goals": business_goals,
            "impact_of_motorcycle": impact_of_motorcycle,
            "future_plans": future_plans,
            "expectations": expectations,
            "concerns": concerns,
            "suggestions": suggestions
        }

        # Perform sentiment analysis on selected answers
        sentiments = []
        for key, answer in form_data.items():
            if isinstance(answer, str):  # Only analyze text answers
                sentiment = analyze_sentiment(answer)
                sentiments.append(sentiment)

        conclusion = generate_conclusion(sentiments, nombre, apellido)

        # Prepare the data to send
        data_to_send = {
            "form_data": form_data,
            "conclusion": conclusion
        }

        # Send data to Make.com
        send_data_to_make(data_to_send)

        # Display a thank you message
        st.success("Gracias por completar el formulario. ¡Tu información ha sido enviada!")

if __name__ == "__main__":
    main()
