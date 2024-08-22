from flask import Flask, jsonify, render_template, request, url_for

app = Flask(__name__)

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

if __name__ == '__main__':
    app.run(debug=True, port=5001)

