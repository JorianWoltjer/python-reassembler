from setuptools import setup

with open('requirements.txt') as f:
    requirements = f.read().splitlines()

setup(
    name='reassembler',
    version='0.1',
    py_modules=['reassembler'],
    install_requires=requirements,
    extras_require={
        'test': ['pytest', 'decompyle3'],
    },
    entry_points={
        'console_scripts': [
            'python-reassembler = reassembler:main',
        ],
    },
    author='Jorian Woltjer',
    description='Re-assemble Python disassembly text to bytecode',
    license='MIT',
    keywords='cli bytecode reassemble decompile',
    url='https://github.com/JorianWoltjer/python-reassembler',
)
