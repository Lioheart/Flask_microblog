"""Plik z niezbędnymi pakietami"""
from setuptools import setup

setup(
    name='Flask Tutorial',
    version='0.0.1',
    packages=['app'],
    author='Lioheart',
    python_requires='>=3.7',
    install_requires=['flask', 'python-dotenv', 'email-validator', 'flask-wtf', 'flask-sqlalchemy', 'flask-migrate',
                      'flask-login', 'flask-mail', 'pyjwt', 'flask-bootstrap', 'flask-moment'],
)
