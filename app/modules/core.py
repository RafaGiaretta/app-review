import json
import pandas as pd
from datetime import datetime

from app.modules.coleta import app_mapping, processar_apple, processar_google
from app.modules.sentimentos import analisar_sentimento, gerar_resumo
from app.modules.sugestoes import comparar_sugerir

def processar_empresas(cliente: str, concorrentes: list[str], data: str):
    lista_empresas = [e.strip() for e in concorrentes + [cliente]]
    limite_inferior = datetime.strptime(data, '%Y-%m-%d')

    apps = app_mapping(lista_empresas)
    reviews = []

    for nome_app, ids in apps.items():
        df_apple = processar_apple(ids['apple_id'], nome_app, limite_inferior)
        df_google = processar_google(ids['google_id'], nome_app, limite_inferior)

        df_all = pd.concat([df_apple, df_google], ignore_index=True)
        df_all['sentimento'] = df_all['text'].apply(analisar_sentimento)
        df_all['review_date'] = df_all['review_date'].dt.strftime('%Y-%m-%d')

        reviews.extend(df_all.to_dict('records'))

    review_json = json.dumps(reviews, ensure_ascii=False)
    dados_resumo = gerar_resumo(review_json)
    final = comparar_sugerir(dados_resumo, cliente)

    return json.loads(final)
