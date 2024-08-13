from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import Config
from flask_cors import CORS
db = SQLAlchemy()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    CORS(app, support_credentials=True)

    from app.routes import drivers, vehicles, assignments, assignment_requests
    app.register_blueprint(drivers.bp)
    app.register_blueprint(vehicles.bp)
    app.register_blueprint(assignments.bp)
    app.register_blueprint(assignment_requests.bp)

    with app.app_context():
        db.create_all()
        db.session.commit()

    return app