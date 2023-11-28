# app.py
from flask import render_template, request, redirect, url_for, jsonify
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
    # view only notes for specific user
    notes = Note.query.filter(Note.user_id == login_session['id']).all()
    for note in notes:
        print(note)
        note_tuples.append((note.id, note.title, note.body))

    if request.method == 'POST':

        empty_title = request.form['note_title'] == ""
        empty_body = request.form['note_body'] == ""
        
        title = "New Note" if empty_title else request.form['note_title']
        body = "Note body goes here!" if empty_title else request.form['note_body']

        new_note = Note(title=title, body=body, user_id = login_session['id'])
        db.session.add(new_note)
        db.session.commit()

        note_tuples.append((new_note.id, new_note.title, new_note.body))

        # update noteview after new note is created
        notes = Note.query.filter(Note.user_id == login_session['id']).all()

        if empty_title:
            del title
        if empty_body:
            del body
        
        num_notes = db.session.query(func.count(Note.id)).scalar()

    return render_template('home.html', **locals())

@flask_obj.route("/get_note/<int:note_id>", methods=["GET"])
def get_note(note_id):
    print(note_id, type(note_id))
    note = db.session.execute(db.select(Note).where(Note.id==note_id)).scalar()
    tags = []
    for tag in db.session.execute(db.select(Tag).where((NoteTag.note_id==note_id) & (NoteTag.tag_id==Tag.id) & (Tag.user_id==login_session['id']))).scalars().all():
        tags.append((tag.id, tag.title))
    response = {
        "id": note_id,
        "selected_title": note.title,
        "selected_body": note.body,
        "tags": tags
    }
    print(response)

    return jsonify(response)

@flask_obj.route("/add_tag", methods=["POST"])
def add_tag():
    selected_note_id = request.json.get("selected_note_id")
    tag_name = request.json.get("tag_name")
    if not bool(db.session.execute(db.select(Tag).where((Tag.title == tag_name) & (Tag.user_id==login_session['id']))).all()):
        tag = Tag(title=tag_name, user_id=login_session['id'])
        db.session.add(tag)
        db.session.commit()
    else:
        print('already exists')
        tag = db.session.execute(db.select(Tag).where((Tag.title == tag_name) & (Tag.user_id == login_session['id']))).scalar()
    
    if not bool(db.session.execute(db.select(NoteTag).where((NoteTag.note_id==selected_note_id) & (NoteTag.tag_id==tag.id))).all()):
        noteTag = NoteTag(note_id=selected_note_id, tag_id=tag.id)
        db.session.add(noteTag)
        db.session.commit()
    
    response = {
        "tag_id": tag.id,
        "tag_name": tag.title
    }
    return jsonify(response)

@flask_obj.route('/options')
def options():
    return render_template('options.html')

@flask_obj.route('/logout')
def logout():
    # You can perform any necessary logout logic here
    # For now, we'll just redirect to the login page
    del login_session['id']
    return render_template('login.html')

@flask_obj.route('/delete_account', methods=['GET', 'POST'])
def delete_account():
    form = DeleteAccountForm()

    if form.validate_on_submit():
        # Get the current user's ID from the session
        user_id = login_session.get('id')

        # Query the database to get the user object
        user = User.query.get(user_id)

        if user:
            # Delete the user and commit the changes to the database
            db.session.delete(user)
            db.session.commit()

            # Logout the user by removing the user ID from the session
            del login_session['id']

            # Redirect to the login page or any other appropriate page
            flash('Account successfully deleted.', 'success')
            return redirect(url_for('login'))
        else:
            # Handle the case where the user is not found
            flash('User not found.', 'danger')
            return render_template('error.html', error='User not found')

    return render_template('/delete_account.html', form=form)

@flask_obj.route('/confirm_delete_account', methods=['GET', 'POST'])
def confirm_delete_account():
    if request.method == 'POST':
        # Get the current user's ID from the session
        user_id = login_session.get('id')

        # Query the database to get the user object
        user = User.query.get(user_id)

        if user:
            # Delete the user and commit the changes to the database
            db.session.delete(user)
            db.session.commit()

            # Logout the user by removing the user ID from the session
            del login_session['id']

            # Render the confirmation template
            return render_template('confirm_delete_account.html')

            # Redirect to the login page or any other appropriate page
            flash('Account successfully deleted.', 'success')
            return redirect(url_for('login'))
        else:
            # Handle the case where the user is not found
            flash('User not found.', 'danger')
            return render_template('error.html', error='User not found')

    return render_template('delete_account.html')
