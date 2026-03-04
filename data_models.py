from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Author(db.Model):
    __tablename__ = 'authors'

    author_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    author_name = db.Column(db.String)
    birth_date = db.Column(db.String)
    date_of_death = db.Column(db.String)

    def __str__(self):
        return f"Author name: {self.author_name}, his age is {datetime.strptime(self.date_of_death, '%Y %m %d').date() - datetime.strptime(self.date_of_death, '%Y %m %d').date()} years old"


class Book(db.Model):
    __tablename__ = 'books'

    book_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    book_title = db.Column(db.String)
    author_id = db.Column(db.Integer, db.ForeignKey('authors.author_id'))
    publication_year = db.Column(db.Integer)
    isbn = db.Column(db.String,unique=True)
    author = db.relationship('Author', backref='books')

    def __str__(self):
        return f"Book title: {self.book_title}, published in {self.publication_year} by the author {self.author_id}"



