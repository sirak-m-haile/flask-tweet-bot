import os
from flask import Flask, request, redirect, session, url_for, render_template, flash
from werkzeug.exceptions import abort
import main

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(50)

@app.route("/oauth/callback", methods=["GET"])
def callback():
    code = request.args.get("code")
    token = main.make_token(twitter, code)
    main.save_token(token)
    return redirect(url_for('create'))

@app.route('/')
def index():
    global twitter
    twitter, authorization_url, state = main.create_session()
    session["oauth_state"] = state
    return redirect(authorization_url)

@app.route('/create', methods = ['GET', 'POST'])
def create():
    if request.method == 'POST':
        id = main.save_search_query_spec(request.form)
        return redirect(url_for('edit', id=id))
    else:
        return render_template('create.html')

@app.route('/query/<id>', methods=['GET','POST'])
def edit(id):
    if request.method =='POST':
        input = { 'id': id, **request.form}
        main.save_search_query_spec(input)
        flash("Update Successfully Saved")

    search_query_item = main.get_search_query_spec(id)
    if search_query_item is None:
        return render_template('404.html')
    return render_template('edit.html', search_query_item=search_query_item)

if __name__ == "__main__":
    app.run()