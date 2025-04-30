import pandas as pd
import openai, json, os, re

from serpapi import GoogleSearch
from datetime import datetime
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv()

serpapi_key = os.getenv("SerpApi_Key")
openai.api_key = os.getenv("GPT_Key")

reviews = []

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
                "api_key": serpapi_key
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
    
def processar_apple(apple_id: int,  nome_app: str) -> pd.DataFrame:
    params = {
        "engine": "apple_reviews",
        "api_key": serpapi_key,
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

def processar_google(google_id: str, nome_app: str) -> pd.DataFrame:
    params = {
        "engine": "google_play_product",
        "api_key": serpapi_key,
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

def analisar_sentimento(texto: str) -> str:
    try:
        resp = openai.chat.completions.create(
            model="gpt-4.1-mini",
            temperature=0.0,
            messages=[
                {"role": "system",  "content": "Você é um assistente de análise de sentimento. Responda somente com Positivo, Negativo ou Neutro."},
                {"role": "user",    "content": texto}
            ]
        )
        label = resp.choices[0].message.content.strip().lower()
        if 'neg' in label:
            return 'Negativo'
        if 'pos' in label:
            return 'Positivo'
        return 'Neutro'
    except Exception as e:
        print(f"Erro na análise de sentimento: {e}")
        return 'Não identificado'

def gerar_resumo(texto: str) -> list:
    instrucao_resumo = (
        """
            Você é um agente de análise de feedback de usuários.  
            Receberá um texto contendo avaliações de um aplicativo, no seguinte formato (colunas):  
            -app_name,
            -author_name,
            -rating
            -text
            -review_date
            -store
            -sentimento

            Sua tarefa é:

            1. Analisar todo o texto das avaliações e gerar um **resumo consolidado**, estruturado em tópicos:
            - **Tópicos Positivos**  
                - **Desempenho e Utilidade**: o que os usuários elogiam em termos de rapidez, estabilidade e funcionalidades.
            - **Tópicos Negativos**  
                - **Atendimento ao Cliente**: menções a suporte, tempo de resposta, cordialidade, etc.  
                - **Experiência do Usuário**: menções à interface, usabilidade, layout, bugs de navegação, etc.  
            - **Outros Tópicos Relevantes**: identifique qualquer outro tema que apareça com destaque (por exemplo: preço, integrações, privacidade, notificações).
            - **Total de cada sentimento**: some a quantidade de cada sentimento.
            
            2. Para cada um dos tópicos acima, apresente:
            - Uma breve síntese (3–5 frases) do que os usuários estão dizendo.
            - Se possível, menção ao sentimento predominante (positivo, negativo, neutro).

            3. **Ao final**, forneça **duas avaliações de exemplo** (texto completo da coluna text, e rating) que ilustrem fortemente cada tópico listado, indicando de qual tópico cada exemplo trata.

            4. Forneça uma lista de registros no seguinte formato, um por linha/tópico:
            - tópico (aplicativo, positivos, negativos, experiencia do usuario e outros topicos relevantes encontrados)
            - Nome_App
            - Sintese
            - Autor_1
            - Rating
            - Texto
            - Data
            - Autor_2       
            - Rating
            - Texto
            - Data
            - Positivo
            - Negativo
            - Neutro

            Retorne essa lista em formato JSON , por exemplo:
            [
                {
                "App" : "Nome do Aplicativo"
                "Topico": "Topicos Positivos",
                "Sintese": "Usuários elogiam a rapidez e a estabilidade do app.",
                "Autor": "João",
                "Rating": 5,
                "Review_ex": "App super rápido e estável!",
                "Autor: "Maria",
                "Rating": 4,
                "Review_ex": "Funcionalidades muito úteis, parabéns!",
                "Positivos" : 15,
                "Negativos" : 40,
                "Neutro" : 20

            },
            ...
            ]
    """
    )
    resp = openai.chat.completions.create(
        model="gpt-4.1-mini",
        temperature=0.0,
        messages=[
            {"role": "system", "content": instrucao_resumo},
            {"role": "user",   "content": texto}
        ]
    )
    return json.loads(resp.choices[0].message.content)

def comparar_sugerir(texto: str, cliente: str) -> str:
    try:
        instrucao = f"""
            Você é um agente especializado em análise de feedback de usuários. Sua tarefa é:
            - Ler e processar avaliações de aplicativos concorrentes contidas em:
            {texto}
            - Identificar pontos elogiados e críticas recorrentes.
            - Comparar esses pontos com as características atuais do aplicativo do cliente "{cliente}", destacando:
            * Onde o app já se destaca.
            * Oportunidades de melhoria.
            * Lacunas a serem resolvidas.

            Sugira melhorias prioritárias, focando em:
            - Soluções práticas para problemas comuns.
            - Inovações inspiradas em elogios dos concorrentes.
            - Diferenciais competitivos.
            
            Retorne o resultado em formato JSON como uma **lista de objetos**
            Exemplo de retorno: 
                
                    "Categoria": "Otimização de Performance",
                    "Sugestão": "Reduzir travamentos e lentidão, especialmente após atualizações, citados em várias análises concorrentes."
                ,
                
                    "Categoria": "Atendimento ao Cliente",
                    "Sugestão": "Melhorar a eficácia do suporte ao cliente, com respostas mais rápidas e resolutivas, evitando respostas automáticas e demoras."
                

        """

        resp = openai.chat.completions.create(
            model="gpt-4.1-mini",
            temperature=0.3,
            messages=[
                {"role": "system",  "content": "Você é um agente de análise estratégica."},
                {"role": "user",    "content": instrucao},
            ]
        )
        return resp.choices[0].message.content.strip()
    except Exception as e:
        print(f"Erro ao comparar: {e}")
        
if __name__ == '__main__': 
    
    # Entradas     
    print('Entre com o nome do cliente: ')
    cliente = input()
    print('Entre com as empresas concorrente que deseja pesquisar (separadas por virgula): ')
    entrada_empresas = input()    
    lista_empresas = [e.strip() for e in entrada_empresas.split(',') + [cliente]]      
    print(lista_empresas)
      
    # Limite inferior de data
    print('Entre com a data (formato: AAAA-MM-DD):')
    entrada = input()
    limite_inferior = datetime.strptime(entrada, '%Y-%m-%d')
    print(limite_inferior)
    
    # Buscando IDs 
    apps = app_mapping(lista_empresas)
    print(apps)
    
    for nome_app, ids in apps.items():
        print(f"Processando {nome_app}...")
        df_apple = processar_apple(ids['apple_id'], nome_app)
        df_google = processar_google(ids['google_id'], nome_app)

        # Analisar sentimento
        df_all = pd.concat([df_apple, df_google], ignore_index=True)
        df_all['sentimento'] = df_all['text'].apply(analisar_sentimento)    
        df_all['review_date'] = df_all['review_date'].dt.strftime('%Y-%m-%d') # Tratando data (dando dump)
        
        # Add na lista reviews
        reviews.extend(df_all.to_dict('records'))     
        
    #print(reviews)
    
    # Gerar resumo
    review_json = json.dumps(reviews, ensure_ascii=False)
    dados_resumo = gerar_resumo(review_json)  
    
    #print(dados_resumo)
    
    # Comparar e sugerir        
    final = comparar_sugerir(dados_resumo, cliente)
    print(final)
    
    