# app.py
from flask import render_template, request, redirect, url_for
from notesApp.models import User, Tag, Note, NoteTag
from notesApp import flask_obj, db
from werkzeug.security import generate_password_hash, check_password_hash

@flask_obj.route('/')
def login():
    return render_template('login.html')

@flask_obj.route('/login', methods=['POST'])
def handle_login():
    # Check username and password
    email = request.form.get('email')
    password = request.form.get('password')

    # Hardcoded username and password for demonstration
    if not bool(db.session.execute(db.select(User).where(User.email == email)).scalar()):
            return render_template('login.html', error1='No account exists with this email.') 
   
    if check_password_hash(db.session.execute(db.select(User.password).where(User.email == email)).scalar(), password):
        # Redirect to home.html upon successful login
        return redirect(url_for('home'))
    else:
        # You can handle authentication failure here
        return render_template('login.html', error2='Incorrect Password')

@flask_obj.route('/create_account', methods=['GET', 'POST'])
def create_account():
    data = request.form
    if request.method == 'POST':
        # Get user input from the registration form
        username = request.form.get('username')
        password = request.form.get('password')
        email = request.form.get('email')

        # Check if the email is already associated with an existing account
        if bool(db.session.execute(db.select(User).where(User.email == email)).scalar()):
            return render_template('create_account.html', data=request.form, error='An account with this email already exists.')
        
        # Create a new user and add them to the database
        new_user = User(email=email, username=username, password=generate_password_hash(password))
        db.session.add(new_user)
        db.session.commit()

        # Redirect to the login page after successful registration
        return redirect(url_for('login'))
    return render_template('create_account.html', data=data)

@flask_obj.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        # Check if the provided email exists in the database
        email = request.form.get('email')
        user = next((user for user in users if user['email'] == email), None)

        if user:
            # Implement logic to send a password reset link (not implemented in this example)
            # You can send an email with a reset link or generate a token and provide a link with the token
            # For simplicity, this example just redirects to a confirmation page
            return redirect(url_for('password_reset_confirmation'))
        else:
            # Handle the case where the email is not found in the database
            return render_template('forgot_password.html', error='Email not found.')

    return render_template('forgot_password.html')

@flask_obj.route('/password_reset_confirmation')
def password_reset_confirmation():
    return render_template('password_reset_confirmation.html')

@flask_obj.route('/home', methods=['GET', 'POST'])
def home():
    notes = Note.query.all()
    data = request.form

    if request.method == 'POST':
        title = request.form['note_title']
        body = request.form['note_body']

        new_note = Note(title=title, body=body, user_id = 1) # placeholder id
        db.session.add(new_note)
        db.session.commit()

        notes = Note.query.all()

    # TODO: Modify note view when existing note is clicked
        
    return render_template('home.html', **locals())

@flask_obj.route('/home/noteview', methods=['GET', 'POST'])
def viewnote():
    notes=Note.query.all()
    data = request.form
    title = "None"
    body = "None"
    selected_note = Note(title=title, body=body, user_id=1)

    if request.method == 'POST':
        title = request.form['note_title-item']
        body = request.form['note_body-item']

        notes = Note.query.filter_by(body=body).all()
        selected_note = Note(title=title, body=body, user_id = 1)  # temporary, fix later: Note.query.filter_by(body=body).all()

    return render_template('home.html', **locals())

@flask_obj.route('/options')
def options():
    return render_template('options.html')

@flask_obj.route('/logout')
def logout():
    # You can perform any necessary logout logic here
    # For now, we'll just redirect to the login page
    return render_template('login.html')