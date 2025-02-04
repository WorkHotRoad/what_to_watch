import csv
from datetime import datetime
from pathlib import Path
from random import \
    randrange  # Импортируется функция выбора случайного значения

import click
from flask import Flask, abort, flash, redirect, render_template, url_for
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, URLField
from wtforms.validators import DataRequired, Length, Optional

BASE_DIR = Path(__file__).parent

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + f'{BASE_DIR}/db.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'MY SECRET KEY'

db = SQLAlchemy(app)
migrate = Migrate(app, db)

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
    # Новое поле
    added_by = db.Column(db.String(64))


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
    added_by = StringField(
        'автор описания',
        validators=[Length(4, 70), Optional()]
    )
    submit = SubmitField('Добавить')



@app.errorhandler(404)
def page_not_found(error):
    # В качестве ответа возвращается собственный шаблон
    # и код ошибки
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    # В таких случаях можно откатить незафиксированные изменения в БД
    db.session.rollback()
    return render_template('500.html'), 500


@app.route('/')
def index_view():
    # Определяется количество мнений в базе данных
    quantity = Opinion.query.count()
    # Если мнений нет,
    if not quantity:
        # то возвращается сообщение
        # return 'В базе данных мнений о фильмах нет.'
        abort(404)
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
        text = form.text.data
         # Если в БД уже есть мнение с текстом, который ввёл пользователь,
        if Opinion.query.filter_by(text=text).first() is not None:
            # вызвать функцию flash и передать соответствующее сообщение
            flash('Такое мнение уже было оставлено ранее!', 'free-message') # free-message - это категория flash сообщения(для шаблона), если flash не один
            # и вернуть пользователя на страницу «Добавить новое мнение»
            return render_template('add_opinion.html', form=form)
        # нужно создать новый экземпляр класса Opinion
        opinion = Opinion(
            title=form.title.data,
            text=form.text.data,
            source=form.source.data,
            added_by = form.added_by.data
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


@app.cli.command('load_opinions')
def load_opinions_command():
    """Функция загрузки мнений в базу данных."""
    # Открывается файл
    with open('opinions.csv', encoding='utf-8') as f:
        # Создаётся итерируемый объект, который отображает каждую строку
        # в качестве словаря с ключами из шапки файла
        reader = csv.DictReader(f)
        # Для подсчёта строк добавляется счётчик
        counter = 0
        for row in reader:
            # Распакованный словарь можно использовать
            # для создания объекта мнения
            opinion = Opinion(**row)
            # Изменения нужно зафиксировать
            db.session.add(opinion)
            db.session.commit()
            counter += 1
    click.echo(f'Загружено мнений: {counter}')
    # Если пользовательская команда подразумевает вывод текстовых данных в консоль или файл,
    # рекомендуется использовать функцию click.echo(), а не print().
    # Функция click.echo() корректно работает с Unicode в Windows.


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

        # Миграции
#  Для SQLAlchemy была разработана специальная библиотека миграции баз данных — Alembic.
#  Для приложений на Flask существует её обёртка — модуль Flask-Migrate.
#  Именно с ней вам и предстоит сейчас поработать.
#  pip install Flask-Migrate==3.1.0
    #  from flask_migrate import Migrate
    # db = SQLAlchemy(app)
    # migrate = Migrate(app, db)
# Создайте репозиторий с помощью команды: flask db init
# Репозиторий миграций создаётся один раз.
# Все созданные папки и файлы миграций становятся частью проекта
# и их нельзя игнорировать при работе с системами управления версий, например, с Git.
#  после этого можно менять модеди
#  flask db migrate -m "added added_by field"
# Опциональный параметр -m позволяет добавить короткий комментарий к создаваемой миграции.
# Старайтесь добавлять такие комментарии, потом будет легче ориентироваться в созданных миграциях.
#  flask db upgrade


# Собственная команда
# Чтобы создать собственную команду для приложения на Flask,
# нужно описать соответствующую функцию в коде проекта и применить к ней декоратор @app.cli.command().
    # Декоратор @app.cli.command() первым аргументом принимает строку, которая используется как имя команды.
    # Если имя не задано, оно генерируется из названия функции. Например,
    # для функции hello_command автоматически сгенерируется имя команды hello-command.

# Также каждой команде можно дать описание.
# Описание — это докстринг соответствующей функции.
# Например, если в терминале вызвать команду flask

        # (venv) flask

        # ...
        # Commands:
        #   db          Perform database migrations
        #   routes      Show the routes for the app.
        #   run         Run a development server.
        #   shell       Run a shell in the app context.
