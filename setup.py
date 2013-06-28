import os
from setuptools import setup

README = open(os.path.join(os.path.dirname(__file__), 'README.md')).read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='pymemstore',
    version='0.2.2',
    packages=['pymemstore'],
    include_package_data=True,
    #license='BSD License',
    description='Python based in-memory datastore.',
    long_description=README,
    url='https://github.com/optimuspaul/pymemstore',
    author='Paul J. DeCoursey',
    author_email='paul@decoursey.net',
    install_requires=['msgpack-python==0.3.0']
)
