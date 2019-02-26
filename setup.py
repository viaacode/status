import os
import sys
from setuptools import setup, find_packages

if sys.version_info < (3, 5):
    sys.exit('Sorry, Python < 3.5 is not supported')

__version__ = '0.0.1'
__author__ = 'VIAA'
__name__ = 'viaastatus'

with open('README.md') as f:
    long_description = f.read()


setup(
    name=__name__,
    url='https://github.com/viaacode/status/',
    version=__version__,
    author=__author__,
    author_email='support@viaa.be',
    descriptiona='Status services',
    long_description=long_description,
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
    ],
    python_requires='>=3.5',
    packages=find_packages("src"),
    package_dir={"": "src"},
    package_data={'conferatur': ['api/templates/*.html']},
    include_package_data=True,
    install_requires=[
       'Flask>=1.0.2',
       'jsonrpcserver>=4.0.1',
       'uWSGI>=2.0.18',
    ],
    extras_require={
        'test': [
            "pytest>=4.2.0"
        ]
    },
    platforms='any',
    entry_points={
        'console_scripts': [
#            "%s=%s.cli:main" % (__name__, __name__)
        ],
    }
)
