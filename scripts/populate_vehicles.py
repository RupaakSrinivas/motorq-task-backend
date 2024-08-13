# scripts/populate_vehicles.py
import sys
import os

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from app.models.vehicle import Vehicle

def populate_vehicles():
    app = create_app()
    with app.app_context():
        vehicles_data = [
            {'make': 'Toyota', 'model': 'Camry', 'plate_number': 'ABC123'},
            {'make':'Honda', 'model': 'Civic', 'plate_number': 'XYZ789'},
            {'make':'Ford', 'model': 'F-150', 'plate_number': 'DEF456'},
            # Add more vehicles as needed
        ]

        for vehicle in vehicles_data:
            existing_vehicle = Vehicle.query.filter_by(plate_number=vehicle['plate_number']).first()
            if not existing_vehicle:
                new_vehicle = Vehicle(**vehicle)
                db.session.add(new_vehicle)

        db.session.commit()
        print("Vehicles data populated successfully.")

if __name__ == '__main__':
    populate_vehicles()