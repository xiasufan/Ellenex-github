from flask import Flask, request, jsonify
from bs4 import BeautifulSoup
import requests
import re
from transformers import BertTokenizer, BertModel, pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from flask_cors import CORS
import torch

app = Flask(__name__)
CORS(app)  # 启用CORS支持

# 加载BERT模型和分词器
tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
model = BertModel.from_pretrained('bert-base-uncased')

def get_website_text(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching the URL: {e}")
        return None

    soup = BeautifulSoup(response.content, 'html.parser')
    texts = soup.stripped_strings
    content = ' '.join(texts)
    content = re.sub(r'[^A-Za-z\s]+', ' ', content)
    return content

def analyze_website_content(content):
    summarizer = pipeline("summarization", model="sshleifer/distilbart-cnn-12-6")
    summary = summarizer(content, max_length=130, min_length=30, do_sample=False)
    return summary[0]['summary_text']

def get_embedding(text):
    inputs = tokenizer(text, return_tensors='pt', truncation=True, padding=True, max_length=512)
    with torch.no_grad():
        outputs = model(**inputs)
    return outputs.last_hidden_state.mean(dim=1)

def calculate_similarity_bert(summary, keyword):
    summary_embedding = get_embedding(summary)
    keyword_embedding = get_embedding(keyword)
    cosine_sim = torch.nn.functional.cosine_similarity(summary_embedding, keyword_embedding)
    return cosine_sim.item() * 100

@app.route('/analyze', methods=['POST'])
def analyze():
    data = request.json
    url = data.get('url')
    keyword = data.get('keyword')
    if not url or not keyword:
        return jsonify({"error": "URL and keyword are required"}), 400

    content = get_website_text(url)
    if content is None:
        return jsonify({"error": "Failed to retrieve website content"}), 500

    summary = analyze_website_content(content)
    similarity = calculate_similarity_bert(summary, keyword)

    return jsonify({"summary": summary, "similarity": similarity})

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
