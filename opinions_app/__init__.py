from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from settings import Config

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)

from . import api_views, cli_commands, error_handlers, views

# Обратите внимание на расположение импортов в файле: часть из них находится в начале кода, часть в конце.
# Это сделано намеренно. Дело в том, что подключаемые в самом конце модули опираются в своей работе на те экземпляры классов,
# которые созданы выше. Если подключить эти модули до создания экземпляров классов, то ничего работать не будет.
