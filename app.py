import os
import streamlit as st
import openai
from googletrans import Translator
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import requests
import nltk

# Download the VADER lexicon for sentiment analysis
nltk.download('vader_lexicon')

# Load environment variables directly from the Streamlit Cloud environment
openai.api_key = os.getenv('OPENAI_API_KEY')

# Initialize the Translator
translator = Translator()

# Initialize Sentiment Analyzer (for Spanish)
def analyze_sentiment(text):
    translated_text = translator.translate(text, dest='en').text
    sentiment_analyzer = SentimentIntensityAnalyzer()
    return sentiment_analyzer.polarity_scores(str(translated_text))

def send_data_to_make(data):
    """Send the processed survey data to Make.com via a webhook."""
    webhook_url = os.getenv('MAKE_WEBHOOK_URL')
    
    # Check if the webhook URL is set
    if not webhook_url:
        st.error("Webhook URL is not set. Please check your environment variables.")
        return

    # Send the POST request to Make.com
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
    
    form_data = {}
    questions = [
        "¿Puedes contarme un poco sobre tu negocio y cómo comenzaste?",
        "¿Cómo crees que una motocicleta podría cambiar las cosas para tu negocio?",
        "¿Cómo manejas el estrés cuando las cosas no salen como lo planeaste?",
        "Cuando las cosas se ponen difíciles, ¿cómo sueles enfrentarlas?",
        "¿Cómo manejas tus finanzas?",
        "¿Qué tan cómodo te sentirías haciendo pagos regulares?"
    ]
    
    for question in questions:
        form_data[question] = st.text_area(question)

    if st.button("Submit"):
        conversation = "\n".join([f"P: {q}\nR: {form_data[q]}" for q in questions])
        results = []

        for question, answer in form_data.items():
            sentiment = analyze_sentiment(answer)
            sentiment_summary = f"Neg: {sentiment['neg']}, Neu: {sentiment['neu']}, Pos: {sentiment['pos']}, Comp: {sentiment['compound']}"
            results.append({"question": question, "answer": answer, "sentiment": sentiment_summary})

        # Send data to Make.com
        send_data_to_make({"conversation": conversation, "results": results})

if __name__ == "__main__":
    main()
