import os
import streamlit as st
import openai
from googletrans import Translator, LANGUAGES
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import requests
import nltk

# Download the VADER lexicon for sentiment analysis
nltk.download('vader_lexicon')

# Load secrets from Streamlit Cloud
openai.api_key = os.getenv('OPENAI_API_KEY')
webhook_url = os.getenv('MAKE_WEBHOOK_URL')

# Initialize the Translator
translator = Translator()

# Initialize Sentiment Analyzer (for Spanish)
def analyze_sentiment(text):
    try:
        # Attempt translation
        translated_text = translator.translate(text, dest='en').text
    except Exception as e:
        st.error("Error in translation service: Using original text for sentiment analysis.")
        translated_text = text  # Fallback to the original text if translation fails
    
    sentiment_analyzer = SentimentIntensityAnalyzer()
    return sentiment_analyzer.polarity_scores(str(translated_text))

def generate_conclusion(sentiments, nombre, apellido):
    """Generate a conclusion based on the sentiment scores, including the user's name."""
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
    """Send the processed survey data to Make.com via a webhook."""
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

    # New fields for first and last name
    nombre = st.text_input("Nombre:")
    apellido = st.text_input("Apellido:")
    
    form_data = {}
    questions = [
        "¿Puedes contarme un poco sobre tu negocio y cómo comenzaste?",
        "¿Cómo crees que una motocicleta podría cambiar las cosas para tu negocio?",
        "¿Cómo manejas el estrés cuando las cosas no salen como lo planeaste?",
        "Cuando las cosas se ponen difíciles, ¿cómo sueles enfrentarlas?",
        "¿Cómo manejas tus finanzas?",
        "¿Qué tan cómodo te sentirías haciendo pagos regulares?"
    ]
    
    sentiments = []
    
    # Loop through each question and display it with a text area
    for question in questions:
        form_data[question] = st.text_area(label=question)

    if st.button("Submit"):
        conversation = "\n".join([f"P: {q}\nR: {form_data[q]}" for q in questions])
        results = []

        for question, answer in form_data.items():
            sentiment = analyze_sentiment(answer)
            sentiment_summary = f"Neg: {sentiment['neg']}, Neu: {sentiment['neu']}, Pos: {sentiment['pos']}, Comp: {sentiment['compound']}"
            sentiments.append(sentiment)
            results.append({
                "question": question, 
                "answer": answer, 
                "sentiment_summary": sentiment_summary
            })

        conclusion = generate_conclusion(sentiments, nombre, apellido)

        # Prepare the data to send
        data_to_send = {
            "conversation": conversation,
            "results": results,
            "conclusion": conclusion  # Include the name and sentiment conclusion together
        }

        # Send data to Make.com
        send_data_to_make(data_to_send)

        # Display a thank you message instead of the data
        st.success("Gracias por completar el formulario. ¡Tu información ha sido enviada!")

if __name__ == "__main__":
    main()
