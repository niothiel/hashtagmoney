from flask import abort, request
from jsonschema import validate

def require(schema):
    """Decorator for validating incoming request.json values.

    :param schema Object from this file representing a schema to use for the validation
    """
    def require_schema_decorator(func):
        def func_wrapper(*args, **kwargs):
            try:
                validate(request.json, schema)
            except Exception as e:
                print 'Failed validation:', e
                abort(400)

            return func(*args, **kwargs)
        return func_wrapper
    return require_schema_decorator

DEBT = {
    'type': 'object',
    'properties': {
        'name': {'type': 'string'},
        'owed_to': {'type': 'string'},
        'amount': {'type': 'number'},
        'date': {'type': 'number'},
        'image': {'type': ['string', 'null']},
    },
    'required': [ 'name', 'owed_to', 'amount', 'date', 'image' ],
}
