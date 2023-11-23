from notesApp import db
from sqlalchemy import Integer, String, Text, ForeignKey
from sqlalchemy.orm import mapped_column, Mapped

class User(db.Model):
    __tablename__ = 'user'
    id = mapped_column(Integer, primary_key=True)
    email = mapped_column(String, unique=True, nullable=False)
    username = mapped_column(String, nullable=False)
    password = mapped_column(String, nullable=False)

class Note(db.Model):
    __tablename__ = 'note'
    __table_args__ = {'extend_existing':True}
    id:Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title:Mapped[str] = mapped_column(String)
    body:Mapped[str] = mapped_column(Text)
    user_id:Mapped[int] = mapped_column(ForeignKey('user.id'),nullable=False)

    def __init__(self, title, body, user_id):
        self.title = title
        self.body = body
        self.user_id = user_id

class Tag(db.Model):
    __tablename__ = 'tag'
    __table_args__ = {'extend_existing':True}
    id:Mapped[int] = mapped_column(Integer, primary_key=True)
    title:Mapped[str] = mapped_column(String)
    user_id:Mapped[int] = mapped_column(ForeignKey('user.id'),nullable=False)

class NoteTag(db.Model):
    __tablename__ = 'note'
    __table_args__ = {'extend_existing':True}
    id:Mapped[int] = mapped_column(Integer, primary_key=True)
    note_id:Mapped[int] = mapped_column(ForeignKey('note.id'),nullable=False)
    tag_id:Mapped[int] = mapped_column(ForeignKey('tag.id'),nullable=False)