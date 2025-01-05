from setuptools import setup, find_packages


setup(
    author='Hasan Ali Özkan',
    description='Simple File Sharing and Gathering Library',
    name='SFSGL',
    version='0.1.0',
    packages=find_packages(),
    install_requires=['flask','werkzeug'],
    python_requires='>=3.6',


)