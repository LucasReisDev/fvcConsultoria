from flask import Flask, render_template, redirect, url_for,request,jsonify
import requests
from pagseguro import PagSeguro
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///clientes.db'
db = SQLAlchemy(app)
pagseguro = PagSeguro(email='viccari215@gmail.com', token='B73EBD2ACECE64B2245D5FB20A5848C6')
migrate = Migrate(app, db)

class Cliente(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    cpf = db.Column(db.String(14), nullable=False)
    status_pagamento = db.Column(db.Boolean, default=False)  # Adicionado campo de status de pagamento

with app.app_context():
    db.create_all()

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        data = request.json
        nome = data.get('nome')
        email = data.get('email')
        cpf = data.get('cpf')

        novo_cliente = Cliente(nome=nome, email=email, cpf=cpf, status_pagamento=False)
        db.session.add(novo_cliente)
        db.session.commit()

        return redirect(url_for('pagamento'))
    
    return render_template('index.html')

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    # Recuperar os dados do cliente da query string
    nome_cliente = request.args.get('nome', '')
    email_cliente = request.args.get('email', '')
    cpf_cliente = request.args.get('cpf', '')

    # Renderizar a página admin com os dados do cliente
    return render_template('painel.html', nome=nome_cliente, email=email_cliente, cpf=cpf_cliente)

@app.route('/pagamento')
def pagamento():

    return render_template('pagamento.html') 

@app.route('/pagamento_credito', methods=['POST'])
def pagamento_credito():
    # Dados do cartão de crédito
    cartao_numero = request.form['cartao_numero']
    print(cartao_numero)
    cartao_mes = request.form['cartao_mes']
    print(cartao_mes)
    cartao_ano = request.form['cartao_ano']
    print(cartao_ano)
    cartao_cvv = request.form['cartao_cvv']
    print(cartao_cvv)

    # Configuração dos dados do pedido
    url_pagseguro = 'https://sandbox.pagseguro.uol.com.br'  # Substitua pela URL real da API do PagSeguro
    valor_a_cobrar = 24,99

    headers = {
        'Authorization': f'Bearer EB0181986A27440FAB1822445585C884',
        'Content-Type': 'application/json'
    }

    payload = {
        'cardNumber': cartao_numero,
        'expMonth': cartao_mes,
        'expYear': cartao_ano,
        'securityCode': cartao_cvv,
        'value':valor_a_cobrar,
        # Mais detalhes do pedido aqui, dependendo da API do PagSeguro
    }

    # Realiza a requisição POST para realizar o pagamento
    response = requests.post(url_pagseguro, json=payload, headers=headers)

    # Verifica a resposta da requisição
    if response.status_code == 200:
        return jsonify({'success': True, 'message': 'Pagamento realizado' })
    else:
        return jsonify({'success': False, 'message': 'Erro ao realizar o pagamento.'})
    

if __name__ == '__main__':
    app.run(debug=True)