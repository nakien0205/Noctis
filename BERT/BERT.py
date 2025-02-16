import json
import random
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


class IntentRecognizer:
    def __init__(self, json_file):
        # Load the intents from the provided JSON file
        with open(json_file, 'r') as f:
            self.data = json.load(f)
        self.intents = self.data['intents']

        # Collect all sample texts and corresponding intent labels
        self.samples = []
        self.labels = []
        for intent in self.intents:
            for text in intent['text']:
                self.samples.append(text)
                self.labels.append(intent['intent'])

        # Initialize and fit the TF-IDF vectorizer on all sample texts
        self.vectorizer = TfidfVectorizer().fit(self.samples)

    def predict_intent(self, query):
        """
        Given an input query, compute the cosine similarity between the query and
        each sample text in every intent. Return the intent with the highest similarity.
        """
        query_vec = self.vectorizer.transform([query])
        best_intent = None
        best_score = 0.0

        for intent in self.intents:
            samples = intent['text']
            samples_vec = self.vectorizer.transform(samples)
            # Compute the maximum similarity score for this intent's samples
            score = cosine_similarity(query_vec, samples_vec).max()
            if score > best_score:
                best_score = score
                best_intent = intent
        return best_intent, best_score

    def get_response(self, intent):
        """
        Randomly select one of the responses from the intent.
        """
        responses = intent.get('responses', [])
        if responses:
            return random.choice(responses)
        return "I don't have a response for that."


if __name__ == '__main__':
    # Ensure the Intent.json file (see :contentReference[oaicite:0]{index=0}) is in the same directory as this script.
    recognizer = IntentRecognizer('Intent.json')
    print("Intent recognizer is running. Type 'exit' to quit.")

    while True:
        user_query = input("User: ")
        if user_query.lower() in ['exit', 'quit']:
            break

        intent, score = recognizer.predict_intent(user_query)
        if intent:
            print(f"Predicted Intent: {intent['intent']} (Score: {score:.2f})")
            print("Bot:", recognizer.get_response(intent))
        else:
            print("Bot: I did not understand that.")
