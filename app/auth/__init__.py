"""Szablon wzorca autoryzacji"""
from flask import Blueprint

print('Uruchomienie wzorca autoryzacji')
bp = Blueprint('auth', __name__)

from app.auth import routes
