from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join('springboard', 'version.txt'), 'r') as vf:
    VERSION = vf.read()

setup(
    name='springboardcli',

    version=VERSION,

    description='The Springboard CLI',
    long_description='The Longer Springboard CLI',

    url='https://gitlab.amer.gettywan.com/springboard/springboard_cli',

    author='Springboard Team',
    author_email='springboard@gettyimages.com',

    license='MIT',

    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Springboard :: Development',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3'
    ],

    keywords='springboard springboardcli',
    packages=find_packages(),

    install_requires=[
        'jinja2',
        'requests',
        'pyyaml'
    ],

    include_package_data=True,
    package_data={
        '': [
            'springboard/faces/puppet/skel/', 'version.txt'
        ],
    },

    entry_points={
        'console_scripts': ['spbd=springboard.entry:main', 'springboard=springboard.entry:main', ]
    }
)
