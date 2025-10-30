from flask import render_template
from flaskr import app
from flaskr.forms import LoginForm

@app.route('/')
@app.route('/login', methods=['GET', 'POST']) #TODO: See the necessity of the GET method here, remove if not needed

def login():
    form = LoginForm()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        remember_me = form.remember_me.data
        #TODO: Implement login logic here
        # return redirect(url_for('index'))

    return render_template('login.html', form=form)