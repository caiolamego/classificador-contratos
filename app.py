import os
import re

import PyPDF2
from flask import Flask, jsonify, render_template, request, url_for
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Set the upload folder path
app.config['UPLOAD_FOLDER'] = os.path.join(os.getcwd(), 'uploads')

# Ensure the uploads folder exists
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

# Variável para armazenar as mensagens do chat
messages = []
recomendacoes = []

def identificar_clausulas_abusivas(texto):
    abusivas = []
    abusiva_padroes = [
        "renúncia a direitos",
        "obrigação excessiva",
        "desvantagem exagerada",
        "penalidades desproporcionais",
        "cláusula unilateral",
    ]
    for padrao in abusiva_padroes:
        if padrao in texto.lower():
            abusivas.append(padrao)
    return abusivas

def avaliar_contrato(contrato):

    # Verifica se a parte é um MEI (Microempreendedor Individual)
    if re.search(r'\b(MEI|Microempreendedor Individual)\b', contrato, re.IGNORECASE):
        recomendacoes.append("Identificado que uma das partes é um MEI. Recomenda-se garantir que o contrato não imponha obrigações desproporcionais, dado o porte da empresa. É importante tomar cuidado com as garantias exigidas pelo banco.")

    # Verifica se há presunção de hipossuficiência
    if re.search(r'\b(consumidor|parte hipossuficiente|pessoa física|pessoa natural)\b', contrato, re.IGNORECASE):
        recomendacoes.append("Foi identificada possível presunção de hipossuficiência. É importante assegurar que a parte hipossuficiente esteja protegida contra cláusulas desproporcionais. O consumidor comum deve se atentar com os termos pré-estabelecidas pelo banco.")

     # Verifica se a parte é Empresa de Grande Porte
    if re.search(r'\b(empresa de grande porte|empresa grande|grande|grandes empresas)\b', contrato, re.IGNORECASE):
        recomendacoes.append("Verificado que há uma empresa de grande porte. Neste caso a empresa corre um risco menor, dada sua capacidade econômica e de negociação. De qualquer forma, é importante que a empresa se atente à possíveis cláusulas de má-fé.")   

    # Verifica se a parte é Entidade Governamental ou Grande Organização Pública
    if re.search(r'\b(pública|governo|entidade|organização)\b', contrato, re.IGNORECASE):
        recomendacoes.append("Identificada Entidade Governamental ou Grande Organização Pública. Há uma hipótese grande de esta parte encontrar-se em posição superior ao banco, sendo inclusive motivo de disputa entre estas instituições. Entretanto, é importante atentar-se para questões políticas e transparência, uma vez que geralmente trata de contratos complexos")

    # Verifica se a parte é Pequena ou Média Empresa (PMEs)
    if re.search(r'\b(pequena|média|PME)\b', contrato, re.IGNORECASE):
        recomendacoes.append("Embora a Pequena ou Média Empresa tenha mais capacidade que o MEI ou o Consumidor Comum ainda há um risco considerável perante o banco.")

    # Verifica se o contrato impõe prazos que podem ser desvantajosos
    if re.search(r'\b(prazo|tempo|período)\b', contrato, re.IGNORECASE):
        recomendacoes.append("Cláusulas de prazo foram encontradas. Assegure-se de que os prazos não sejam excessivamente curtos ou longos, impondo desvantagens a uma das partes.")

    # Caso nenhuma recomendação seja encontrada
    if not recomendacoes:
        recomendacoes.append("Nenhuma disparidade óbvia foi identificada, mas uma revisão detalhada é recomendada.")

    return recomendacoes

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/botContrato')
def botContrato():
    return render_template('botContrato.html', messages=messages)

@app.route('/botDisparidade')
def botDisparidade():
    return render_template('botDisparidade.html')

@app.route('/send_message', methods=['POST'])
def send_message():
    user_message = request.form['message']
    messages.append({'sender': 'user', 'text': user_message})

    # Processar a mensagem do usuário
    #abusivas = avaliar_contrato(user_message)
    bot_response = "Possíveis disparidades encontradas:\n" + '\n'.join(f"- {recomendacao}" for recomendacao in avaliar_contrato(user_message))
    # if abusivas:
    #     # Formata a lista de cláusulas abusivas com quebra de linha
    #     bot_response = "Possíveis disparidades encontradas:\n" + '\n'.join(f"- {recomendacao}" for recomendacao in recomendacoes)
    # else:
    #     bot_response = "Nenhuma cláusula abusiva identificada."

    messages.append({'sender': 'bot', 'text': bot_response})

    recomendacoes.clear()
    # Retorna a resposta como JSON para ser tratada pelo JavaScript
    return jsonify({'bot_response': bot_response})


def extrair_texto_arquivo(file_path):
    texto = ""
    if file_path.endswith('.txt'):
        with open(file_path, 'r', encoding='utf-8') as file:
            texto = file.read()
    elif file_path.endswith('.pdf'):
        with open(file_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            for page in reader.pages:
                texto += page.extract_text()
    return texto

@app.route('/botContrato', methods=['GET', 'POST'])
@app.route('/botContrato', methods=['GET', 'POST'])
def handle_botContrato():
    if request.method == 'POST':
        file = request.files['file']
        if file:
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            
            # Extrair texto do arquivo e identificar cláusulas abusivas
            texto = extrair_texto_arquivo(file_path)
            abusivas = identificar_clausulas_abusivas(texto)
            
            if abusivas:
                # Cria uma resposta formatada com tópicos
                abusivas_list = '\n'.join(f'- {abusiva}' for abusiva in abusivas)
                bot_response = f"Cláusulas abusivas encontradas:\n{abusivas_list}"
            else:
                bot_response = "Nenhuma cláusula abusiva identificada."
            
            # Remover o arquivo após o processamento
            os.remove(file_path)
            
            return jsonify({'bot_response': bot_response})

    return render_template('botContrato.html')

if __name__ == '__main__':
    app.run(debug=True, port=5001)

