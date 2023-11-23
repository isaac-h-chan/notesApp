from notesApp import db
from sqlalchemy import Integer, String, Text, ForeignKey
from sqlalchemy.orm import mapped_column, Mapped

class User(db.Model):
    __tablename__ = 'user'
    id = mapped_column(Integer, primary_key=True)
    email = mapped_column(String, unique=True, nullable=False)
    username = mapped_column(String, nullable=False)
    password = mapped_column(String, nullable=False)

class Note(db.model):
    __tablename__ = 'note'
    id:Mapped[int] = mapped_column(Integer, primary_key=True)
    title:Mapped[str] = mapped_column(String)
    body:Mapped[str] = mapped_column(Text)
    user_id:Mapped[int] = mapped_column(ForeignKey('user.id'),nullable=False)

class Tag(db.model):
    __tablename__ = 'tag'
    id:Mapped[int] = mapped_column(Integer, primary_key=True)
    title:Mapped[str] = mapped_column(String)
    user_id:Mapped[int] = mapped_column(ForeignKey('user.id'),nullable=False)

class NoteTag(db.model):
    __tablename__ = 'note'
    id:Mapped[int] = mapped_column(Integer, primary_key=True)
    note_id:Mapped[int] = mapped_column(ForeignKey('note.id'),nullable=False)
    tag_id:Mapped[int] = mapped_column(ForeignKey('tag.id'),nullable=False)