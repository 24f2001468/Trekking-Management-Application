from flask import Blueprint

# Placeholder blueprint
routes_file2 = Blueprint('routes_file2', __name__)

@routes_file2.route('/api/file2')
def file2_endpoint():
    return {"message": "Hello from file2 route"}
