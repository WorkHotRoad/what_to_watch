from datetime import datetime

from . import db


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

    def to_dict(self):
        return dict(
            id=self.id,
            title=self.title,
            text=self.text,
            source=self.source,
            timestamp=self.timestamp,
            added_by=self.added_by
        )

    # Добавляем в модель метод-десериализатор.
    # На вход метод принимает словарь data, полученный из JSON в запросе
    def from_dict(self, data):
        # Для каждого поля модели, которое можно заполнить...
        for field in ['title', 'text', 'source', 'added_by']:
            # ...выполняется проверка: есть ли ключ с таким же именем в словаре
            if field in data:
                # Если есть — добавляем значение из словаря
                # в соответствующее поле объекта модели:
                setattr(self, field, data[field])
