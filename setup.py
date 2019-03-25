from setuptools import setup, find_packages

with open('README.md') as f:
    long_description = f.read()

with open('requirements.txt') as f:
    requirements = list(map(str.rstrip, f.readlines()))

setup(
    name='viaastatus',
    url='https://github.com/viaacode/status/',
    version='0.0.3',
    author='VIAA',
    author_email='support@viaa.be',
    descriptiona='Status services',
    long_description=long_description,
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
    ],
    python_requires='>=3.4',
    packages=find_packages("src"),
    package_dir={"": "src"},
    package_data={'viaastatus': ['server/static/*']},
    include_package_data=True,
    install_requires=requirements,
    extras_require={
        'test': [
            "pytest>=4.2.0"
        ],
        'loadtest': [
            "locustio>=0.11.0"
        ],
        'gunicorn': [
            'gunicorn>=19.9.0'
        ],
        'uwsgi': [
            'uWSGI>=2.0.18'
        ],
        'waitress': [
            'waitress>=1.2.1'
        ]
    },
    platforms='any'
)
