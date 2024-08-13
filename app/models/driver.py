from app import db

class Driver(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    work_start_time = db.Column(db.Time, nullable=False)
    work_end_time = db.Column(db.Time, nullable=False)
    location = db.Column(db.String(100), nullable=False)

    assignments = db.relationship('Assignment', back_populates='driver')

    def __repr__(self):
        return f'<Driver {self.name}>'