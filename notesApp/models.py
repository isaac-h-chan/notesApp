from notesApp import db
from sqlalchemy import Integer, String
from sqlalchemy.orm import mapped_column

class User(db.Model):
    id = mapped_column(Integer, primary_key=True)
    email = mapped_column(String, unique=True, nullable=False)
    username = mapped_column(String, nullable=False)
    password = mapped_column(String, nullable=False)
