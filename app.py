from flask import Flask, render_template, flash, redirect, request, url_for
import sqlite3

app = Flask(__name__)
app.config['SECRET_KEY'] = "Karol1004"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/autenticar', methods=['POST'])
def autenticar():
    email = request.form['email']
    senha = request.form['senha']

    con = sqlite3.connect('database.db')
    cursor = con.cursor()
    cursor.execute('SELECT * FROM users WHERE email = ?', [email])
    users = cursor.fetchone()
    
    if(users[1] == senha):
        flash('Logado com sucesso', 'success')
        return redirect('/')

    if(users[1] != senha):
        flash('Login ou senha incorretos', 'danger')
        return redirect(url_for('login'))

@app.route('/doacoes')
def doacoes():
     return render_template('doacoes.html')

@app.route('/sobre')
def sobre():
    return render_template('sobre.html')


@app.route('/cadastro', methods=['POST', 'GET'])
def cadastro():
    if request.method == 'GET':
        return render_template('cadastro.html')
    
    if request.method=='POST':
        nome = request.form['nome']
        email = request.form['email']
        senha = request.form['senha'] 
        con =  sqlite3.connect('database.db')
        con.execute('INSERT INTO users (nome, email, password) VALUES (?,?,?)',(nome,email, senha))
        con.commit()
        con.close()

        flash('Cadastrado com sucesso', 'success')
        return redirect(url_for('login'))