# app.py
from flask import render_template, request, redirect, url_for
from flask import session as login_session
from notesApp.models import User, Tag, Note, NoteTag
from notesApp import flask_obj, db
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import func

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
        # store current user's user id for later usage
        login_session['id'] = db.session.execute(db.select(User.id).where(User.email == email)).scalar()

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
    note_tuples = []
    first = 0
    # view only notes for specific user
    notes = Note.query.filter(Note.user_id == login_session['id']).all()
    note_tuples.clear()
    for note in notes:
        note_tuples.append((note.id, note.body))

    data = request.form
    print(request.form)
    
    if request.method == 'POST':

        empty_title = request.form['note_title'] == ""
        empty_body = request.form['note_body'] == ""
        empty_tag_name = request.form['new_tag_name'] == ""

        if request.form.get('button') == 'tag_button' and not empty_tag_name:
            tag_name = request.form['new_tag_name']
            if not bool(db.session.execute(db.select(Tag).where((Tag.title == tag_name) & (Tag.user_id==login_session['id']))).all()):
                print('in here!')
                new_tag = Tag(title=tag_name, user_id=login_session['id'])
                db.session.add(new_tag)
                db.session.commit()
            print(db.session.execute(db.select(Tag).where((Tag.title == tag_name) & (Tag.user_id==login_session['id']))).all())
        elif request.form.get('button') == 'save_note_button':
            title = "New Note" if empty_title else request.form['note_title']
            body = "Note body goes here!" if empty_title else request.form['note_body']

            new_note = Note(title=title, body=body, user_id = login_session['id'])
            db.session.add(new_note)
            db.session.commit()

            note_tuples.append((new_note.id, new_note.body))

            # if (len(Note.query.filter(Note.user_id == login_session['id']).all())) == 1:
            #     first_note = new_note.id
            #     first = first_note

            # update noteview after new note is created
            notes = Note.query.filter(Note.user_id == login_session['id']).all()

            if empty_title:
                del title
            if empty_body:
                del body
            print("save button")
        
        num_notes = db.session.query(func.count(Note.id)).scalar()

    print('here')
    tags = {}
    for n in notes:
        tags[n.id] = db.session.execute(db.select(Tag).join(NoteTag, NoteTag.id == n.id)).all()
    print(tags)

    if len(note_tuples) != 0:
        first = note_tuples[0][0]

    if (request.method == 'GET'):
        clicked_note = request.args.get('clicked', default=0, type=int)
        selected_notes = Note.query.filter(Note.id == (clicked_note) + first - 1).all()
        
        for selected_note in selected_notes:
        
            if clicked_note:
                selected_title = selected_note.title
                selected_body = selected_note.body
            else:
                selected_title = "Note not found"
                selected_body = ""

    # TO RETRIEVE CLICKED NOTE'S ID, FETCH: clicked_note = request.args.get('clicked', default=0, type=int)
    # THEN USE THE FOLLOWING FORMULA: (clicked_note) + first - 1

    return render_template('home.html', **locals())

@flask_obj.route('/options')
def options():
    return render_template('options.html')

@flask_obj.route('/logout')
def logout():
    # You can perform any necessary logout logic here
    # For now, we'll just redirect to the login page
    del login_session['id']
    return render_template('login.html')