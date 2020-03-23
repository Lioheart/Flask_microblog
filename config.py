"""Plik konfiguracyjny"""
import os


class Config:
    """
    Klasa konfiguracyjna, zawierająca SECRET_KEY
    """
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'nigdy-nie-zgadniesz'
