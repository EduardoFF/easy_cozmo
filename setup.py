from setuptools import setup
import os

thelibFolder = os.path.dirname(os.path.realpath(__file__))
requirementPath = thelibFolder + '/requirements.txt'
install_requires = []
if os.path.isfile(requirementPath):
    with open(requirementPath) as f:
        install_requires = f.read().splitlines()
with open(os.path.join(thelibFolder, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='easy_cozmo',
    version='1.0.1',
    author='Eduardo Feo-Flushing',
    author_email='efeoflus@andrew.cmu.edu',
    packages=['easy_cozmo'],
    url='http://github.com/EduardoFF/easy_cozmo',
    license='LICENSE.txt',
    description='Useful python wrappers for Cozmo SDK.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    install_requires=install_requires,
)
