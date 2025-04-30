import openai
import json
from config import OPENAI_KEY

openai.api_key = OPENAI_KEY

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