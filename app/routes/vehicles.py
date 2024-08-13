from flask import Blueprint, request, jsonify
from app import db
from app.models.vehicle import Vehicle
from app.models.driver import Driver
from app.models.vehicle_driver import Assignment

bp = Blueprint('vehicles', __name__)


@bp.route('/vehicles', methods=['GET'])
def show_vehicles():

    make = request.args.get('make')
    model = request.args.get('model')
    plate_number = request.args.get('plate_number')

    vehicles = Vehicle.query
    assignment_request = Assignment.query

    if make:
        vehicles = vehicles.filter(Vehicle.make.ilike(f'%{make}%'))

    if model:
        vehicles = vehicles.filter(Vehicle.model.ilike(f'%{model}%'))

    if plate_number:
        vehicles = vehicles.filter(Vehicle.plate_number.ilike(f'%{plate_number}%'))

    if vehicles.count() == 0:
        return jsonify({'status': 'error', 'message': 'No vehicles found'}), 404

    return jsonify([{
        'id': vehicle.id,
        'make': vehicle.make,
        'model': vehicle.model,
        'plate_number': vehicle.plate_number,
    } for vehicle in vehicles]), 200