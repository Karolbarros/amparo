from flask import Flask, render_template, flash, redirect, request, url_for, session 
from flask_sqlalchemy import SQLAlchemy
import os
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from functools import wraps
import re

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

@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id)) or Cuidador.query.get(int(user_id))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login')
def login():
    return render_template('login.html')

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
    session["user_role"] = "cuidador" if isinstance(us, Cuidador) else "usuario" 

    flash('Logado com sucesso', 'success')
    return redirect(url_for('index'))

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Você saiu da conta.', 'info')
    return redirect(url_for('index'))


def cuidador_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not isinstance(current_user, Cuidador):
            flash("Acesso negado. Apenas cuidadores podem acessar esta página.", "danger")
            return redirect(url_for("index"))
        return f(*args, **kwargs)
    return decorated_function

def paciente_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not isinstance(current_user, Usuario):  
            flash("Acesso negado. Apenas pacientes podem acessar esta página.", "danger")
            return redirect(url_for("index"))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/doacoes', methods=['GET', 'POST'])
@login_required
def doacoes():
    if isinstance(current_user, Cuidador): 
        flash("Apenas pacientes podem fazer pedidos de doações.", "danger")
        return redirect(url_for('doacoes_disponiveis')) 

    if request.method == 'POST':
        item = request.form['item']
        descricao = request.form['description']
        urgencia = request.form['urgency']
        contato_info = request.form['contact_info']
        usuario_id = current_user.id 

        pedido = PedidoDoacao(item=item, descricao=descricao, urgencia=urgencia, contato_info=contato_info, usuario_id=usuario_id)
        db.session.add(pedido)
        db.session.commit()

        flash('Pedido de doação registrado com sucesso!', 'success')

    pedidos = PedidoDoacao.query.filter_by(usuario_id=current_user.id).all()
    return render_template('doacoes.html', pedidos=pedidos)

@app.route('/doacoes_disponiveis')
@login_required
def doacoes_disponiveis():
    if isinstance(current_user, Usuario): 
        flash("Acesso negado. Apenas cuidadores podem acessar esta página.", "danger")
        return redirect(url_for("index")) 
    
    else:
        pedidos = PedidoDoacao.query.all()  
        return render_template('doacoes_disponiveis.html', pedidos=pedidos)


@app.route('/deletar_pedido/<int:pedido_id>', methods=['POST'])
@login_required
def deletar_pedido(pedido_id):
    pedido = PedidoDoacao.query.get_or_404(pedido_id)

    if pedido.usuario_id != current_user.id:
        flash('Você não tem permissão para excluir este pedido', 'danger')
        return redirect(url_for('doacoes'))

    db.session.delete(pedido)
    db.session.commit()

    flash('Pedido de doação deletado com sucesso!', 'success')
    return redirect(url_for('doacoes'))

@app.route('/sobre')
def sobre():
    return render_template('sobre.html')

def validar_senha(senha):
    if len(senha) < 6:
        return "A senha deve ter pelo menos 6 caracteres."
    if not re.search(r"\d", senha):
        return "A senha deve conter pelo menos um número."
    return None

@app.route('/cadastro', methods=['POST', 'GET'])
def cadastro():
    if request.method == 'GET':
        return render_template('cadastro.html')

    if request.method=='POST':
        tipo = request.form['tipo']
        nome = request.form['nome']
        email = request.form['email']
        senha = request.form['senha']

        erro_senha = validar_senha(senha)
        if erro_senha:
            flash(erro_senha, 'erro_senha')  # Categoria específica para senha
            return redirect(url_for('cadastro'))



        if tipo=='0':
            usuario = Usuario(nome=nome, email=email, senha=senha)
            db.session.add(usuario)

        if tipo=='1':
            cuidador = Cuidador(nome=nome, email=email, senha=senha)
            db.session.add(cuidador)

        db.session.commit()

        flash('Cadastrado com sucesso', 'success')
        return redirect(url_for('login'))

@app.route('/faq')
def faq():
    return render_template('faq.html')

@app.route('/perfil')
@login_required
def perfil():
    return render_template('perfil.html', usuario=current_user)

# Rota para editar o perfil
@app.route('/editar_perfil', methods=['GET', 'POST'])
@login_required
def editar_perfil():
    usuario = current_user

    if request.method == 'POST':
        # Aqui você processa os dados do formulário de edição, como nome, email, etc.
        usuario.nome = request.form['nome']
        usuario.email = request.form['email']
        db.session.commit()  # Salva as mudanças no banco de dados
        flash('Perfil atualizado com sucesso!', 'success')
        return redirect(url_for('perfil'))  # Redireciona para a página de perfil

    return render_template('editar_perfil.html', usuario=usuario)

# Rota para deletar a conta
@app.route('/deletar_conta', methods=['POST'])
@login_required
def deletar_conta():
    usuario = current_user

    # Deleta o usuário atual da base de dados
    db.session.delete(usuario)
    db.session.commit()  # Confirma a remoção do usuário
    flash('Conta deletada com sucesso!', 'success')

    # Redireciona para a página inicial ou de login
    return redirect(url_for('index'))

app.run(debug=True)
