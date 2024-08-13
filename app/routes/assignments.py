from flask import Blueprint, request, jsonify
from app import db
from app.models.vehicle_driver import Assignment
from app.models.driver import Driver
from app.models.vehicle import Vehicle
from datetime import datetime

bp = Blueprint('assignments', __name__)

# @bp.route('/assignments', methods=['POST'])
# def create_assignment():
#     data = request.json
#     driver_id = data['driver_id']
#     vehicle_id = data['vehicle_id']
#     start_time = data['start_time']
#     end_time = data['end_time']

#     driver = Driver.query.get(driver_id);
#     vehicle = Vehicle.query.get(vehicle_id);

#     if Driver.query.get(driver_id) is None:
#         return jsonify({'status': 'error', 'message': 'No driver found with this id'}), 404
    
#     if Vehicle.query.get(vehicle_id) is None:
#         return jsonify({'status': 'error', 'message': 'No vehicle found with this id'}), 404

#     conflicts = Assignment.query.filter(
#         Assignment.vehicle_id == vehicle_id,
#         Assignment.start_time < end_time,
#         Assignment.end_time > start_time
#     ).all()

#     if driver.work_start_time > datetime.fromisoformat(start_time).time() or driver.work_end_time < datetime.fromisoformat(end_time).time():
#         return jsonify({'status':'error', 'message': 'Assignment hours outside of driver working hours'}), 400
#     if conflicts:
#         return jsonify({'status': 'error', 'message': 'Vehicle or Driver is already assigned during this time period'}), 400

#     new_assignment = Assignment(driver_id=driver_id, vehicle_id=vehicle_id, 
#                                 start_time=start_time, end_time=end_time)
#     db.session.add(new_assignment)
#     db.session.commit()

#     return jsonify({'status':'success', 'message': 'Assignment created successfully'}), 201



@bp.route('/assignments', methods=['GET'])
def get_assignments():
    driver_id = request.args.get('driver_id', type=int)
    vehicle_id = request.args.get('vehicle_id', type=int)
    start_time = request.args.get('start_time')
    end_time = request.args.get('end_time')

    query = Assignment.query

    if driver_id:
        if Driver.query.get(driver_id) is None:
            return jsonify({'status': 'error', 'message': 'No driver found with this id'}), 404
        query = query.filter(Assignment.driver_id == driver_id)
    if vehicle_id:
        if Vehicle.query.get(vehicle_id) is None:
            return jsonify({'status': 'error', 'message': 'No vehicle found with this id'}), 404
        query = query.filter(Assignment.vehicle_id == vehicle_id)
    if start_time and end_time:
        if datetime.fromisoformat(start_time) > datetime.fromisoformat(end_time):
            return jsonify({'status': 'error', 'message': 'Start time must be before end time'}), 400
        start = datetime.fromisoformat(start_time)
        end = datetime.fromisoformat(end_time)
        query = query.filter(Assignment.start_time < end, Assignment.end_time > start)

    assignments = query.all()

    return jsonify([{
        'id': a.id,
        'start_time': a.start_time.isoformat(),
        'end_time': a.end_time.isoformat(),
        'driver': {
            'id': a.driver.id,
            'name': a.driver.name,
            'phone': a.driver.phone,
            'email': a.driver.email,
            'location': a.driver.location,
            'work_start_time': a.driver.work_start_time.isoformat(),
            'work_end_time': a.driver.work_end_time.isoformat()
        },
        'vehicle': {
            'id': a.vehicle.id,
            'make': a.vehicle.make,
            'model': a.vehicle.model,
            'plate_number': a.vehicle.plate_number
        } 
    } for a in assignments]), 200

@bp.route('/assignments/<int:assignment_id>', methods=['DELETE'])
def delete_assignment(assignment_id):
    assignment = Assignment.query.get(assignment_id)

    if assignment is None:
        return jsonify({'status': 'error', 'message': 'No assignment found with this id'}), 404


    db.session.delete(assignment)
    db.session.commit()
    return jsonify({'status': 'success', 'message': 'Assignment deleted successfully'}), 200



@bp.route('/drivers/<int:driver_id>/schedule', methods=['GET'])
def get_driver_schedule(driver_id):
    start_time = request.args.get('start_time')
    end_time = request.args.get('end_time')

    query = Assignment.query.filter(Assignment.driver_id == driver_id)

    if Assignment.query.filter(Assignment.driver_id == driver_id).first() is None:
        return jsonify({'status': 'error', 'message': 'No Schedule found for this id'}), 404

    if not query:
        return jsonify({'status': 'error', 'message': 'No assignments found for this driver'}), 404

    if start_time and end_time:
        start = datetime.fromisoformat(start_time)
        end = datetime.fromisoformat(end_time)
        query = query.filter(Assignment.start_time < end, Assignment.end_time > start)

    schedule = query.order_by(Assignment.start_time).all()
    return jsonify([{
        'id': a.id,
        'vehicle_id': a.vehicle_id,
        'start_time': a.start_time.isoformat(),
        'end_time': a.end_time.isoformat()
    } for a in schedule]), 200

@bp.route('/drivers/<int:driver_id>/pastSchedule', methods=['GET'])
def get_driver_past_schedule(driver_id):
    query = Assignment.query.filter(Assignment.driver_id == driver_id)

    if Assignment.query.filter(Assignment.driver_id == driver_id).first() is None:
        return jsonify({'status': 'error', 'message': 'No Schedule found for this id'}), 404

    if not query:
        return jsonify({'status': 'error', 'message': 'No assignments found for this driver'}), 404

    schedule = query.filter(Assignment.end_time < datetime.now()).order_by(Assignment.start_time).all()

    return jsonify([{
        'id': a.id,
        'vehicle_id': a.vehicle_id,
        'start_time': a.start_time.isoformat(),
        'end_time': a.end_time.isoformat()
    } for a in schedule]), 200

