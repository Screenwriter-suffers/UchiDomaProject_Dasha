from datetime import datetime

from flask import Flask, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, SubmitField
from wtforms.validators import DataRequired, Length

import os

app = Flask(__name__)

basedir = os.path.abspath(os.path.dirname(__file__))

app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024 
app.config['SECRET_KEY'] = 'fjs923hd723ghs2'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'db.sqlite3')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    news = db.relationship('News', back_populates='category')

    def __repr__(self):
        return f'Category {self.id}: ({self.title})'


class News(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), unique=True, nullable=False)
    text = db.Column(db.Text, nullable=False)
    created_date = db.Column(db.DateTime, default=datetime.utcnow)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=True)
    category = db.relationship('Category', back_populates='news')

    def __repr__(self):
        return f'News {self.id}: ({self.title[:20]}...)'


#db.create_all()
#with app.app_context():
#    db.create_all()


def get_categories():
    with app.app_context():
        categories = Category.query.all()
        return [(category.id, category.title) for category in categories]


class NewsForm(FlaskForm):
    title = StringField(
        'Название',
        validators=[DataRequired(message="пустое поле = no-no-no"),
                    Length(max=255, message='Заголовок ≤ 255 символов')]
    )
    text = TextAreaField(
        'Текст',
        validators=[DataRequired(message="пустое поле = no-no-no")])
    category = SelectField('Категория', choices = []) #(choices=get_categories())
    submit = SubmitField('Добавитъ')


@app.route('/')
def index():
    news_list = News.query.all()
    categories = Category.query.all()
    return render_template('index.html',
                           news=news_list,
                           categories=categories)


@app.route('/news_detail/<int:id>')
def news_detail(id):
    news = News.query.get(id)
    categories = Category.query.all()
    return render_template('news_detail.html',
                           news=news,
                           categories=categories)


@app.route('/category/<int:id>')
def news_in_category(id):
    category = Category.query.get(id)
    news = category.news
    category_name = category.title
    categories = Category.query.all()
    return render_template('category.html',
                           news=news,
                           category_name=category_name,
                           categories=categories)


@app.route('/add_news', methods=['GET', 'POST'])
def add_news():
    form = NewsForm()
    form.category.choices = get_categories() 
    categories = Category.query.all()
    if form.validate_on_submit():
        news = News()
        news.title = form.title.data
        news.text = form.text.data
        news.category_id = form.category.data
        db.session.add(news)
        db.session.commit()
        return redirect(url_for('news_detail', id=news.id))
    return render_template('add_news.html',
                           form=form,
                           categories=categories)


@app.route('/VERY_OFICIAL')
def VERY_OFICIAL():
    return render_template('video.html')

@app.route('/back_home')
def back_home():
    return redirect(url_for('index', show_lol=1)) 


if __name__ == '__main__':
    with app.app_context():
        db.create_all() 
        if not Category.query.first(): 
            c1 = Category(title="Котики")
            c2 = Category(title="Мемчикc")
            c3 = Category(title="фу политика")
            c4 = Category(title="бьюти-щит")
            c5 = Category(title="...Слово ром и слово смерть...")
            c6 = Category(title=":|")
            db.session.add_all([c1, c2, c3, c4, c5, c6])
            db.session.commit()
            print("--- категории загружены ---")

        news_to_del = News.query.filter_by(title="").first()
        if news_to_del:
            db.session.delete(news_to_del)
            db.session.commit()
            print("--- НОВОСТЬ УДАЛЕНА ---")

    app.run(debug=True)
