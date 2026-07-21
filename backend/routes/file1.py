from flask import Blueprint

# Placeholder blueprint
routes_file1 = Blueprint('routes_file1', __name__)

@routes_file1.route('/api/file1')
def file1_endpoint():
    return {"message": "Hello from file1 route"}
