from flask import render_template, flash, redirect
from flaskr import app
from flaskr.forms import LoginForm

@app.route('/')
@app.route('/index')
def index():
    return redirect('/login')

@app.route('/login', methods=['GET', 'POST']) #TODO: See the necessity of the GET method here, remove if not needed
def login():
    form = LoginForm()

    if form.validate_on_submit():
        #username = form.username.data
        #password = form.password.data
        #remember_me = form.remember_me.data
        flash('Login requested for user {}, remember_me={}'.format(
            form.username.data, form.remember_me.data
        ))
        return redirect('/dashboard')
        #TODO: Implement login logic here
        # return redirect(url_for('index'))

    return render_template('login.html', form=form)

@app.route('/menu')
def menu():
    return render_template('menu.html')

@app.route('/relatorio-grafico')
def relatorio_grafico():
    return render_template('relatorio-grafico.html')
