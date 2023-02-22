from flask import jsonify, request

from . import app, db
from .models import Opinion
import random
from .views import random_opinion


# Явно разрешить метод GET
@app.route('/api/opinions/<int:id>/', methods=['GET'])
def get_opinion(id):
    # Получить объект по id или выбросить ошибку
    opinion = Opinion.query.get_or_404(id)
    # Конвертировать данные в JSON и вернуть объект и код ответа API
    return jsonify({'opinion': opinion.to_dict()}), 200


@app.route('/api/opinions/<int:id>/', methods=['PATCH'])
def update_opinion(id):
    data = request.get_json()
    if (
        'text' in data and 
        Opinion.query.filter_by(text=data['text']).first() is not None
    ):
        # При неуникальном значении поля text
        # возвращаем сообщение об ошибке в формате JSON 
        # и статус-код 400
        return jsonify({'error': 
                        'Такое мнение уже есть в базе данных'}), 400
    opinion = Opinion.query.get_or_404(id)
    # Если метод get_or_404 не найдёт указанный ключ,
    # то он выбросит исключение 404
    opinion.title = data.get('title', opinion.title)
    opinion.text = data.get('text', opinion.text)
    opinion.source = data.get('source', opinion.source)
    opinion.added_by = data.get('added_by', opinion.added_by)
    # Все изменения нужно сохранить в базе данных
    db.session.commit()
    # При создании или изменении объекта вернём сам объект и код 201
    return jsonify({'opinion': opinion.to_dict()}), 201

@app.route('/api/opinions/<int:id>/', methods=['DELETE'])
def delete_opinion(id):
    opinion = Opinion.query.get_or_404(id)
    db.session.delete(opinion)
    db.session.commit()
    # При удалении принято возвращать только код ответа 204
    return '', 204

@app.route('/api/opinions/', methods=['GET'])
def get_opinions():
    # Запрашивается список объектов
    opinions = Opinion.query.all()
    # Поочерёдно сериализуется каждый объект,
    # а потом все объекты помещаются в список opinions_list
    opinions_list = [opinion.to_dict() for opinion in opinions]
    return jsonify({'opinions': opinions_list}), 200

@app.route('/api/opinions/', methods=['POST'])
def add_opinion():
    # Получение данные из запроса в виде словаря
    data = request.get_json()
    # Если нужных ключей нет в словаре,
    if 'title' not in data or 'text' not in data:
        # ...то возвращаем сообщение об ошибке в формате JSON и код 400:
        return jsonify({'error':
                        'В запросе отсутствуют обязательные поля'}), 400
    # Если в базе данных уже есть объект 
    # с таким же значением поля text
    if Opinion.query.filter_by(text=data['text']).first() is not None:
        # ...возвращаем сообщение об ошибке в формате JSON 
        # и статус-код 400
        return jsonify({'error': 
                        'Такое мнение уже есть в базе данных'}), 400
    # Создание нового пустого экземпляра модели
    opinion = Opinion()
    # Наполнение его данными из запроса 
    opinion.from_dict(data)
    # Добавление новой записи в базу данных
    db.session.add(opinion)
    # Сохранение изменений
    db.session.commit()
    return jsonify({'opinion': opinion.to_dict()}), 201

@app.route('/api/get-random-opinion/', methods=['GET'])
def get_random_opinion():
    # мое решение без доп функций
    # opinions = Opinion.query.all()
    # list_id = [x.id for x in opinions]
    # id = random.choice(list_id)
    # opinion_random = Opinion.query.get_or_404(id)
    # return jsonify({'opinion': opinion_random.to_dict()}), 200

    # не мое решение
    # тут создается отдельная ф-я в views -random_opinion()
    opinion = random_opinion()
    return jsonify({'opinion': opinion.to_dict()}), 200 

