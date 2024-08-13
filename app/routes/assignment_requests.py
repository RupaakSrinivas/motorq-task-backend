from flask import Blueprint, request, jsonify
from app import db
from app.models.assignment_request import AssignmentRequest
from app.models.driver import Driver
from app.models.vehicle import Vehicle
from app.models.vehicle_driver import Assignment
from app.models.mappingTable import MappingTable
from datetime import datetime

bp = Blueprint('assignment_requests', __name__)

@bp.route('/assignment-requests', methods=['POST'])
def create_assignment_request():
    data = request.json
    print(data)
    vehicle_id = data['vehicle_id']
    start_time = data['start_time']
    end_time = data['end_time']
    driver_ids = data['driver_ids']

    assignment_conflicts = Assignment.query.filter(
        Assignment.vehicle_id == vehicle_id,
        Assignment.start_time < end_time,
        Assignment.end_time > start_time
    ).first()

    if assignment_conflicts:
        return jsonify({'message': 'Vehicle is already assigned during this time period'}), 400
    
    if Vehicle.query.get(vehicle_id) is None:
        return jsonify({'status': 'error', 'message': 'No vehicle found with this id'}), 404
    
    if Driver.query.filter(Driver.id.in_(driver_ids)).count() != len(driver_ids):
        return jsonify({'status': 'error', 'message': 'One or more drivers not found'}), 404

    new_request = AssignmentRequest(vehicle_id=vehicle_id, start_time=start_time, end_time=end_time)
    db.session.add(new_request)
    db.session.commit()

    request_id = new_request.id

    for driver_id in driver_ids:
        new_mapping = MappingTable(driver_id=driver_id, request_id=request_id)
        db.session.add(new_mapping)

    db.session.commit()

    return jsonify({'message': 'Assignment request created successfully', 'id': new_request.id}), 201


@bp.route('/assignment-requests', methods=['GET'])
def get_assignment_requests():

    driver_id = request.args.get('driver_id', type=int)

    if not driver_id:
        return jsonify({'status': 'error', 'message': 'Driver ID is required'}), 400

    if Driver.query.get(driver_id) is None:
        return jsonify({'status': 'error', 'message': 'No driver found with this id'}), 404

    requests = AssignmentRequest.query

    if driver_id:
        requests = requests.join(MappingTable, AssignmentRequest.id == MappingTable.request_id).filter(MappingTable.driver_id == driver_id)

    requests = requests.all()

    return jsonify([{
        'id': r.id,
        'vehicle_id': r.vehicle_id,
        'start_time': r.start_time.isoformat(),
        'end_time': r.end_time.isoformat(),
        'status': r.status
    } for r in requests])

@bp.route('/assignment-requests/accept', methods=['POST'])
def accept_assignment_request():
    driver_id = request.json['driver_id']
    request_id = request.json['request_id']
    assignment_request = AssignmentRequest.query.get(request_id)
    driver = Driver.query.get(driver_id)

    if not driver:
        return jsonify({'status': 'error', 'message': 'No driver found with this id'}), 404
    
    if not assignment_request:
        return jsonify({'status': 'error', 'message': 'No assignment request found with this id'}), 404
    
    mapping = MappingTable.query.filter(MappingTable.request_id == request_id, MappingTable.driver_id == driver_id).first()

    if not mapping:
        return jsonify({'status': 'error', 'message': 'Unauthourized use'}), 400

    assignment_conflicts = Assignment.query.filter(
        Assignment.driver_id == driver_id,
        Assignment.start_time < assignment_request.end_time,
        Assignment.end_time > assignment_request.start_time
    ).first()

    vehicle_assignment_conflicts = Assignment.query.filter(
        Assignment.vehicle_id == assignment_request.vehicle_id,
        Assignment.start_time < assignment_request.end_time,
        Assignment.end_time > assignment_request.start_time
    ).first()

    if assignment_conflicts:
        return jsonify({'status': 'error', 'message': 'Driver is already assigned during this time period'}), 400
    
    if vehicle_assignment_conflicts:
        return jsonify({'status': 'error', 'message': 'Vehicle is already assigned during this time period'}), 400
    
    # if driver.work_start_time > assignment_request.start_time.time() or driver.work_end_time < assignment_request.end_time.time():
    #     return jsonify({'status':'error', 'message': 'Assignment hours outside of driver working hours'}), 400

    new_assignment = Assignment(
        driver_id=driver_id,
        vehicle_id=assignment_request.vehicle_id,
        start_time=assignment_request.start_time,
        end_time=assignment_request.end_time
    )
    db.session.add(new_assignment)

    mapping = MappingTable.query.filter(MappingTable.request_id == request_id).all()

    for m in mapping:
        db.session.delete(m)

    assignment_request.query.filter(AssignmentRequest.id == request_id).delete()

    db.session.commit()

    return jsonify({'status': 'success', 'message': 'Assignment request accepted successfully'}), 200


@bp.route('/assignment-requests/reject', methods=['POST'])
def reject_assignment_request():

    request_id = request.json['request_id']
    driver_id = request.json['driver_id']

    if Driver.query.get(driver_id) is None:
        return jsonify({'status': 'error', 'message': 'No driver found with this id'}), 404
    
    assignment_request = AssignmentRequest.query.get(request_id)
    if not assignment_request:
        return jsonify({'status': 'error', 'message': 'No assignment request found with this id'}), 404
    
    mapping = MappingTable.query.filter(MappingTable.request_id == request_id, MappingTable.driver_id == driver_id).first()
    if not mapping:
        return jsonify({'status': 'error', 'message': 'Unauthourized use'}), 400

    mapping = MappingTable.query.filter(MappingTable.request_id == request_id).all()

    for m in mapping:
        db.session.delete(m)

    db.session.commit()

    return jsonify({'status' : 'success', 'message': 'Assignment request rejected successfully'}), 200