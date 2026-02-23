from flask import Flask, render_template, request, flash, redirect, url_for
from sqlalchemy import create_engine, asc, desc, or_
from sqlalchemy.orm import sessionmaker, joinedload
from data_models import db, Author, Book
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

# Create a database connection
engine = create_engine('sqlite:///data/library.sqlite')

# Create a database session
Session = sessionmaker(bind=engine)

@app.route('/add_author', methods=['GET','POST'])
def add_author():

    if request.method == 'POST':

        session = Session()

        # Create an instance of the Restaurant table class
        author = Author(
            author_name = request.form['name'],
            birth_date= request.form['birthdate'],
            date_of_death= request.form['date_of_death'],
        )

        # Since the session is already open, add the new restaurant record
        session.add(author)
        session.commit()
        return f"Author {author} added successfully", 200
    return render_template("add_author.html")


@app.route('/add_book', methods=['GET','POST'])
def add_book():

    if request.method == 'POST':
        # Create a database connection
        engine = create_engine('sqlite:///data/library.sqlite')

        # Create a database session
        Session = sessionmaker(bind=engine)
        session = Session()
        # Create an instance of the Restaurant table class
        book = Book(
            book_title = request.form['title'],
            publication_year= request.form['publication_year'],
            author_id= request.form['author_id'],
            isbn= request.form['isbn'],
        )

        # Since the session is already open, add the new restaurant record
        session.add(book)
        session.commit()
        books = session.query(Book).all()
        return render_template("home.html",books=books)
    # GET logic: Fetch all authors to populate the dropdown
    engine = create_engine('sqlite:///data/library.sqlite')
    Session = sessionmaker(bind=engine)
    session = Session()
    authors = session.query(Author).all()
    session.close()
    return render_template("add_book.html", authors=authors)



@app.route('/')
def home():
    session = Session()

    # Get 'sort' and 'direction' from the URL (defaults to title/asc)
    sort_by = request.args.get('sort', 'book_title')
    direction = request.args.get('direction', 'asc')

    try:
        # Start the query
        query = session.query(Book).join(Author).options(joinedload(Book.author))

        # Determine the sorting column
        if sort_by == 'author':
            sort_column = Author.author_name
        else:
            sort_column = getattr(Book, sort_by, Book.book_title)

        # Apply sorting
        if direction == 'desc':
            query = query.order_by(desc(sort_column))
        else:
            query = query.order_by(asc(sort_column))

        books = query.all()
    finally:
        session.close()

    return render_template("home.html", books=books, current_sort=sort_by, current_dir=direction)

@app.route('/search')
def search():
    session = Session()

    # 1. Get the search term from the URL (e.g., /?search=Python)
    search_query = request.args.get('search', '')

    # 2. Build the base query with Joinedload (to avoid the DetachedInstanceError)
    query = session.query(Book).join(Author).options(joinedload(Book.author))

    # 3. If there is a search term, apply the filter
    if search_query:
        # ilike makes it case-insensitive (Search 'python' finds 'Python')
        # The % symbols are wildcards (search anywhere in the string)
        search_filter = f"%{search_query}%"
        query = query.filter(
            or_(
                Book.book_title.ilike(search_filter),
                Author.author_name.ilike(search_filter)
            )
        )

    # 4. Execute and close
    books = query.all()
    session.close()
    return render_template("home.html", books=books, search_term=search_query)


@app.route('/delete_book/<int:book_id>', methods=['POST'])
def delete_book(book_id):
    session = Session()
    try:
        book = session.query(Book).get(book_id)
        if book:
            author_id = book.author_id  # Save the ID before the book is gone
            book_title = book.book_title

            # 1. Delete the book
            session.delete(book)
            session.commit()  # Commit so the database updates the count

            # 2. Check if the author has any OTHER books left
            remaining_books_count = session.query(Book).filter(Book.author_id == author_id).count()

            if remaining_books_count == 0:
                author_to_delete = session.query(Author).get(author_id)
                if author_to_delete:
                    session.delete(author_to_delete)
                    session.commit()
                    flash(
                        f"Book '{book_title}' and author '{author_to_delete.author_name}' (who had no other books) were removed.",
                        "success")
            else:
                flash(f"Book '{book_title}' deleted.", "success")

    except Exception as e:
        session.rollback()
        flash(f"Error: {str(e)}", "danger")
    finally:
        session.close()
    return redirect(url_for('home'))


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5002, debug=True)