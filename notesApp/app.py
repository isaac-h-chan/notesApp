# app.py
from flask import abort, render_template, request, redirect, url_for, jsonify, flash, send_file
from flask import session as login_session
from notesApp.models import User, Tag, Note, NoteTag
from notesApp import flask_obj, db
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import func
from flask import Flask, render_template, request, send_file
from fpdf import FPDF
from notesApp.thumb import generate_image
import re


@flask_obj.route('/', methods=['GET'])
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

# serve home.html to frontend and populate fields with all notes associated with user id
@flask_obj.route('/home', methods=['GET', 'POST'])
def home():
    note_tuples = []
    # view only notes for specific user
    notes = Note.query.filter(Note.user_id == login_session['id']).all()
    for note in notes:
        note_tuples.append((note.id, note.title, note.body, note.thumb_url))
    return render_template('home.html', **locals())

#save note or create note if it doesnt exist
@flask_obj.route('/save/<int:note_id>', methods=["POST"])
def save_note(note_id):

    if request.method == 'POST':

        # note_id == 0 means to create a new note
        if note_id == 0:

            # assign default values to note if fields are empty
            title = "New Note" if not request.json['note_title'] else request.json['note_title']
            body = "Note body goes here!" if not request.json['note_body'] else request.json['note_body']

            new_note = Note(title=title, body=body, user_id = login_session['id'], thumb_url=False)
            db.session.add(new_note)
            db.session.commit()
            response = {
                "new": True,
                "note_title": title,
                "note_body": body,
                "note_id": new_note.id
            }

        # not a new note, update content of specified note in db
        else:
            db.session.execute(db.update(Note).where(Note.id==note_id).values({Note.title: request.json['note_title'], Note.body: request.json['note_body']}))
            db.session.commit()
            response = {
                "new": False
            }
        return jsonify(response)

# get all content associated with a note
@flask_obj.route("/get_note/<int:note_id>", methods=["GET"])
def get_note(note_id):
    note = db.session.execute(db.select(Note).where(Note.id==note_id)).scalar()

    # add all tags associated with note to a list
    tags = []
    for tag in db.session.execute(db.select(Tag).where((NoteTag.note_id==note_id) & (NoteTag.tag_id==Tag.id) & (Tag.user_id==login_session['id']))).scalars().all():
        tags.append((tag.id, tag.title))

    response = {
        "id": note_id,
        "selected_title": note.title,
        "selected_body": note.body,
        "tags": tags
    }

    return jsonify(response)

# create a tag if it doesn't exist and then assign a relationship between tag and note in db
@flask_obj.route("/add_tag", methods=["POST"])
def add_tag():

    # get note id and the tag name specified by user
    selected_note_id = request.json.get("selected_note_id")
    tag_name = request.json.get("tag_name")

    # if the tag doesn't exist for the user, create a new tag with tag_name for the user
    if not bool(db.session.execute(db.select(Tag).where((Tag.title == tag_name) & (Tag.user_id==login_session['id']))).all()):
        tag = Tag(title=tag_name, user_id=login_session['id'])
        db.session.add(tag)
        db.session.commit()
    
    # tag already exists for user so get the tag from db so we can create relationship between note and tag
    else:
        tag = db.session.execute(db.select(Tag).where((Tag.title == tag_name) & (Tag.user_id == login_session['id']))).scalar()
    
    # if the not does not already have the tag, create a relationship between note and tag
    if not bool(db.session.execute(db.select(NoteTag).where((NoteTag.note_id==selected_note_id) & (NoteTag.tag_id==tag.id))).all()):
        noteTag = NoteTag(note_id=selected_note_id, tag_id=tag.id)
        db.session.add(noteTag)
        db.session.commit()
    
    response = {
        "tag_id": tag.id,
        "tag_name": tag.title
    }
    return jsonify(response)

# redirects the user to a page where notes can be deleted
@flask_obj.route('/delete', methods=["GET"])
def go_to_delete():

    # get all notes that belong to the user so that they can be displayed on frontend
    note_tuples = []
    notes = Note.query.filter(Note.user_id == login_session['id']).all()
    for note in notes:
        note_tuples.append((note.id, note.title, note.body))
    return render_template("delete.html", note_tuples=note_tuples)

# deletes specified notes from db
@flask_obj.route('/delete_notes', methods=["DELETE"])
def delete_notes():

    # get all note id's of notes to be deleted
    data = request.json['notes']

    # delete each note from the db
    for id in data:
        db.session.execute(db.delete(Note).where(Note.id==id))
        db.session.execute(db.delete(NoteTag).where(NoteTag.note_id==id))
    db.session.commit()
    return jsonify("OK")

# generates thumbnail for note when passed its body content
@flask_obj.route('/get_thumb/<int:note_id>', methods=["POST"])
def get_thumb(note_id):

    # get body content
    sen = request.json['note_body']

    # generate new image related to the body content. defaults to leaves if there is specific topic.
    generate_image(sen, note_id)
    response = {
        'path': "thumbnails/" + str(note_id) + ".png"
    }

    # update db to signify that there is a thumbnail for the note
    db.session.execute(db.update(Note).where(Note.id==note_id).values({Note.thumb_url: True}))
    db.session.commit()
    return jsonify(response)

# fetches thumbnail image for specified note and then sends it back to frontend as a response
@flask_obj.route("/thumbnails/<file>", methods=["GET"])
def get_image(file):

    # split on "?" character since characters after "?" are random to override browser cache
    file = file.split("?")[0]
    path = "./static/thumbnails/" + file
    return send_file(path)

@flask_obj.route('/options')
def options():
    return render_template('options.html')

@flask_obj.route('/delete_account', methods=['DELETE'])
def delete_account():
    user_to_delete = User.query.filter(User.id == login_session['id']).first()
    try:
        # delete all of user's created notes in the db
        notes = Note.query.filter(Note.user_id == login_session['id']).all()
        for note in notes:
            db.session.delete(note)
        db.session.commit()

        # delete all of user's created tags in the db
        tags = Tag.query.filter(Tag.user_id == login_session['id']).all()
        for tag in tags:
            db.session.delete(tag)
        db.session.commit()

        # delete user
        db.session.delete(user_to_delete)
        db.session.commit()
        flash("User deleted successfully!", 'success')
        return jsonify({'status': 'success'})
    
    except:
        db.session.rollback()  # Rollback changes in case of an exception
        flash("There was an issue deleting the user. Please try again.", 'error')
        return jsonify({'status': 'error'})

@flask_obj.route('/logout')
def logout():
    # You can perform any necessary logout logic here
    # For now, we'll just redirect to the login page
    del login_session['id']
    return render_template('login.html')


# Function to update the user profile into database
def update_user_profile(new_name,new_email, new_password):
    user = User.query.filter(User.id == login_session['id']).first()
    if user:
        user.username = new_name
        user.email = new_email
        user.password = generate_password_hash(new_password)
        db.session.commit()

#Function to ask user to enter new email, password , and username
@flask_obj.route('/update_profile', methods=['GET', 'POST'])
def update_profile():
    if request.method == 'POST':
        new_name = request.form.get('new_name')
        new_email = request.form.get('new_email')
        new_password = request.form.get('new_password')

        update_user_profile(new_name, new_email, new_password)
        return redirect(url_for('home'))

    return render_template('update_profile.html')

# Function that share note to other user
@flask_obj.route('/share_id_note/', methods=["POST"])
def share_note():
    #Extract note_id and email from json request
    note_id = request.json['note_id']
    email = request.json['email']
    user_exists = db.session.execute(db.select(User.id).where(User.email == email)).scalar()
    if user_exists:
    #Retrieve the user ID with email from the database
        share_user = db.session.execute(db.select(User.id).where(User.email == email)).scalar()
        if request.method == 'POST':
            if share_user is not None:
                # If note_id = 0, it indicates that a new note
                if note_id == 0:
                    title = "New Note" if not request.json['note_title'] else request.json['note_title']
                    body = "Note body goes here!" if not request.json['note_body'] else request.json['note_body']

                    #Create a new note and add to the database
                    new_note = Note(title=title, body=body, user_id = share_user, thumb_url=False)
                    db.session.add(new_note)
                    db.session.commit()
                    response = {
                    "new": True,
                    "note_title": title,
                    "note_body": body,
                    "note_id": new_note.id
                }
                else: # for existing note
                    title = "New Note" if not request.json['note_title'] else request.json['note_title']
                    body = "Note body goes here!" if not request.json['note_body'] else request.json['note_body']

                    new_note = Note(title=title, body=body, user_id = share_user, thumb_url=False)
                    db.session.add(new_note)
                    db.session.commit()
                    response = {
                    "new": True,
                    "note_title": title,
                    "note_body": body,
                }
        return jsonify(response)
    else:
        abort(404) #Connect to JS

# gets all notes from db with selected tags and have search query in either title or body
@flask_obj.route('/search', methods=['GET','POST'])
def search_notes():
    search_query = request.json['search_query']
    tag_ids = request.json['tag_ids']
    notes = filterTags(tag_ids)
    matching_notes = notes.filter(Note.title.ilike(f'%{search_query}%') | Note.body.ilike(f'%{search_query}%')).all()
    response = [{"id": note.id, "body": note.body, "title": note.title, 'thumb': note.thumb_url} for note in matching_notes]
    return 

@flask_obj.route("/get_tags", methods=['GET'])
def get_tags():
    tags = db.session.query(Tag).filter(Tag.user_id == login_session['id']).all()

    tags_list = [
        {"id": tag.id, "title": tag.title}
        for tag in tags
    ]

    return jsonify(tags_list)

# returns sqlalchemy query for only notes with the given tags in tags_id
def filterTags(tag_ids:str):
    if tag_ids:
        # split selected tag ids into a list using commas as separators
        tag_ids_list = re.split(',', tag_ids)

        # count the number of matching tags for each note
        subquery = (
            db.session.query(Note.id.label("note_id"), func.count(NoteTag.tag_id).label("tag_count"))
            .join(NoteTag)
            .filter(Note.id == NoteTag.note_id)
            .filter(NoteTag.tag_id.in_(tag_ids_list))
            .group_by(Note.id)
            .subquery()
        )

        # filter notes based on the count of matching tags
        notes = (
            db.session.query(Note)
            .join(subquery, Note.id == subquery.c.note_id)
            .filter(subquery.c.tag_count == len(tag_ids_list))
        )

    else:
        # if no tags are selected, return all notes for this user
        notes = Note.query.filter(Note.user_id == login_session['id'])
    return notes

@flask_obj.route("/get_notes", methods=["GET"])
def get_notes():
    tag_ids = request.args.get("tags")
    notes = filterTags(tag_ids).all()
    response = [{"id": note.id, "body": note.body, "title": note.title, 'thumb': note.thumb_url} for note in notes]
    return jsonify(response)
     