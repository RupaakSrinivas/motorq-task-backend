from flask import Blueprint, request, jsonify
from app import db
from app.models.assignment_request import AssignmentRequest
from app.models.driver import Driver
from app.models.vehicle import Vehicle
from app.models.vehicle_driver import Assignment
from datetime import datetime

bp = Blueprint('assignment_requests', __name__)

@bp.route('/assignment-requests', methods=['POST'])
def create_assignment_request():
    data = request.json
    vehicle_id = data['vehicle_id']
    start_time = data['start_time']
    end_time = data['end_time']

    # Check for conflicts in existing assignments
    assignment_conflicts = Assignment.query.filter(
        Assignment.vehicle_id == vehicle_id,
        Assignment.start_time < end_time,
        Assignment.end_time > start_time
    ).first()

    if assignment_conflicts:
        return jsonify({'message': 'Vehicle is already assigned during this time period'}), 400

    # Check for conflicts in pending assignment requests
    request_conflicts = AssignmentRequest.query.filter(
        AssignmentRequest.vehicle_id == vehicle_id,
        AssignmentRequest.status == 'pending',
        AssignmentRequest.start_time < end_time,
        AssignmentRequest.end_time > start_time
    ).first()

    if request_conflicts:
        return jsonify({'message': 'There is already a pending request for this vehicle during this time period'}), 400

    new_request = AssignmentRequest(vehicle_id=vehicle_id, start_time=start_time, end_time=end_time)
    db.session.add(new_request)
    db.session.commit()

    return jsonify({'message': 'Assignment request created successfully', 'id': new_request.id}), 201


@bp.route('/assignment-requests', methods=['GET'])
def get_assignment_requests():
    status = request.args.get('status', 'pending')

    if status not in ['pending', 'accepted', 'expired']:
        return jsonify({'message': 'Invalid status parameter'}), 400

    start_time = request.args.get('start_time')
    end_time = request.args.get('end_time')

    requests = AssignmentRequest.query.filter_by(status=status).all()

    if start_time:
        start_time = datetime.fromisoformat(start_time)
        requests = [r for r in requests if r.start_time >= start_time]

    if end_time:
        end_time = datetime.fromisoformat(end_time)
        requests = [r for r in requests if r.end_time <= end_time]

    if not requests:
        return jsonify({'message': 'No assignment requests found'}), 404

    return jsonify([{
        'id': r.id,
        'vehicle_id': r.vehicle_id,
        'start_time': r.start_time.isoformat(),
        'end_time': r.end_time.isoformat(),
        'status': r.status
    } for r in requests])

@bp.route('/assignment-requests/<int:request_id>/accept', methods=['POST'])
def accept_assignment_request(request_id):
    driver_id = request.json['driver_id']
    assignment_request = AssignmentRequest.query.get_or_404(request_id)
    driver = Driver.query.get(driver_id)

    if not driver:
        return jsonify({'status': 'error', 'message': 'No driver found with this id'}), 404

    if driver.work_start_time > assignment_request.start_time.time() or driver.work_end_time < assignment_request.end_time.time():
        return jsonify({'status': 'error', 'message': 'Assignment hours outside of working hours'}), 400

    if assignment_request.status != 'pending':
        return jsonify({'status': 'error', 'message': 'This request is no longer valid'}), 400

    # Check if the vehicle is still available for this time slot
    conflicts = Assignment.query.filter(
        Assignment.vehicle_id == assignment_request.vehicle_id,
        Assignment.start_time < assignment_request.end_time,
        Assignment.end_time > assignment_request.start_time
    ).first()

    if conflicts:
        assignment_request.status = 'expired'
        db.session.commit()
        return jsonify({'error': 'error', 'message': 'This vehicle is no longer available for the requested time slot'}), 400

    # Create new assignment
    new_assignment = Assignment(
        driver_id=driver_id,
        vehicle_id=assignment_request.vehicle_id,
        start_time=assignment_request.start_time,
        end_time=assignment_request.end_time
    )
    db.session.add(new_assignment)

    # Update request status
    assignment_request.status = 'accepted'
    db.session.commit()

    return jsonify({'status': 'success', 'message': 'Assignment request accepted successfully'}), 200

@bp.route('/assignment-requests/<int:request_id>/reject', methods=['POST'])
def reject_assignment_request(request_id):
    assignment_request = AssignmentRequest.query.get_or_404(request_id)

    if assignment_request.status != 'pending':
        return jsonify({'status': 'error', 'message': 'This request is no longer valid'}), 400

    assignment_request.status = 'rejected'
    db.session.commit()

    return jsonify({'status' : 'success', 'message': 'Assignment request rejected successfully'}), 200