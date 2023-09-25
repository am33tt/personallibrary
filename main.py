from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_bootstrap import Bootstrap5
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, EmailField
from wtforms.validators import DataRequired, Email, EqualTo, Length
from flask_sqlalchemy import SQLAlchemy
import os, datetime

app = Flask(__name__)
Bootstrap5(app) 

app.secret_key = os.environ.get('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///books-database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Email(message='Invalid Email')] )
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8, max=16, message='Password must be between 8 and 16 characters')])
    submit = SubmitField('Log In')


class SignUpForm(FlaskForm):
    email = EmailField('Username',validators=[DataRequired(), Email()])
    username = StringField('Username',validators=[DataRequired()])
    password = PasswordField('Password',validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password',validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')


class AddForm(FlaskForm):
    book_name = StringField('Book Name', validators=[DataRequired()])
    author = StringField('Author', validators=[DataRequired()])
    genre = StringField('Genre', validators=[DataRequired()])
    rating = StringField('Rating', validators=[DataRequired()])
    submit = SubmitField('Add Book')

class Book(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        date_added = db.Column(db.String(250), nullable=False)
        book_name = db.Column(db.String(250), unique=True, nullable=False)
        author = db.Column(db.String(250), nullable=False)
        genre = db.Column(db.String(250), nullable=False)
        rating = db.Column(db.Float, nullable=False)
                       
#HomePage
@app.route('/', methods=['GET', 'POST'])
def index():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        if username == 'test@gmail.com' and password == '12345678':
            flash('You have been logged in!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Login Unsuccessful. Please check username and password', 'danger')
    return render_template('login.html', form=form)

#SignUp Page
@app.route('/signup')
def signup():
    form = SignUpForm()
    return render_template('signup.html', form=form)


#LoginDashboard
@app.route('/dashboard')
def dashboard():
    result = db.session.execute(db.select(Book).order_by(Book.book_name))
    # Use .scalars() to get the elements rather than entire rows from the database
    all_books = result.scalars()
    return render_template('dashboard.html', books=all_books )


#add a New Book
@app.route('/add', methods=['GET', 'POST'])
def add():
    form = AddForm()
    if form.validate_on_submit():
        date = datetime.datetime.now().strftime("%Y-%m-%d")
        book = form.book_name.data
        author = form.author.data
        genre = form.genre.data
        rating = form.rating.data
        with app.app_context():
            new_book = Book(date_added=date, book_name=book, author=author,genre=genre, rating=rating)
            db.session.add(new_book)
            db.session.commit()
        flash('You have been logged in!', 'success')
        return redirect(url_for('dashboard'))

    return render_template('add.html', form=form)

#Create a DB
@app.route('/createdb', methods=['GET', 'POST'])
def createdb():
    with app.app_context():
        db.create_all()
    return 'Database Created Successfully'
    

@app.route('/delete/<id>', methods=['GET', 'POST'])
def delete(id):
    with app.app_context():
        book_to_delete = db.session.execute(db.select(Book).where(Book.id == id)).scalar()
        # or book_to_delete = db.get_or_404(Book, book_id)
        db.session.delete(book_to_delete)
        db.session.commit()
    return redirect(url_for('dashboard'))

@app.route('/edit/<id>', methods=['GET', 'POST'])
def edit(id):
    with app.app_context():
        book_to_edit = db.session.execute(db.select(Book).where(Book.id == id)).scalar()
        # or book_to_edit = db.get_or_404(Book, book_id)
        form = AddForm(
            book_name=book_to_edit.book_name,
            author=book_to_edit.author,
            genre=book_to_edit.genre,
            rating=book_to_edit.rating
        )
        if form.validate_on_submit():
            book_to_edit.book_name = form.book_name.data
            book_to_edit.author = form.author.data
            book_to_edit.genre = form.genre.data
            book_to_edit.rating = form.rating.data
            db.session.commit()
            return redirect(url_for('dashboard'))
    return render_template('edit.html', form=form)

@app.route('/search', methods=['POST'])
def search():
    result = db.session.execute(db.select(Book).order_by(Book.book_name))
    # Use .scalars() to get the elements rather than entire rows from the database
    all_books = result.scalars()
    search_query = request.form.get('searchQuery').lower()
    filtered_data = [item for item in all_books if search_query in item['name'].lower()]
    return jsonify(filtered_data)

if __name__ == '__main__':
    app.run(debug=True)