from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy,Model
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
import requests

API_KEY = 'b46718e9dc97ccacf8da94c7adfcc5f6'
MDB_session = requests.get(f'https://api.themoviedb.org/3/authentication/guest_session/new?api_key={API_KEY})')


app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6WlSihBXox7C0sKR6b'
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///top_10_film.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
Bootstrap(app)
db = SQLAlchemy(app)


class Card(db.Model):

    id = db.Column(db.Integer,  primary_key=True)
    title = db.Column(db.String(200))
    year = db.Column(db.Integer)
    description = db.Column(db.String(250))
    rating = db.Column(db.Float)
    ranking = db.Column(db.Integer)
    review = db.Column(db.String(250))
    img_url = db.Column(db.String(250))


db.create_all()


class EditForm(FlaskForm):
    new_rating = StringField('Your Rating out of 10 e.g. ??')
    new_review = StringField('Your new review')
    submit = SubmitField()


class AddForm(FlaskForm):
    film_to_add = StringField('Name of new film')
    submit = SubmitField()


@app.route("/")
def home():
    all_movies = Card.query.order_by(Card.rating).all()
    for i in range(0, len(all_movies)):
        all_movies[i].ranking = len(all_movies) - i
    db.session.commit()
    return render_template("index.html", all_cards=all_movies)


@app.route('/edit', methods=["GET", "POST"])
def edit():
    form = EditForm()
    movie_id = request.args.get('id')
    if form.validate_on_submit():
        movie = Card.query.get(movie_id)
        new_rating = form.new_rating.data
        new_review = form.new_review.data
        movie.rating = new_rating
        movie.review = new_review
        db.session.commit()
        return redirect(url_for('home'))
    return render_template('edit.html', form=form, book=movie_id)


@app.route('/delete', methods=["GET", "POST"])
def delete():
    movie_id = request.args.get('id')
    movie = Card.query.get(movie_id)
    db.session.delete(movie)
    db.session.commit()
    return redirect(url_for('home'))


@app.route('/new_film', methods=["GET","POST"])
def add_card():
    form = AddForm()
    if form.validate_on_submit():
        film_name = form.film_to_add.data
        films = requests.get(f'https://api.themoviedb.org/3/search/movie?api_key={API_KEY}&language=en-US&query={film_name}&page=1&include_adult=false').json()
        return render_template('select.html', movie=films['results'], title=films['results'][0]['title'],
                               img_url=films['results'][0]['poster_path'], year_film=films['results'][0]['release_date'][0:4],
                               description=films['results'][0]['overview'])
    return render_template('add.html', form=form)


@app.route('/find', methods=["GET", "POST"])
def add_card_to_bd():
    new_card = Card()
    new_card.title = request.args.get('title')
    new_card.img_url = request.args.get('img_url')
    new_card.year = request.args.get('year_film')
    new_card.description = request.args.get('description')
    db.session.add(new_card)
    db.session.commit()
    new_book = Card.query.filter_by(title=request.args.get('title')).first()
    return redirect(url_for('edit', id=new_book.id))



if __name__ == '__main__':
    app.run(debug=True)
