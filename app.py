from base64 import b64decode
from flask import Flask, jsonify, request, abort
from uuid import uuid4
import datetime
import json
import os
import re

from models import Session, Debt
import config

app = Flask(__name__, static_url_path='')


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
    session.close()

    return jsonify({'debt': debt.to_public_dict()})


@app.errorhandler(404)
def not_found(error):
    print error
    return jsonify({'error': 'Not found'}), 404


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
