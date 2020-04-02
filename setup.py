from setuptools import setup

setup(
    name='SDG',
    version='0.1',
    description='SDG app',
    url='http://www.arielakeman.com',
    author='Arie Lakeman',
    author_email='arie.lakeman@gmail.com',
    packages=['sdg'],
    entry_points = {
        'console_scripts': [
            'sdg = sdg.server.server:main',
        ]
    }
)
