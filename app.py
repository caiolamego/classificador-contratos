import os

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
    abusivas = identificar_clausulas_abusivas(user_message)
    if abusivas:
        bot_response = f"Cláusulas abusivas encontradas: {', '.join(abusivas)}"
    else:
        bot_response = "Nenhuma cláusula abusiva identificada."

    messages.append({'sender': 'bot', 'text': bot_response})

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
                bot_response = f"Cláusulas abusivas encontradas: {', '.join(abusivas)}"
            else:
                bot_response = "Nenhuma cláusula abusiva identificada."
            
            # Remover o arquivo após o processamento
            os.remove(file_path)
            
            return jsonify({'bot_response': bot_response})

    return render_template('botContrato.html')

if __name__ == '__main__':
    app.run(debug=True, port=5001)

