
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    author='Hasan Ali Özkan',
    description='Simple File Sharing and Gathering Library',
    name='SFSGL',
    version='0.1.9',
    url='https://github.com/hasanaliozkan-dev/SFSGL/',
    project_urls={
        "Source Code": "https://github.com/hasanaliozkan-dev/SFSGL/",
        "Bug Tracker": "https://github.com/hasanaliozkan-dev/SFSGL/issues",
        "Documentation": "https://github.com/hasanaliozkan-dev/SFSGL/blob/main/README.md"
    },
    packages=find_packages(),
    install_requires=['flask', 'werkzeug'],
    package_data={
        '': ['*.html', '*.py'],
        'SFSGL': ['static/*', 'templates/*'],
    },
    python_requires='>=3.6',
    long_description=long_description,
    long_description_content_type="text/markdown",
)