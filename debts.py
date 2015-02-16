from flask import Flask, jsonify, request, abort, send_from_directory
import os
import json
import datetime
from sqlalchemy.orm import sessionmaker, class_mapper
from sqlalchemy import create_engine, Column, Integer, String, Date
from sqlalchemy.ext.declarative import declarative_base

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DB_PATH = os.path.join(BASE_DIR, 'debts.db')

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

    debt = Debt(data['name'], data['owed_to'], data['amount'], date, data['notes'])
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


class Debt(Base):
    __tablename__ = 'debts'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    owed_to = Column(String)
    amount = Column(Integer)
    date = Column(Date)
    notes = Column(String)

    def __init__(self, name, owed_to, amount, date, notes):
        if not isinstance(date, datetime.date):
            raise AssertionError('Date is supposed to be an instance of date.')

        self.name = name
        self.owed_to = owed_to
        self.amount = amount
        self.date = date
        self.notes = notes

    def to_public_dict(self):
        print self.date
        the_date = datetime.datetime(self.date.year, self.date.month, self.date.day)
        total_seconds = (the_date - datetime.datetime(1970, 1, 1)).total_seconds()

        return {
            'id': self.id,
            'name': self.name,
            'owed_to': self.owed_to,
            'amount': self.amount,
            'date': int(total_seconds * 1000),
            'notes': self.notes
        }


Base.metadata.create_all(engine)


def add_sample_data():
    session = Session()
    if session.query(Debt).count() == 0:
        d1 = Debt('Marty', 'Val', 300, datetime.date.today(), 'This is the first test.')
        session.add(d1)
        session.commit()
    session.close()


if __name__ == '__main__':
    add_sample_data()
    app.run(host='0.0.0.0', debug=True)
