import os
import streamlit as st
import openai
from googletrans import Translator
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
    translated_text = translator.translate(text, dest='en').text
    sentiment_analyzer = SentimentIntensityAnalyzer()
    return sentiment_analyzer.polarity_scores(str(translated_text))

def generate_conclusion(sentiments):
    """Generate a simple conclusion based on the sentiment scores."""
    positive = sum(sent['pos'] for sent in sentiments)
    negative = sum(sent['neg'] for sent in sentiments)
    
    if positive > negative:
        return "Overall, the responses are positive, indicating a generally optimistic outlook."
    elif negative > positive:
        return "Overall, the responses are negative, indicating some concerns or difficulties."
    else:
        return "The responses are neutral, suggesting a balanced perspective."

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
        "¡Hola! Bienvenido/a a Motopack. Queremos conocerte un poco mejor\n\n"
        "Responde las preguntas lo mejor posible, se tu mismo!\n\n"
        "Gracias por tus respuestas!"
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
    for question in questions:
        form_data[question] = st.text_area(question)

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

        conclusion = generate_conclusion(sentiments)

        # Prepare the data to send
        data_to_send = {
            "conversation": conversation,
            "results": results,
            "conclusion": conclusion
        }

        # Send data to Make.com
        send_data_to_make(data_to_send)

if __name__ == "__main__":
    main()
