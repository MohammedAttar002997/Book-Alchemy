from datetime import datetime

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, ForeignKey

db = SQLAlchemy()


class Author(db.Model):
    __tablename__ = 'authors'

    author_id = Column(Integer, primary_key=True, autoincrement=True)
    author_name = Column(String)
    birth_date = Column(String)
    date_of_death = Column(String)

    def __str__(self):
        return f"Author name: {self.author_name}, his age is {datetime.strptime(self.date_of_death, '%Y %m %d').date() - datetime.strptime(self.date_of_death, '%Y %m %d').date()} years old"


class Book(db.Model):
    __tablename__ = 'books'

    book_id = Column(Integer, primary_key=True, autoincrement=True)
    book_title = Column(String)
    author_id = Column(Integer, ForeignKey('authors.author_id'))
    publication_year = Column(Integer)
    isbn = Column(String,unique=True)
    author = db.relationship('Author', backref='books')

    def __str__(self):
        return f"Book title: {self.book_title}, published in {self.publication_year} by the author {self.author_id}"



