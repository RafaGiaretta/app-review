import openai
import json
from config import OPENAI_KEY

openai.api_key = OPENAI_KEY


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