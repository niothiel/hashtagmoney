from flask import Flask, jsonify, request, abort, send_from_directory
import os
import json
import datetime
import re
from uuid import uuid4
from base64 import b64decode
from sqlalchemy.orm import sessionmaker, class_mapper
from sqlalchemy import create_engine, Column, Integer, String, Date
from sqlalchemy.ext.declarative import declarative_base

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
IMAGE_DIR = os.path.join(BASE_DIR, 'images')
DB_PATH = os.path.join(BASE_DIR, 'debts.db')

if not os.path.exists(IMAGE_DIR):
    os.mkdir(IMAGE_DIR)

engine = create_engine('sqlite:///' + DB_PATH, echo=True)
Base = declarative_base()
Session = sessionmaker(bind=engine)

app = Flask(__name__)


@app.route('/')
def send_index():
    return app.send_static_file('index.html')

@app.route('/api/debts', methods=['GET'])
def get_all_debts():
    session = Session()
    debts = session.query(Debt).all()
    serialized = [model.to_public_dict() for model in debts]

    return jsonify({'debts': serialized})


@app.route('/api/debts', methods=['POST'])
def add_a_debt():
    def save_image(encoded_data):
        if not encoded_data: return None

        ext, data = re.match('data:image/(\w+);base64,(.*)$', encoded_data).groups()
        name = '{}.{}'.format(uuid4(), ext)
        path = os.path.join(IMAGE_DIR, name)

        with open(path, 'wb') as fout:
            fout.write(b64decode(data))

        return name

    if not request.json:
        abort(400)

    data = request.json
    if 'name' not in data or \
        'owed_to' not in data or \
        'amount' not in data or \
        'date' not in data:
        abort(400)

    # Convert the date into a date object.
    date = datetime.datetime.fromtimestamp(data['date'] / 1000).date()

    # Save the image to a specific directory.
    image_name = save_image(data['image'])

    debt = Debt(data['name'], data['owed_to'], data['amount'], date, data['notes'], image_name)
    session = Session()
    session.add(debt)
    session.commit()

    return_value = jsonify({'debt': debt.to_public_dict()})
    session.close()
    return return_value


@app.errorhandler(404)
def not_found(error):
    print error
    return jsonify({'error': 'Not found'}), 404


@app.route('/js/<path:path>')
def send_js(path):
    return send_from_directory(os.path.join(BASE_DIR, 'static/js'), path)


@app.route('/css/<path:path>')
def send_css(path):
    return send_from_directory(os.path.join(BASE_DIR, 'static/css'), path)


@app.route('/images/<path:path>')
def send_images(path):
    return send_from_directory(IMAGE_DIR, path)


class Debt(Base):
    __tablename__ = 'debts'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    owed_to = Column(String)
    amount = Column(Integer)
    date = Column(Date)
    notes = Column(String)
    image_name = Column(String)

    def __init__(self, name, owed_to, amount, date, notes, image_name):
        if not isinstance(date, datetime.date):
            raise AssertionError('Date is supposed to be an instance of date.')

        self.name = name
        self.owed_to = owed_to
        self.amount = amount
        self.date = date
        self.notes = notes
        self.image_name = image_name

    def to_public_dict(self):
        the_date = datetime.datetime(self.date.year, self.date.month, self.date.day)
        total_seconds = (the_date - datetime.datetime(1970, 1, 1)).total_seconds()
        total_millis = int(total_seconds * 1000)

        return {
            'id': self.id,
            'name': self.name,
            'owed_to': self.owed_to,
            'amount': self.amount,
            'date': total_millis,
            'notes': self.notes,
            'image_path': os.path.join('/images/', self.image_name) if self.image_name else None
        }


Base.metadata.create_all(engine)


def add_sample_data():
    session = Session()
    if session.query(Debt).count() == 0:
        d1 = Debt('Marty', 'Val', 300, datetime.date.today(), 'This is the first test.', None)
        session.add(d1)
        session.commit()
    session.close()


if __name__ == '__main__':
    add_sample_data()
    app.run(host='0.0.0.0', debug=True)
