import pandas as pd
from datetime import datetime
from serpapi import GoogleSearch
import re
from config import SERPAPI_KEY

# Mapeamento de aplicativos
def app_mapping(empresas: list) -> dict:    
    resultado = {}
    print('Buscando IDs')
    try:
        for emp in empresas:
            app_mapping = {
                "google_id": None,
                "apple_id": None
            }
            # Google Play
            params = {
                "engine": "google",
                "q": emp + " google play",
                "api_key": SERPAPI_KEY
            }
            search = GoogleSearch(params)
            results = search.get_dict()
            organic_results = results.get("organic_results", [])

            for result in organic_results:
                link = result.get("link", "")
                if "play.google.com" in link and "details?id=" in link:
                    match = re.search(r"id=([\w\.]+)", link)
                    if match:
                        app_mapping["google_id"] = match.group(1)
                        break
            # Apple
            params["q"] = emp + " apple store"
            search = GoogleSearch(params)
            results = search.get_dict()
            organic_results = results.get("organic_results", [])

            for result in organic_results:
                link = result.get("link", "")
                if "apps.apple.com" in link:
                    match = re.search(r"/id(\d+)", link)
                    if match:
                        app_mapping["apple_id"] = int(match.group(1))
                        break

            resultado[emp] = app_mapping
        return resultado

    except Exception as e:
        print(f"Erro na busca do ID: {e}")
        return {"erro": str(e)}
    
def processar_apple(apple_id: int,  nome_app: str, limite_inferior: datetime) -> pd.DataFrame:
    params = {
        "engine": "apple_reviews",
        "api_key": SERPAPI_KEY,
        "product_id": apple_id,
        "country": "br",
        "sort": "mostrecent",
        "output": "json"
    }
    results = GoogleSearch(params).get_dict()
    reviews = results.get("reviews", [])
    df = pd.DataFrame(reviews)
    df['app_name'] = nome_app
    df['author_name'] = df['author'].apply(lambda x: x.get('name') if isinstance(x, dict) else None)
    df['review_date'] = pd.to_datetime(df['review_date'], format='%d/%m/%Y', errors='coerce')
    df['store'] = 'Apple Store'
    return df[df['review_date'] >= limite_inferior][['author_name', 'rating', 'text', 'review_date', 'store']]

def processar_google(google_id: str, nome_app: str, limite_inferior: datetime) -> pd.DataFrame:
    params = {
        "engine": "google_play_product",
        "api_key": SERPAPI_KEY,
        "store": "apps",
        "gl": "br",
        "product_id": google_id,
        "all_reviews": "true",
        "hl": "pt"
    }
    results = GoogleSearch(params).get_dict()
    reviews = results.get("reviews", [])

    processed = []
    for review in reviews:
        try:
            date_str = datetime.strptime(review['date'], "%B %d, %Y").strftime("%Y-%m-%d")
        except Exception:
            date_str = None
        processed.append({
            'app_name' : nome_app,
            'author_name': review.get('title', 'Anônimo'),
            'rating': review.get('rating', 0),
            'text': review.get('snippet', ''),
            'review_date': pd.to_datetime(date_str),
            'store': 'Google Play'
        })
    df = pd.DataFrame(processed)
    return df[df['review_date'] >= limite_inferior]    
