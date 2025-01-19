from setuptools import setup, find_packages
from codecs import open
from os import path

HERE = path.abspath(path.dirname(__file__))

with open(path.join(HERE, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='bibtex-generator',
    version='0.1.0',
    packages=find_packages(),
    install_requires=[
        'requests',
        'typing',
        'urllib3',
    ],
    author='Sadeep Ariyarathna',
    author_email='sadeepari@gmail.com',
    description='A tool to generate BibTeX entries',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/elemenceOR/bibtex-generator',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)