import os
from app import app
from flask import render_template, redirect, request, url_for, session, jsonify, Response
from flask_login import login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from .extensions import login_manager,db,cache
from .models import User, Task

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/logo.svg')
@cache.cached(timeout=3600)
def serve_logo():
    with open(os.path.join(app.static_folder, 'images/logo.svg'), 'rb') as f:
        svg_data = f.read()

    return Response(svg_data, mimetype='image/svg+xml')

@app.route('/')
def index():
    if current_user.is_authenticated:
        uncompleted = Task.query.filter_by(owner_id=current_user.id, status=0).all()
        completed = Task.query.filter_by(owner_id=current_user.id, status=1).all()
        return render_template('index.html', all_tasks=uncompleted+completed)
    else :
        return render_template('index.html', all_tasks=[])

@app.route('/login', methods=['POST'])
def login():
    form = request.json
    user = User.query.filter_by(account=form['account']).first()
    if user:
        if check_password_hash(user.password, form['password']):
            login_user(user)
            session['account'] = current_user.account
            session['id'] =  current_user.id
            if form['remember'] == True :
                session.permanent = True
            else :
                session.permanent = False

            return '', 200
        
    return '', 401

@app.route('/register', methods=['POST'])
def register():
    form = request.json
    duplicate_name = User.query.filter_by(account=form['account']).count()
    if not duplicate_name:
        hashed_password = generate_password_hash(form['password'], method='sha256')
        new_user = User(account=form['account'], password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        session['account'] = new_user.account
        session['id'] = new_user.id
        return '', 200
    else:
        return '', 401

@app.route('/logout')
def logout():
    logout_user()
    session['account'] = "" 
    session['id'] = ""
    return redirect(url_for('index'))

@app.route('/add', methods=['POST'])
def add():
    form = request.json
    new_task = Task(desc=form['description'], status=0, owner_id=current_user.id)
    db.session.add(new_task)
    db.session.commit()
    return jsonify({'id': new_task.id })

@app.route('/delete/<int:id>', methods=['POST'])
def delete(id) :
    task = Task.query.filter_by(id=id).first()
    if task != None and current_user.id == task.owner_id:
        db.session.delete(task)
        db.session.commit()
        return '', 200
    else :
        return '', 404

@app.route('/complete/<int:id>', methods=['POST'])
def complete(id) :
    task = Task.query.filter_by(id=id).first()
    if task != None and current_user.id == task.owner_id:
        task.status = not task.status 
        db.session.commit()
        return '', 200
    else :
        return '', 404
    
@app.route('/update/<int:id>', methods=['POST'])
def update(id) :
    form = request.json
    task = Task.query.filter_by(id=id).first()
    if task != None and current_user.id == task.owner_id:
        task.desc = form['new_desc']
        db.session.commit()
        return '', 200
    else :
        return '', 404