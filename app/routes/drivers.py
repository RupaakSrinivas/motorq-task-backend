from flask import Blueprint, request, jsonify
from app import db
from app.models.driver import Driver
from app.models.vehicle_driver import Assignment
from sqlalchemy import func
from datetime import datetime

import haversine as hs   
from haversine import Unit

bp = Blueprint('drivers', __name__)

@bp.route('/drivers', methods=['POST'])
def create_driver():
    data = request.json

    if 'name' not in data or 'phone' not in data or 'email' not in data or 'location' not in data or 'work_start_time' not in data or 'work_end_time' not in data:
        return jsonify({'status': 'error', 'message': 'Missing required fields'}), 400
    
    if Driver.query.filter(func.lower(Driver.email) == func.lower(data['email'])).first():
        return jsonify({'status':'error', 'message': 'Driver with this email already exists'}), 400

    # data['work_start_time'] = data['work_start_time'].toUTCString()
    # data['work_end_time'] = data['work_end_time'].toUTCString()

    start_time = datetime.strptime(data['work_start_time'], '%H:%M').time()
    end_time = datetime.strptime(data['work_end_time'], '%H:%M').time()

    if start_time >= end_time:
        return jsonify({'status': 'error', 'message': 'Start time must be before end time'}), 400

    new_driver = Driver(name=data['name'], phone=data['phone'], email=data['email'], location=data['location'], work_start_time=start_time, work_end_time=end_time, city=data['city'])

    db.session.add(new_driver)
    db.session.commit()
    return jsonify({'status':'success', 'message': 'Driver created successfully'}), 201

@bp.route('/drivers', methods=['GET'])
def search_drivers():
    name = request.args.get('name')
    phone = request.args.get('phone')
    email = request.args.get('email')
    #13.0435051,79.2404096



    print(name, phone, email)

    query = Driver.query

    if name:
        query = query.filter(Driver.name.ilike(f'%{name}%'))
    if phone:
        query = query.filter(Driver.phone.ilike(f'%{phone}%'))
    if email:
        query = query.filter(Driver.email.ilike(f'%{email}%'))

    drivers = query.all()

    if email and not drivers:
        return jsonify({'status': 'success', 'message': 'No driver found with this email'}), 200
    
    if name and not drivers:
        return jsonify({'status': 'success', 'message': 'No driver found with this name'}), 200
    
    if phone and not drivers:
        return jsonify({'status': 'success', 'message': 'No driver found with this phone number'}), 200
    

    location = request.args.get('location')
    
    if location:
        location = location.split(',')
        lat1 = float(location[0])
        lon1 = float(location[1])
        drivers = Driver.query.all()
        driver_list = []
    
        for driver in drivers:
            driver_location = driver.location.split(',')
            lat2 = float(driver_location[0])
            lon2 = float(driver_location[1])
            distance = hs.haversine((lat1, lon1), (lat2, lon2), unit=Unit.METERS)
            if distance < 10000:
                driver_list.append(driver)
        return jsonify([{
            'id': driver.id,
            'name': driver.name,
            'phone': driver.phone,
            'email': driver.email
        } for driver in driver_list]), 200
    
    return jsonify([{
        'id': driver.id,
        'name': driver.name,
        'phone': driver.phone,
        'email': driver.email,
        'location': driver.location,
        'work_start_time': driver.work_start_time.isoformat(),
        'work_end_time': driver.work_end_time.isoformat()
    } for driver in drivers]), 200