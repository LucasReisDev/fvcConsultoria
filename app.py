from flask import Flask, render_template, redirect, request, jsonify
from flask_sqlalchemy import SQLAlchemy
# from pagseguro import PagSeguro
from flask_migrate import Migrate
import requests
import flask_mail

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///clientes.db'
db = SQLAlchemy(app)
# pagseguro = PagSeguro(email='viccari215@gmail.com',
# token='B73EBD2ACECE64B2245D5FB20A5848C6')
migrate = Migrate(app, db)


class Cliente(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    cpf = db.Column(db.String(14), nullable=False)
    status_pagamento = db.Column(db.Boolean, default=False)

# Criação do banco de dados fora do escopo da aplicação


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/cadastro', methods=['POST'])
def cadastro():
    data = request.json
    nome = data.get('nome')
    email = data.get('email')
    cpf = data.get('cpf')

    print(nome)
    print(email)
    print(cpf)

    novo_cliente = Cliente(
        nome=nome, email=email, cpf=cpf, status_pagamento=False)
    db.session.add(novo_cliente)
    db.session.commit()

    # # Redireciona para a rota de pagamento
    return redirect('/pagamento')


@app.route('/admin', methods=['GET'])
def admin():
    # Recuperar todos os clientes do banco de dados
    clientes = Cliente.query.all()

    # Renderizar a página admin com a lista de clientes
    return render_template('painel.html', clientes=clientes)


# Listar usuários
@app.route('/users', methods=['GET'])
def getUsers():
    allUsers = Cliente.query.all()

    serialized_users = []
    for user in allUsers:
        serialized_user = {
            'id': user.id,
            'nome': user.nome,
            'email': user.email,
            'cpf': user.cpf,
            'status_pagamento': user.status_pagamento
        }
        serialized_users.append(serialized_user)

    return serialized_users


# Deletar usuário
@app.route('/users/<cpf>', methods=['DELETE'])
def delete_user(cpf):
    # Procura o usuário pelo CPF
    user = Cliente.query.filter_by(cpf=cpf).first()

    if user:
        # Remove o usuário do banco de dados
        db.session.delete(user)
        db.session.commit()
        return jsonify({'message': f'Usuário com CPF {cpf} foi removido'})
    else:
        return jsonify({
            'message': f'Usuário com CPF {cpf} não encontrado'
        }), 404


@app.route('/pagamento')
def pagamento():
    return render_template('pagamento.html')


if __name__ == '__main__':
    app.run(debug=True)


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
    url_pagseguro = 'https://sandbox.pagseguro.uol.com.br'
    valor_a_cobrar = 24.99

    headers = {
        'Authorization': 'Bearer EB0181986A27440FAB1822445585C884',
        'Content-Type': 'application/json'
    }

    payload = {
        'cardNumber': cartao_numero,
        'expMonth': cartao_mes,
        'expYear': cartao_ano,
        'securityCode': cartao_cvv,
        'value': valor_a_cobrar,
        # Mais detalhes do pedido aqui, dependendo da API do PagSeguro
    }

    # Realiza a requisição POST para realizar o pagamento
    response = requests.post(url_pagseguro, json=payload, headers=headers)

    # Verifica a resposta da requisição
    if response.status_code == 200:
        return jsonify({'success': True, 'message': 'Pagamento realizado'})
    else:
        return jsonify({
            'success': False,
            'message': 'Erro ao realizar o pagamento.'
        })


if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)
