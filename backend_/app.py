from flask import Flask
from flask_cors import CORS
from app.db import db, init_db
from app.routes.auth_routes import auth_routes
from app.routes.test_routes import test_routes
from app.routes.cpp_learning import cpp_learning
from app.routes.moderate import moderate_learning
from app.routes.advanced import advanced_learning  # Add this line

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:nikhil@localhost/Language_Learning'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    init_db(app)
    CORS(app)

    # Register Blueprints
    app.register_blueprint(auth_routes, url_prefix='/auth')
    app.register_blueprint(test_routes, url_prefix='/test')
    app.register_blueprint(cpp_learning, url_prefix='/cpp_learning')
    app.register_blueprint(moderate_learning, url_prefix='/moderate')
    app.register_blueprint(advanced_learning, url_prefix='/advanced')  # Add this line

    @app.errorhandler(404)
    def not_found_error(error):
        return {"error": "Resource not found"}, 404

    return app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True)