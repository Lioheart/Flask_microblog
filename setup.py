"""Plik z niezbędnymi pakietami"""
from setuptools import setup

setup(
    name='Flask Tutorial',
    version='0.0.1',
    packages=['app'],
    author='Lioheart',
    python_requires='>=3.7',
    install_requires=['flask', 'python-dotenv', 'flask-wtf'],
)
