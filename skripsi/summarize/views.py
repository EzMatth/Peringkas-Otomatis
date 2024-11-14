import requests
from django.shortcuts import render
from bs4 import BeautifulSoup
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from django.views.decorators.csrf import csrf_exempt
import nltk
import logging

# Tambahkan ini di bagian atas file
logger = logging.getLogger(__name__)

nltk.download('punkt')
SUGGESTED_LINKS = [
    "https://liputankawanua.com/",
    "https://kanalmetro.com/",
]
@csrf_exempt
def summarize_url(request):
    if request.method == 'POST':
        url = request.POST.get('url')
        if url:
            result = summarize_from_url(url)
            if 'error' in result:
                return render(request, 'new.html', {'error': result['error'], 'suggested_links': SUGGESTED_LINKS})
            return render(request, 'summary.html', {'summary': result['summary']})
        return render(request, 'new.html', {'error': 'No URL provided', 'suggested_links': SUGGESTED_LINKS})
    return render(request, 'new.html')

def extract_content_from_html(html):
    soup = BeautifulSoup(html, 'html.parser')
    paragraphs = soup.find_all('p')
    content = ' '.join([p.get_text() for p in paragraphs])
    
    if not content:
        return None, None, None

    author = soup.find(attrs={"name": "author"})
    author = author['content'] if author else "Unknown author"
    
    publication_date = soup.find(attrs={"name": "date"})
    publication_date = publication_date['content'] if publication_date else "Unknown date"

    return content, author, publication_date

def summarize_text_with_kmeans(text, num_clusters=5):
    sentences = nltk.sent_tokenize(text)
    vectorizer = TfidfVectorizer(stop_words='english')
    X = vectorizer.fit_transform(sentences)

    kmeans = KMeans(n_clusters=num_clusters, random_state=0).fit(X)
    clusters = kmeans.labels_

    clustered_sentences = {}
    for i, label in enumerate(clusters):
        if label not in clustered_sentences:
            clustered_sentences[label] = []
        clustered_sentences[label].append(sentences[i])

    summaries = []
    for cluster_id in range(num_clusters):
        if cluster_id in clustered_sentences:
            longest_sentence = max(clustered_sentences[cluster_id], key=len)
            summaries.append(longest_sentence)

    return summaries

def summarize_from_url(request):
    if request.method == 'POST':
        url = request.POST.get('url_input')
        try:
            response = requests.get(url)
            response.raise_for_status()
            html = response.text
            content = extract_content_from_html(html)
            if not content:
                logger.error(f"Could not extract content from URL: {url}")
                context = {
                    'error': 'Konten tidak dapat diekstrak dari URL yang diberikan.',
                    'suggested_links': SUGGESTED_LINKS
                }
                return render(request, 'new.html', context)
            
            article_text, author, publication_date = content
            summary = summarize_text_with_kmeans(article_text)
            
            context = {
                'summaries': summary,
                'author': author,
                'publication_date': publication_date
            }
            return render(request, 'summary.html', context)
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching URL {url}: {str(e)}")
            context = {
                'error': 'Silahkan Mengambil URL yang lain, Link yang anda masukkan tidak bisa diproses karena permasalahan keamanan data.',
                'suggested_links': SUGGESTED_LINKS
            }
            return render(request, 'new.html', context)
    else:
        return render(request, 'new.html')