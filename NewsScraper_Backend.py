from fastapi import FastAPI, HTTPException
import feedparser
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from newspaper import Article
import re
import warnings
from fastapi.middleware.cors import CORSMiddleware

warnings.filterwarnings("ignore")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

RSS_FEEDS = {
    "biopharma": {
        "feeds": {
            "https://www.fiercepharma.com/rss/xml": "Breaking news and insights from the pharma industry.",
            "https://www.pharmatimes.com/rss/news_rss.rss": "Industry trends, regulatory updates & patient perspectives.",
            "https://www.bioworld.com/rss/14": "Deals/M&As in Biotech & MedTech.",
            "https://www.bioworld.com/rss/5": "Artificial Intelligence in BioTech & MedTech."
        },
        "description": "Latest developments in the biopharma industry."
    },
    "ai": {
        "feeds": {
            "https://www.marktechpost.com/feed/": "Latest AI research, industry trends & applications.",
            "https://bair.berkeley.edu/blog/feed.xml": "Updates from Berkeley AI Research Lab.",
            "http://news.mit.edu/rss/topic/artificial-intelligence2": "MIT News Artificial Intelligence Blog.",
            "https://deepmind.com/blog/feed/basic/": "Groundbreaking research & innovations at the forefront of AI.",
            "https://www.unite.ai/feed/": "Articles, expert interviews & latest news on AI technologies.",
            "https://www.ft.com/companies/technology?format=rss": "News for Hardware, software, networking, and Internet media."
        },
        "description": "Artificial intelligence research and industry updates."
    },
    "investments": {
        "feeds": {
            "https://search.cnbc.com/rs/search/combinedcms/view.xml?partnerId=wrss01&id=100003114": "Latest financial market updates from CNBC.",
            "https://blogs.cfainstitute.org/investor/feed/": "Insightful & practical analysis for investment professionals.",
            "https://www.investmentwatchblog.com/feed/": "Analysis & insights on financial markets, politics, and global events.",
            "https://www.ft.com/global-economy?format=rss": "Coverage of global economic issues.",
            "https://www.ft.com/markets?format=rss": "Latest market trends and updates.",
            "https://techcrunch.com/feed/": "Focus on technology news, startups, and VCs."
        },
        "description": "Financial markets, investments, and economic news."
    },
    "world": {
        "feeds": {
            "http://feeds.bbci.co.uk/news/world/rss.xml": "Global headlines from BBC News.",
            "http://www.aljazeera.com/xml/rss/all.xml": "Global headlines from Al Jazeera.",
            "https://www.france24.com/en/rss": "Global headlines from France 24.",
            "https://www.ft.com/world?format=rss": "News, analysis, and comment from the Financial Times (business publication).",
            "https://www.euronews.com/rss?format=mrss&level=theme&name=news": "Global headlines from Euronews."
        },
        "description": "Global news and international affairs."
    },
    "lebanon": {
        "feeds": {
            "https://libnanews.com/feed/": "Political, economic, judicial, cultural & social news from Lebanon.",
            "https://www.ft.com/world/mideast?format=rss": "FT news specific to MENA region."
        },
        "description": "News and updates from Lebanon."
    },
    "belgium": {
        "feeds": {
            "https://www.thebulletin.be/rss.xml": "News & lifestyle updates for internationals in Belgium.",
            "https://brusselsmorning.com/feed/": "Politics, business & daily news from Brussels.",
            "https://www.lalibre.be/arc/outboundfeeds/rss/?outputType=xml": "General news & opinions from La Libre Belgique.",
            "https://www.lecho.be/rss/top_stories.xml": "Top financial & economic news from Belgium."
        },
        "description": "News and updates from Belgium."
    }
}

def fetch_news(category: str, max_articles: int = 8):
    if category not in RSS_FEEDS:
        raise HTTPException(status_code=404, detail=f"Category '{category}' not found.")
    
    month_pattern = re.compile(r"^(January|February|March|April|May|June|July|August|September|October|November|December)\b", re.IGNORECASE)
    ignore_pattern = re.compile(r"^(Latest news bulletin|Revue de presse du|#FierceMadness|Interview Series)$", re.IGNORECASE)
    
    articles = []
    for url, feed_desc in RSS_FEEDS[category]["feeds"].items():
        feed = feedparser.parse(url)
        valid_articles_count = 0
        
        for entry in feed.entries:
            if valid_articles_count >= max_articles:
                break
            
            title = entry.title
            link = entry.link
            domain = urlparse(link).netloc

            if ignore_pattern.match(entry.title):
                continue
            if category == "biopharma" and "/webinar/" in link:
                continue
            if "cafepharma.com" in url and month_pattern.match(entry.title):
                continue

            summary = clean_summary(entry.summary) if hasattr(entry, "summary") else extract_summary(link)
            published = entry.published if hasattr(entry, "published") else "Unknown"
            
            if not summary or len(summary) < 40:
                continue

            articles.append({
                "title": title,
                "link": link,
                "summary": summary[:1100] + "..." if len(summary) > 1100 else summary,
                "published": published,
                "feed_description": feed_desc,
                "domain": domain
            })
            valid_articles_count += 1
    
    return articles

def extract_summary(url):
    try:
        article = Article(url)
        article.download()
        article.parse()
        article.nlp()
        return article.summary[:300]
    except Exception:
        return "⚠️ Summary not available."

def clean_summary(summary):
    soup = BeautifulSoup(summary, "html.parser")
    text = soup.get_text(separator=" ", strip=True)
    remove_patterns = [
        r"Les articles publiés par Libnanews, le média citoyen du Liban",
        r"The post .*? appeared first on MarkTechPost",
        r"The post .*? appeared first on Unite.AI",
        r"Cet article .*? Citoyen du Liban",
        r"Landing Page Url .*? industry",
        r"Continue reading .*"
    ]
    for pattern in remove_patterns:
        text = re.sub(pattern, "", text, flags=re.DOTALL)
    return text.strip()

@app.get("/")
def home():
    return {"message": "This The Elpazzu Post API. By using /news/{category} you can read news in json format, but these are meant to be read on a separate custom UI."}

@app.get("/news/{category}")
def get_news(category: str, max_articles: int = 8):
    articles = fetch_news(category, max_articles)
    return {"category": category, "articles": articles}
