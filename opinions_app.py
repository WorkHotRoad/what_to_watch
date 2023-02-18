from datetime import datetime
from random import randrange # Импортируется функция выбора случайного значения

from flask import Flask, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, URLField
from wtforms.validators import DataRequired, Length, Optional

from pathlib import Path

BASE_DIR = Path(__file__).parent

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + f'{BASE_DIR}/db.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'MY SECRET KEY'

db = SQLAlchemy(app)


class Opinion(db.Model):
    # ID — целое число, первичный ключ
    id = db.Column(db.Integer, primary_key=True)
    # Название фильма — строка длиной 128 символов, не может быть пустым
    title = db.Column(db.String(128), nullable=False)
    # Мнение о фильме — большая строка, не может быть пустым,
    # должно быть уникальным
    text = db.Column(db.Text, unique=True, nullable=False)
    # Ссылка на сторонний источник — строка длиной 256 символов
    source = db.Column(db.String(256))
    # Дата и время — текущее время,
    # по этому столбцу база данных будет проиндексирована
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)


class OpinionForm(FlaskForm):
    title = StringField(
        'Введите название фильма',
        validators=[DataRequired(message='Обязательное поле'),
                    Length(1, 128)]
    )
    text = TextAreaField(
        'Напишите мнение',
        validators=[DataRequired(message='Обязательное поле')]
    )
    source = URLField(
        'Добавьте ссылку на подробный обзор фильма',
        validators=[Length(1, 256), Optional()]
    )
    submit = SubmitField('Добавить')


@app.route('/')
def index_view():
    # Определяется количество мнений в базе данных
    quantity = Opinion.query.count()
    # Если мнений нет,
    if not quantity:
        # то возвращается сообщение
        return 'В базе данных мнений о фильмах нет.'
    # Иначе выбирается случайное число в диапазоне от 0 и до quantity
    offset_value = randrange(quantity)
    # И определяется случайный объект
    opinion = Opinion.query.offset(offset_value).first()
    return render_template('opinion.html', opinion=opinion)


@app.route('/add', methods=['GET', 'POST'])
def add_opinion_view():
    form = OpinionForm()
    # Если ошибок не возникло, то
    if form.validate_on_submit():
        # нужно создать новый экземпляр класса Opinion
        opinion = Opinion(
            title=form.title.data,
            text=form.text.data,
            source=form.source.data
        )
        # Затем добавить его в сессию работы с базой данных
        db.session.add(opinion)
        # И зафиксировать изменения
        db.session.commit()
        # Затем перейти на страницу добавленного мнения
        return redirect(url_for('opinion_view', id=opinion.id))
    return render_template('add_opinion.html', form=form)


@app.route('/opinions/<int:id>')
def opinion_view(id):
    # Теперь можно запрашивать мнение по id
    opinion = Opinion.query.get_or_404(id)
    # И передавать его в шаблон
    return render_template('opinion.html', opinion=opinion)

if __name__ == '__main__':
    app.run()

# запуск проэкта
# В корневой директории проекта создайте файл .env и определите в нём переменные окружения:
# FLASK_APP=opinions_app
# FLASK_ENV=development
# flask run


# для создания базы авходим в интерактивную оболочку flask (flask shell)
# для выхода используется exit()
# >>> from opinions_app import db
# >>> db.create_all()
#
# Метод create_all() создаёт базу данных, если её ещё нет в проекте, а если база есть, то создаются таблицы в ней.
# Метод не сработает, если в проекте есть и база, и таблицы; также он не подойдёт для обновления существующей базы, если модели изменятся.
# Чтобы удалить все таблицы и данные в подключённой базе данных, используется метод drop_all(). Сама база при этом останется.
# >>>db.drop_all()
# Чтобы создать новую запись в таблице, нужно импортировать класс Opinion и создать его экземпляр, в котором будет как минимум два обязательных поля: название фильма — title и мнение — text.
# >>> opinion1 = Opinion(title='Джой', text='Фильм обязателен.......
# Объект opinion1 — это ещё не запись в базе, а просто объект в памяти (на это указывает слово transient в предыдущем листинге). Если вы сейчас выйдете из интерактивной оболочки, то все ваши труды будут напрасны — база так и останется пустой. Чтобы объект сохранился, нужно добавить его в сессию работы с базой данных и сделать коммит, зафиксировать изменения.
# >>> db.session.add(opinion1)
# >>> db.session.commit()

# Получение и изменение данных с помощью ORM-запросов

# Интерактивная оболочка Flask позволяет не только создавать объекты, но и выполнять ORM-запросы. Например, если известен id конкретного мнения, то с помощью метода get() можно получить соответствующий объект из базы данных.
# opinion1 = Opinion.query.get(1)
# Информацию об объектах можно не только получать, но и изменять. Для того чтобы поменять значение поля в уже существующем объекте, нужно задать для этого поля новое значение и сделать коммит.
# >>> opinion1.title='Джой (2015)'
# >>> db.session.commit()
# Для удаления конкретных данных из таблицы, нужно в метод delete() передать экземпляр класса, в котором хранятся эти данные, и сделать коммит.
# >>> db.session.delete(opinion1)
# >>> db.session.commit()

# Работа с выборками
# По умолчанию у всех моделей в ORM есть атрибут query
# Далее вы можете использовать методы all(), get() и другие, при помощи которых можно не только получать отдельные объекты, но и формировать различные выборки из них.
# Opinion.query.all()
# В ответ вы получите список объектов. А раз это список, значит по нему можно итерироваться и получать значения нужных полей
# >>> result = Opinion.query.all()
# >>> for opinion in result:
# >>>...  opinion.text
# Размер итоговой выборки можно ограничивать.
# запрос можно сформировать с помощью метода limit()
# Opinion.query.limit(2).all()
# А можно и исключать указанное количество элементов из выборки при помощи метода offset()
# >>> Opinion.query.offset(2).all()
# # Выведется:
# [<Opinion 3>]
#  Также эти методы можно применять одновременно:
# >>> Opinion.query.offset(1).limit(1).all()
