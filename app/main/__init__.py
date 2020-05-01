"""Szablon wzorca głównego"""
from flask import Blueprint

print('Uruchomienie wzorca głównego')
bp = Blueprint('main', __name__)

from app.main import routes