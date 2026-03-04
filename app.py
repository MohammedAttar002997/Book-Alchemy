from data_models import db, Author, Book
from flask import Flask, render_template, request, flash, redirect, url_for
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)
app.secret_key = 'development-key'

basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(basedir, 'data/library.sqlite')}"

db.init_app(app)

with app.app_context():
  db.create_all()


@app.route('/add_author', methods=['GET','POST'])
def add_author():

    if request.method == 'POST':
        author = Author(
            author_name = request.form['name'],
            birth_date= request.form['birthdate'],
            date_of_death= request.form['date_of_death'],
        )
        db.session.add(author)
        db.session.commit()
        flash(f"Author {author.author_name} added successfully", "success")
        return redirect(url_for('home')), 200
    return render_template("add_author.html")


@app.route('/add_book', methods=['GET','POST'])
def add_book():

    if request.method == 'POST':
        book = Book(
            book_title = request.form['title'],
            publication_year= request.form['publication_year'],
            author_id= request.form['author_id'],
            isbn= request.form['isbn'],
        )
        db.session.add(book)
        db.session.commit()
        flash(f"Book '{book.book_title}' added successfully!", "success")
        return redirect(url_for('home'))
    authors = db.session.query(Author).all()
    return render_template("add_book.html", authors=authors)


@app.route('/')
def home():
    search_query = request.args.get('search', '')
    sort_by = request.args.get('sort', 'book_title')
    direction = request.args.get('direction', 'asc')

    try:
        # Start the query
        query = Book.query.join(Author).options(db.joinedload(Book.author))

        # Apply search filter if present
        if search_query:
            search_filter = f"%{search_query}%"
            query = query.filter(
                db.or_(
                    Book.book_title.ilike(search_filter),
                    Author.author_name.ilike(search_filter)
                )
            )
        # Determine the sorting column
        if sort_by == 'author':
            sort_column = Author.author_name
        else:
            sort_column = getattr(Book, sort_by, Book.book_title)

        # Apply sorting
        if direction == 'desc':
            query = query.order_by(db.desc(sort_column))
        else:
            query = query.order_by(db.asc(sort_column))

        books = query.all()
    except Exception as e:
        return e
    return render_template("home.html",
                           books=books,
                           search_term=search_query,
                           current_sort=sort_by,
                           current_dir=direction)


@app.route('/delete_book/<int:book_id>', methods=['POST'])
def delete_book(book_id):
    try:
        book = db.session.query(Book).get(book_id)
        if book:
            author_id = book.author_id  # Save the ID before the book is gone
            book_title = book.book_title

            # 1. Delete the book
            db.session.delete(book)
            db.session.commit()  # Commit so the database updates the count

            # 2. Check if the author has any OTHER books left
            remaining_books_count = db.session.query(Book).filter(Book.author_id == author_id).count()

            if remaining_books_count == 0:
                author_to_delete = Author.query.get(author_id)
                if author_to_delete:
                    db.session.delete(author_to_delete)
                    db.session.commit()
                    flash(
                        f"Book '{book_title}' and author '{author_to_delete.author_name}' (who had no other books) were removed.",
                        "success")
            else:
                flash(f"Book '{book_title}' deleted.", "success")

    except Exception as e:
        db.session.rollback()
        flash(f"Error: {str(e)}", "danger")
    return redirect(url_for('home'))


@app.route('/author/<int:author_id>')
def author_profile(author_id):
    try:
        # 1. Fetch the author.
        # joinedload('books') grabs all their books in one go!
        author = Author.query.options(db.joinedload(Author.books)).get(author_id)

        if not author:
            flash("Author not found.", "danger")
            return redirect(url_for('home'))

        return render_template("author.html", author=author)
    except Exception as e:
        return e


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5002, debug=True)