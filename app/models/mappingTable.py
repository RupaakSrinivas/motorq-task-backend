from app import db
from datetime import datetime

class MappingTable(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    request_id = db.Column(db.Integer, db.ForeignKey('assignment_request.id'), nullable=False)
    driver_id = db.Column(db.Integer, db.ForeignKey('driver.id'), nullable=False)

    def __repr__(self):
        return f'<AssignmentRequest {self.id}>'