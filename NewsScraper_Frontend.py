from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = FastAPI()

CATEGORIES = {
    "pharma": f"https://the-elpazzu-post-backend.onrender.com/news/biopharma",
    "ai": f"https://the-elpazzu-post-backend.onrender.com/news/ai",
    "invest": f"https://the-elpazzu-post-backend.onrender.com/news/investments",
    "world": f"https://the-elpazzu-post-backend.onrender.com/news/world",
    "lebanon": f"https://the-elpazzu-post-backend.onrender.com/news/lebanon"
}

@app.get("/", response_class=HTMLResponse)
def serve_react():
    categories_json = str(CATEGORIES).replace("'", '"')
    return HTMLResponse(content=f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>The Elpazzu Post</title>
        <style>
            body {{ font-family: Arial, sans-serif; background-color: #121212; color: #E0E0E0; margin: 0; padding: 20px; }}
            .container {{ max-width: 800px; margin: auto; background: #1E1E1E; padding: 20px; border-radius: 10px; }}
            h1 {{ text-align: center; color: #BB86FC; }}
            .menu {{ display: flex; justify-content: center; gap: 15px; margin-bottom: 20px; }}
            .menu button {{ background: #BB86FC; color: white; border: none; padding: 10px; cursor: pointer; border-radius: 5px; }}
            .menu button:hover {{ background: #9a67ea; }}
            .articles {{ display: flex; flex-direction: column; gap: 20px; }}
            .article-card {{ background: #2C2C2C; padding: 15px; border-radius: 8px; position: relative; min-height: 100px; 
                             display: flex; flex-direction: column; justify-content: space-between; }}
            .article-card.read {{ opacity: 0.5; }}
            .article-card h2 {{ font-size: 18px; margin: 0; padding-right: 70px; word-wrap: break-word; }}
            .article-card a {{ color: #03DAC6; text-decoration: none; }}
            .published-date {{ font-size: 12px; color: #999; }}
            .summary {{ font-size: 14px; color: #E0E0E0; }}
            .mark-read {{ position: absolute; top: 10px; right: 10px; cursor: pointer; background: #BB86FC; color: white; border: none; padding: 5px 10px; border-radius: 5px; 
                          font-size: 12px; white-space: nowrap; }}
            .notice-box {{ position: fixed; top: 20px; left: 50%; transform: translateX(-50%); background: #BB86FC; color: white; padding: 15px; border-radius: 8px;
                           box-shadow: 0px 0px 10px rgba(0, 0, 0, 0.3); text-align: center; max-width: 600px; z-index: 1000; }}
            .notice-box button {{ margin-top: 10px; background: #1E1E1E; color: white; border: none; padding: 5px 10px; cursor: pointer; border-radius: 5px; }}
            .notice-box button:hover {{ background: #121212; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>📰 The Elpazzu Post</h1>
            <div id="notice-box" class="notice-box">
                <p>
                    This is a personalized journal that is not meant for wide use. 
                    If you are not Elpazzu himself, you've got no business here.
                </p>
                <button onclick="closeNotice()">Got it</button>
            </div>
            <div class="menu" id="menu-bar"></div>
            <div id="news-container">Loading news...</div>
        </div>

        <script>
            const CATEGORIES = {categories_json};
            let currentCategory = Object.keys(CATEGORIES)[0];

            function getReadArticles() {{
                return JSON.parse(localStorage.getItem("readArticles")) || [];
            }}

            function toggleRead(articleId, button) {{
                let readArticles = getReadArticles();
                if (readArticles.includes(articleId)) {{
                    readArticles = readArticles.filter(id => id !== articleId);
                    button.textContent = "Mark Done";
                }} else {{
                    readArticles.push(articleId);
                    button.textContent = "✅ Done";
                }}
                localStorage.setItem("readArticles", JSON.stringify(readArticles));
                document.getElementById(articleId).classList.toggle("read");
            }}

            function loadMenu() {{
                let menuBar = document.getElementById("menu-bar");
                menuBar.innerHTML = "";
                Object.keys(CATEGORIES).forEach(category => {{
                    let button = document.createElement("button");
                    button.textContent = category.toUpperCase();
                    button.onclick = () => loadNews(category);
                    menuBar.appendChild(button);
                }});
            }}

            async function loadNews(category) {{
                currentCategory = category;
                let container = document.getElementById("news-container");
                container.innerHTML = "<p>Loading news...</p>";
                let apiUrl = CATEGORIES[category];
                let readArticles = await getReadArticles();
                readArticles = readArticles || [];

                try {{
                    let response = await fetch(apiUrl);
                    let data = await response.json();
                    let articles = data.articles.sort((a, b) => new Date(b.published) - new Date(a.published));
                    
                    container.innerHTML = articles.map(article => {{
                        let articleId = btoa(article.link);
                        let isRead = Array.isArray(readArticles) && readArticles.includes(articleId);
                        return `
                            <div id="${{articleId}}" class="article-card ${{isRead ? 'read' : ''}}">
                                <h2><a href="${{article.link}}" target="_blank">${{article.title}}</a></h2>
                                <p class="domain">🌐 ${{article.domain}}</p>
                                <p class="published-date">📅 ${{article.published}}</p>
                                <p class="summary">${{article.summary}}</p>
                                <button class="mark-read" onclick="toggleRead('${{articleId}}', this)">
                                    ${{ isRead ? '✅ Done' : 'Mark Done' }}
                                </button>
                            </div>`;
                    }}).join("");
                }} catch (error) {{
                    console.error("Error fetching news:", error);
                    container.innerHTML = "<p>Error loading news.</p>";
                }}
            }}

            function closeNotice() {{
                document.getElementById("notice-box").style.display = "none";
                localStorage.setItem("noticeDismissed", "true");
            }}

            window.onload = function () {{
                if (localStorage.getItem("noticeDismissed") === "true") {{
                    document.getElementById("notice-box").style.display = "none";
                }}
            }};
            
            loadMenu();
            loadNews(currentCategory);
        </script>
    </body>
    </html>
    """)
