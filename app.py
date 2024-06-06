# Import libraries
from flask import Flask, render_template, request
from newsapi import NewsApiClient
import os


# Initialize Flask app
app = Flask(__name__)

# Initialize news API client
newsapi = NewsApiClient(api_key='6e648238a4c743b7bdaf2892f04d8101')

# Helper function to get sources and domains
def get_sources_and_domains(limit=10):
    all_sources = newsapi.get_sources()['sources']
    sources = []
    domains = []
    for e in all_sources[:limit]:
        id = e['id']
        domain = e['url'].replace("http://", "")
        domain = domain.replace("https://", "")
        domain = domain.replace("www.", "")
        slash = domain.find('/')
        if slash != -1:
            domain = domain[:slash]
        sources.append(id)
        domains.append(domain)
    sources = ", ".join(sources)
    domains = ", ".join(domains)
    return sources, domains

@app.route("/", methods=['GET', 'POST'])
def home():
    if request.method == "POST":
        sources, domains = get_sources_and_domains(limit=10)  # Limiting to 10 sources/domains
        keyword = request.form["keyword"]
        try:
            related_news = newsapi.get_everything(q=keyword,
                                                  sources=sources,
                                                  domains=domains,
                                                  language='en',
                                                  sort_by='relevancy')
            no_of_articles = related_news.get('totalResults', 0)
            if no_of_articles > 100:
                no_of_articles = 100
            all_articles = newsapi.get_everything(q=keyword,
                                                  sources=sources,
                                                  domains=domains,
                                                  language='en',
                                                  sort_by='relevancy',
                                                  page_size=no_of_articles).get('articles', [])
            return render_template("index.html", all_articles=all_articles, keyword=keyword)
        except NewsAPIException as e:
            error_message = e.get_message()
            return render_template("index.html", error=error_message)
    else:
        try:
            top_headlines = newsapi.get_top_headlines(country="in", language="en")
            total_results = top_headlines.get('totalResults', 0)
            if total_results > 100:
                total_results = 100
            all_headlines = newsapi.get_top_headlines(country="in",
                                                      language="en",
                                                      page_size=total_results).get('articles', [])
            return render_template("index.html", all_headlines=all_headlines)
        except NewsAPIException as e:
            error_message = e.get_message()
            return render_template("index.html", error=error_message)
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))

