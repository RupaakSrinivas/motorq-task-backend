import os

from dotenv import load_dotenv

load_dotenv('.env.local')

class Config:
    SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:123admin@localhost/vehicle_driver_management'

    SQLALCHEMY_TRACK_MODIFICATIONS = False