import os
from flask import Flask, request, jsonify
from flask_cors import CORS
import openai
import json
from transcribe import download_video, transcribe_audio_portuguese
from dotenv import load_dotenv


# --- Configuração Inicial ---
# Crie uma variável de ambiente chamada 'OPENAI_API_KEY' com sua chave da OpenAI.
# Ou, para um teste rápido (não recomendado para produção), substitua pela sua chave:
# openai.api_key = "SUA_CHAVE_DE_API_AQUI"
load_dotenv()  # Carrega variáveis do arquivo .env
openai.api_key = os.getenv("OPENAI_API_KEY")

# Inicializa a aplicação Flask
app = Flask(__name__)
CORS(app)

# --- Lógica de Análise com a IA ---
def analisar_texto_com_ia(texto_transcrito: str) -> dict:
    """
    Envia o texto transcrito para a API da OpenAI para análise de fake news.
    """
    if not openai.api_key:
        return {
            "erro": "A chave da API da OpenAI não foi configurada. "
                    "Defina a variável de ambiente OPENAI_API_KEY."
        }

    # O prompt é a instrução que damos ao modelo.
    # Ele define o papel do modelo (um checador de fatos) e o que esperamos como resposta.
    prompt_sistema = """
    Você é um assistente especializado em identificar características de fake news em textos.
    Analise o texto fornecido e avalie os seguintes critérios:
    1.  **Ausência de Fontes:** O texto cita fontes de dados, especialistas ou estudos? Se sim, são fontes verificáveis ou genéricas (ex: "cientistas dizem")?
    2.  **Linguagem de Alta Convicção:** O texto usa uma linguagem excessivamente emotiva, categórica ou alarmista (ex: "com certeza", "sem dúvida", "é um absurdo")?
    3.  **Viés Político Forte:** O texto demonstra um posicionamento político claro e parcial, atacando ou defendendo um lado específico sem apresentar contrapontos?

    Responda em português e formate a saída como um objeto JSON com as seguintes chaves:
    -   "potencial_fake_news": (booleano, true se houver alta probabilidade, false caso contrário)
    -   "pontuacao_confianca": (um float de 0.0 a 1.0, indicando o nível de confiança na análise, onde 0.0 é nenhuma confiança e 1.0 é total confiança)
    -   "analise_fontes": (uma string com sua análise sobre as fontes)
    -   "analise_linguagem": (uma string com sua análise sobre a linguagem)
    -   "analise_vies": (uma string com sua análise sobre o viés político)
    -   "resumo": (uma string com um resumo conclusivo da sua análise)
    """

    try:
        # Fazendo a chamada para a API do ChatGPT
        completion = openai.chat.completions.create(
            model="gpt-4o-mini",  # Você pode usar "gpt-3.5-turbo" para uma opção mais rápida e barata
            messages=[
                {"role": "system", "content": prompt_sistema},
                {"role": "user", "content": texto_transcrito}
            ],
            # Garante que a resposta da API será um objeto JSON válido
            response_format={"type": "json_object"}
        )
        
        # Extrai e carrega a resposta JSON do modelo
        resposta_json = completion.choices[0].message.content
        return json.loads(resposta_json)

    except openai.APIError as e:
        print(f"Erro na API da OpenAI: {e}")
        return {"erro": f"Ocorreu um erro ao se comunicar com a API da OpenAI: {e}"}
    except Exception as e:
        print(f"Um erro inesperado ocorreu: {e}")
        return {"erro": f"Ocorreu um erro inesperado durante a análise: {e}"}


# --- Endpoint da API ---
@app.route('/analiser', methods=['POST'])
def endpoint_analisar():
    """
    Endpoint que recebe o JSON com o texto transcrito ou link do vídeo e retorna a análise.
    """
    dados = request.get_json()

    # Se receber um link de vídeo, faz o download e transcrição
    if dados and 'video_url' in dados:
        video_url = dados['video_url']
        # Baixa o vídeo e transcreve
        mp3_filename = download_video(video_url)
        texto = transcribe_audio_portuguese(mp3_filename)
    elif dados and 'texto_transcrito' in dados:
        texto = dados['texto_transcrito']
    else:
        return jsonify({"erro": "JSON inválido. É obrigatório fornecer 'texto_transcrito' ou 'video_url'."}), 400

    if not texto or not texto.strip():
        return jsonify({"erro": "O valor de 'texto_transcrito' não pode ser vazio."}), 400

    print(f"Recebido para análise: {texto[:100]}...")
    resultado_analise = analisar_texto_com_ia(texto)

    if "erro" in resultado_analise:
        return jsonify(resultado_analise), 500

    print("Análise concluída com sucesso.")
    return jsonify(resultado_analise), 200
# ...existing cod


# --- Execução da Aplicação ---
if __name__ == '__main__':
    # A aplicação rodará em http://127.0.0.1:5000
    # O modo debug permite que as alterações no código reiniciem o servidor automaticamente
    app.run(debug=True, port=5000)