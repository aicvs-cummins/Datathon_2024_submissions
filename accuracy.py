import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer
from nltk.stem import WordNetLemmatizer
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import re
import nltk
from sklearn.metrics import classification_report, accuracy_score, precision_score, recall_score, f1_score

nltk.download('punkt')
nltk.download('stopwords')
nltk.download('wordnet')
nltk.download('vader_lexicon')


def preprocess_text(text):
    # Convert text to lowercase
    text = text.lower()
    # Remove special characters, numbers, and extra spaces
    text = re.sub(r'[^a-zA-Z\s]', '', text)
    # Tokenize the text
    tokens = word_tokenize(text)
    # Remove stopwords
    stop_words = set(stopwords.words('english'))
    filtered_tokens = [word for word in tokens if word not in stop_words]
    # Initialize lemmatizer and stemmer
    lemmatizer = WordNetLemmatizer()
    stemmer = PorterStemmer()
    # Lemmatize and stem tokens
    lemmatized_tokens = [lemmatizer.lemmatize(word) for word in filtered_tokens]
    stemmed_tokens = [stemmer.stem(word) for word in lemmatized_tokens]
    # Join tokens back into a string
    preprocessed_text = ' '.join(stemmed_tokens)
    return preprocessed_text


# Text vectorization using TF-IDF
def vectorize_text(text_data):
    tfidf_vectorizer = TfidfVectorizer(max_features=5000)
    X_tfidf = tfidf_vectorizer.fit_transform(text_data)
    return X_tfidf, tfidf_vectorizer


# Function to predict complaint type
def predict_complaint_type(user_input, tfidf_vectorizer, classifier):
    preprocessed_input = preprocess_text(user_input)
    preprocessed_input_tfidf = tfidf_vectorizer.transform([preprocessed_input])
    prediction = classifier.predict(preprocessed_input_tfidf)
    return prediction[0]


# Function for sentiment analysis
def analyze_sentiment(text):
    sid = SentimentIntensityAnalyzer()
    compound_score = sid.polarity_scores(text)['compound']
    if compound_score >= 0.05:
        return 'Positive'
    elif compound_score <= -0.05:
        return 'Negative'
    else:
        return 'Neutral'


if __name__ == '__main__':
    # Load preprocessed data from CSV
    data = pd.read_csv("output.csv")  # Replace "output.csv" with your preprocessed CSV file path

    # Drop rows with missing values in 'preprocessed_text' column
    data = data.dropna(subset=['preprocessed_text'])

    # Vectorize preprocessed text
    X_tfidf, tfidf_vectorizer = vectorize_text(data['preprocessed_text'])

    # Initialize and train Random Forest classifier
    rf_classifier = RandomForestClassifier(n_estimators=100, random_state=42)
    rf_classifier.fit(X_tfidf, data['product'])

    X_test_tfidf = X_tfidf  # For simplicity, assuming all data is test data
    y_true = data['product']  # True labels

    while True:
        # Ask for user input
        user_input = input("Enter your complaint (or type '1' to stop): ")

        # Check if the user wants to stop
        if user_input == '1':
            print("Exiting...")
            break

        # Predict complaint type
        predicted_complaint_type = predict_complaint_type(user_input, tfidf_vectorizer, rf_classifier)

        # Perform sentiment analysis
        sentiment = analyze_sentiment(user_input)

        print("Predicted complaint type:", predicted_complaint_type)
        print("Sentiment:", sentiment)

        # Predictions
        y_pred = rf_classifier.predict(X_test_tfidf)

        # Calculate evaluation metrics
        accuracy = accuracy_score(y_true, y_pred)
        precision = precision_score(y_true, y_pred, average='weighted')
        recall = recall_score(y_true, y_pred, average='weighted')
        f1 = f1_score(y_true, y_pred, average='weighted')

        print("Accuracy:", accuracy)
        print("Precision:", precision)
        print("Recall:", recall)
        print("F1-score:", f1)

        # Detailed classification report
        print("Classification Report:")
        print(classification_report(y_true, y_pred))