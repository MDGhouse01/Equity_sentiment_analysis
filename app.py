from flask import Flask, request, jsonify, render_template
import requests
import asyncio
from twikit import Client, TooManyRequests
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from scipy.special import softmax

app = Flask(__name__)

# Constants
API_KEY = 'cqo9k8pr01qo8865piggcqo9k8pr01qo8865pih0'
cookies_file_path = r'converted_cookies.json'
roberta = "cardiffnlp/twitter-roberta-base-sentiment"

# Load the sentiment analysis model and tokenizer
model = AutoModelForSequenceClassification.from_pretrained(roberta)
tokenizer = AutoTokenizer.from_pretrained(roberta)
labels = ['Negative', 'Neutral', 'Positive']

# Function to analyze sentiment of a tweet
def analyze_sentiment(tweet):
    tweet_words = []
    for word in tweet.split(' '):
        if word.startswith('@') and len(word) > 1:
            word = '@user'
        elif word.startswith('http'):
            word = "http"
        tweet_words.append(word)
    
    tweet_proc = " ".join(tweet_words)

    encoded_tweet = tokenizer(tweet_proc, return_tensors='pt')
    output = model(**encoded_tweet)
    scores = output[0][0].detach().numpy()
    scores = softmax(scores)
    
    return scores

# Function to fetch tweets asynchronously
async def fetch_tweets(query):
    client = Client(language='en-US')
    all_tweets = []
    
    try:
        client.load_cookies(cookies_file_path)  # Load cookies
        tweets = await client.search_tweet(query, product='top')
        
        for tweet in tweets:
            all_tweets.append(tweet)
    
    except TooManyRequests:
        print("Too many requests. Please wait and try again.")
    except Exception as e:
        print(f"An error occurred: {e}")
    
    return all_tweets

# Home page
@app.route('/')
def index():
    return render_template('index.html')

# API route to fetch tweets and sentiment analysis
@app.route('/api/tweets')
def tweets(): 
    # Use the query parameter from the request, default to 'AAPL'
    symbol = request.args.get('symbol', 'aapl')
    fetched_tweets = asyncio.run(fetch_tweets(symbol))
    sentiment_scores = {'Negative': 0, 'Neutral': 0, 'Positive': 0}
    
    for tweet in fetched_tweets:
        tweet_text = tweet.text if hasattr(tweet, 'text') else None
        if tweet_text:
            scores = analyze_sentiment(tweet_text)
            sentiment_scores['Negative'] += scores[0]
            sentiment_scores['Neutral'] += scores[1]
            sentiment_scores['Positive'] += scores[2]

    return jsonify({
        'tweets': [{'text': tweet.text} for tweet in fetched_tweets],
        'sentiment_scores': sentiment_scores
    })

# API route to fetch stock information
@app.route('/get_stock_info')
def get_stock_info():
    symbol = request.args.get('symbol')
    url = f'https://finnhub.io/api/v1/quote?symbol={symbol}&token={API_KEY}'

    try:
        response = requests.get(url)
        data = response.json()

        if 'c' in data:
            stock_info = {
                'symbol': symbol.upper(),
                'price': data['c'],
                'open': data['o'],
                'high': data['h'],
                'low': data['l'],
                'prevClose': data['pc']
            }
            return jsonify(stock_info) 
        else:
            return jsonify({'error': 'Invalid symbol or no data available'})

    except Exception as e:
        return jsonify({'error': str(e)})

# Sentiment analysis page
@app.route('/sentiment_analysis/<symbol>')
def sentiment_analysis(symbol):
    # Use the symbol passed from the URL for fetching tweets
    fetched_tweets = asyncio.run(fetch_tweets(symbol))
    sentiment_scores = {'Negative': 0, 'Neutral': 0, 'Positive': 0}

    for tweet in fetched_tweets:
        tweet_text = tweet.text if hasattr(tweet, 'text') else None
        if tweet_text:
            scores = analyze_sentiment(tweet_text)
            sentiment_scores['Negative'] += scores[0]
            sentiment_scores['Neutral'] += scores[1]
            sentiment_scores['Positive'] += scores[2]

    app.logger.info("Sentiment analysis completed for symbol: %s", symbol)

    return render_template('sentiment.html', query=symbol, sentiment_scores=sentiment_scores, tweets=fetched_tweets)

if __name__ == "__main__":
    app.run(debug=True)
