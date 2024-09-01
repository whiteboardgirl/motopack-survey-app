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


def calculate_score(form_data):
    """Calculate a score based on the applicant's responses."""
    score = 0

    # Example scoring logic - adjust based on your needs
    if form_data['licencia_conduccion'] == 'Sí':
        score += 10

    if form_data['prestamos_actuales'] == 'No':
        score += 15
    elif form_data['prestamos_actuales'] == 'Sí':
        score -= 10

    if form_data['codeudor'] == 'Sí':
        score += 10
    elif form_data['codeudor'] == 'No':
        score -= 5

    if form_data['ingresos_mensuales'] >= 1000000:  # Example threshold
        score += 20
    elif form_data['ingresos_mensuales'] < 500000:
        score -= 15

    # Add more conditions based on your form fields
    # ...

    return score

def generate_conclusion(sentiments, nombre, apellido, score):
    positive = sum(sent['pos'] for sent in sentiments)
    negative = sum(sent['neg'] for sent in sentiments)

    if score < 0:
        eligibility = "Basado en tus respuestas, es posible que haya algunas preocupaciones con respecto a la elegibilidad para el plan de financiamiento."
    else:
        if positive > negative:
            sentiment_conclusion = "Resultado Positivo: Se recomienda a esta persona para el plan de financiamiento."
        elif negative > positive:
            sentiment_conclusion = "Resultado Negativo: No se recomienda a esta persona para el plan de financiamiento."
        else:
            sentiment_conclusion = "Resultado Neutro. Se puede continuar el proceso con esta persona para el plan de financimiento."

        eligibility = f"{sentiment_conclusion} Tu puntaje de elegibilidad es {score}."

    return f"{nombre} {apellido}: {eligibility}"

    positive = sum(sent['pos'] for sent in sentiments)
    negative = sum(sent['neg'] for sent in sentiments)
    
    if positive > negative:
        sentiment_conclusion = "Resultado Positivo: Se recomienda a esta persona para el plan de financiamiento."
    elif negative > positive:
        sentiment_conclusion = "Resultado Negativo: No se recomienda a esta persona para el plan de financiamiento."
    else:
        sentiment_conclusion = "Resultado Neutro. Se puede continuar el proceso con esta persona para el plan de financimiento."
    
    return f"{nombre} {apellido}: {sentiment_conclusion}"

def send_data_to_make(data):
    if not webhook_url:
        st.error("Webhook URL is not set. Please check your environment variables.")
        return
    
    response = requests.post(webhook_url, json=data)
    
    if response.status_code == 200:
        st.success("Tu información está siendo procesada. Te contactaremos pronto!")
    else:
        st.error("Hubo un problema con tus respuestas por favor intentalo más tarde")

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
    prestamos_actuales = st.selectbox("¿Tienes algún préstamo o crédito actualmente? *", ["No tengo", "Sí, con un familiar o amigo", "Sí, con una entidad bancaria o financiera", "Sí, con un préstamo informal o gota a gota"])
    codeudor = st.selectbox("¿Tienes un Co-Deudor(a) Colombiano(a)?", ["Sí", "No"])
    rappitendero = st.selectbox("¿Eres un Rappitendero?", ["Sí", "No"])
    ingresos_mensuales = st.selectbox("¿Cuáles son tus ingresos mensuales actuales? *", ["$0 a $500.000", "$500.000 a $1.000.000", "$1.000.000 a $1.500.000", "$1.500.000 a $2.000.000", "Más de $2.000.000"])
    movilizacion_actual = st.selectbox("¿Actualmente cómo te movilizas? *", ["A pie", "Bicicleta", "Moto propia", "Moto Alquilada", "Ciclomotor"])
    acepto_politica = st.checkbox("Acepto la política de tratamiento de datos de Motopack SAS BIC. * Ver acá: https://www.motopack.co/politica-de-tratamiento-de-datos")

    if not acepto_politica:
        st.error("Debes aceptar la política de tratamiento de datos para continuar.")
        return

    # LLM conversation questions
    business_description = st.text_area("¿Puedes contarme un poco sobre tu trabajo y cómo comenzaste?")
    business_experience = st.selectbox("¿Cuánto tiempo has estado en tu trabajo actual? (en meses)", ["1-3 meses", "3-6 meses", "6-12 meses", "más de 12 meses"])
    business_type = st.selectbox("¿Cuál es el tipo principal darías a la moto?", ["Entregas", "Transporte personal", "Entregas y Transporte personal"])

    financial_management = st.text_area("¿Cómo manejas tus finanzas actualmente?")
    payment_comfort = st.selectbox("¿Qué tan cómodo te sentirías haciendo pagos regulares para la renta de una motocicleta?", ["Muy cómodo", "Algo cómodo", "No muy cómodo", "Incomodo"])

    motorcycle_purpose = st.text_area("¿Para qué planeas utilizar la motocicleta principalmente?")
    estimated_usage = st.number_input("¿Cuántas horas al día planeas utilizar la motocicleta?", min_value=0, max_value=24)

    stress_management = st.text_area("¿Cómo manejas el estrés cuando las cosas no salen como lo planeaste?")
    responsibility = st.text_area("¿Cómo te aseguras de cumplir con tus compromisos financieros y laborales?")
    previous_experience = st.text_area("¿Has tenido alguna experiencia previa en la gestión de pagos a plazos o alquiler de equipos?")

    business_goals = st.text_area("¿Cuáles son tus objetivos a corto y largo plazo para tu trabajo?")
    impact_of_motorcycle = st.text_area("¿Cómo crees que una motocicleta podría cambiar las cosas para tu trabajo?")
    future_plans = st.text_area("¿Dónde te ves a ti mismo en los próximos 2-3 años?")

    expectations = st.text_area("¿Qué esperas obtener del programa de alquiler de motocicletas?")
    concerns = st.text_area("¿Tienes alguna preocupación sobre el proceso de alquiler de una motocicleta?")

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
            "financial_management": financial_management,
            "payment_comfort": payment_comfort,
            "motorcycle_purpose": motorcycle_purpose,
            "estimated_usage": estimated_usage,
            "stress_management": stress_management,
            "responsibility": responsibility,
            "previous_experience": previous_experience,
            "business_goals": business_goals,
            "impact_of_motorcycle": impact_of_motorcycle,
            "future_plans": future_plans,
            "expectations": expectations,
            "concerns": concerns,
        }

        # Perform sentiment analysis on selected answers
        sentiments = []
        for key, answer in form_data.items():
            if isinstance(answer, str):  # Only analyze text answers
                sentiment = analyze_sentiment(answer)
                sentiments.append(sentiment)

        
            score = calculate_score(form_data)
            conclusion = generate_conclusion(sentiments, nombre, apellido, score)


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
