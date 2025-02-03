from flask import Flask, render_template, flash, Response, redirect, request, url_for
import sqlite3
from flask_sqlalchemy import SQLAlchemy
import json, os
from flask_login import LoginManager
from flask_login import UserMixin, login_user, logout_user, login_required
from flask_login import current_user


login_manager = LoginManager()
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__)
app.config['SECRET_KEY'] = "amparo1004"
login_manager.init_app(app)
login_manager.login_view = "index"  


app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(BASE_DIR, 'database.db')}"
db = SQLAlchemy()
db.init_app(app)

class Usuario(db.Model, UserMixin):
    __tablename__='usuario'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100))
    email = db.Column(db.String(150), unique=True)
    senha = db.Column(db.String(250))

class Cuidador(db.Model, UserMixin):
    __tablename__='cuidador'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100))
    email = db.Column(db.String(150), unique=True)
    senha = db.Column(db.String(250))

class PedidoDoacao(db.Model):
    __tablename__ = 'pedido_doacao'
    id = db.Column(db.Integer, primary_key=True)
    item = db.Column(db.String(100), nullable=False)
    descricao = db.Column(db.String(300), nullable=False)
    urgencia = db.Column(db.String(20), nullable=False)
    contato_info = db.Column(db.String(100), nullable=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id', ondelete='CASCADE'), nullable=False)
    usuario = db.relationship('Usuario', backref=db.backref('pedidos_doacao', lazy=True))


# with app.app_context():
#   db.drop_all()
#   db.create_all()
#   print("Tabelas criadas no banco de dados.")

# @login_manager.user_loader
# def load_user(user_id):
#     return Usuario.get(user_id)

@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id)) or Cuidador.query.get(int(user_id))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login')
def login():
    return render_template('login.html')

from flask_login import login_user

@app.route('/autenticar', methods=['POST'])
def autenticar():
    tipo = request.form['tipo']
    email = request.form['email']
    senha = request.form['senha']

    if tipo == '0':
        us = Usuario.query.filter_by(email=email).first()
    else:
        us = Cuidador.query.filter_by(email=email).first()

    if us is None or us.senha != senha:
        flash('Login ou senha incorretos', 'danger')
        return redirect(url_for('login'))

    login_user(us)  
    flash('Logado com sucesso', 'success')
    return redirect(url_for('index'))


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Você saiu da conta.', 'info')
    return redirect(url_for('login'))

@app.route('/doacoes', methods=['GET', 'POST'])
@login_required
def doacoes():
    if request.method == 'POST':
        # Recebe os dados do formulário
        item = request.form['item']
        descricao = request.form['description']  # Corrigir nome do campo no formulário
        urgencia = request.form['urgency']      # Corrigir nome do campo no formulário
        contato_info = request.form['contact_info']  # Corrigir nome do campo no formulário
        usuario_id = current_user.id  # Usando o usuário autenticado

        # Cria o pedido de doação no banco de dados
        pedido = PedidoDoacao(item=item, descricao=descricao, urgencia=urgencia, contato_info=contato_info, usuario_id=usuario_id)
        db.session.add(pedido)
        db.session.commit()

        flash('Pedido de doação registrado com sucesso!', 'success')

    # Recupera todos os pedidos de doação do usuário atual
    pedidos = PedidoDoacao.query.filter_by(usuario_id=current_user.id).all()

    return render_template('doacoes.html', pedidos=pedidos)  # Retorna o template com os pedidos de doação

@app.route('/sobre')
def sobre():
    return render_template('sobre.html')


@app.route('/cadastro', methods=['POST', 'GET'])
def cadastro():
    if request.method == 'GET':
        return render_template('cadastro.html')
    
    if request.method=='POST':
        tipo = request.form['tipo']
        nome = request.form['nome']
        email = request.form['email']
        senha = request.form['senha'] 
        
        if tipo=='0':
            usuario = Usuario(nome = nome, email = email, senha = senha)
            db.session.add(usuario)
  
        if tipo=='1':
            cuidador = Cuidador(nome = nome, email = email, senha = senha)
            db.session.add(cuidador)

        db.session.commit()
            
        flash('Cadastrado com sucesso', 'success')
        return redirect(url_for('login'))
    
@app.route('/contato')
def contato():
    return render_template('contato.html')

@app.route('/faq')
def faq():
    return render_template('faq.html')

@app.route('/doencas')
def doecas():
    return render_template('doencas.html')

with app.app_context():
    db.create_all()
app.run(app)