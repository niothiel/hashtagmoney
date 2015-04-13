from flask import Flask, jsonify, request
import datetime

from models import Session, Debt
import schemas

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
@schemas.require(schemas.DEBT)
def add_a_debt():
    data = request.json

    # Convert the date into a date object.
    date = datetime.datetime.fromtimestamp(data['date'] / 1000).date()

    debt = Debt(data['name'], data['owed_to'], data['amount'], date, data['notes'], data['image'])
    session = Session()
    session.add(debt)
    session.commit()

    response = jsonify({'debt': debt.to_public_dict()})
    session.close()
    return response


@app.errorhandler(404)
def not_found(error):
    print error
    return jsonify({'error': 'Not found'}), 404


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
