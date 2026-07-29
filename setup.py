
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    author='Hasan Ali Özkan',
    description='Simple File Sharing and Gathering Library',
    name='sfsgl',
    version='0.1.11',
    url='https://github.com/hasanaliozkan-dev/SFSGL/',
    project_urls={
        "Source Code": "https://github.com/hasanaliozkan-dev/SFSGL/",
        "Bug Tracker": "https://github.com/hasanaliozkan-dev/SFSGL/issues",
        "Documentation": "https://hasanaliozkan-dev.github.io/SFSGL/"
    },
    packages=find_packages(),
    install_requires=['flask'],
    include_package_data=True,
    python_requires='>=3.6',
    long_description=long_description,
    long_description_content_type="text/markdown",
    license='MIT License',
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Education",
        "Topic :: Education",

    ],
    keywords='file sharing gathering library',
    author_email="hasanaliozkan-dev@outlook.com",
    entry_points={
        'console_scripts': [
            'sfsgl = SFSGL.sfsgl:main',
        ],
    },
    
)