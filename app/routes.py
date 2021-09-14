from flask import render_template, flash, redirect
from app import app
from app.forms import LoginForm


@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def index():
    form = LoginForm()
    if form.validate_on_submit():
        flash(f"Login requested for user {form.username.data}")
        return redirect(f"/polis/xid/{form.username.data}")
    return render_template('index.html', form=form)


@app.route('/polis/xid/<username>')
def polis(username):
    return render_template('polis.html', username=username)
