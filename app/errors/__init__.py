"""Szablon wzorca błędów"""
from flask import Blueprint

print('Uruchomienie wzorca błędów')
bp = Blueprint('errors', __name__)

from app.errors import handlers
