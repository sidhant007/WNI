from setuptools import setup

setup(
    name='wni',
    author='Sidhant Bansal',
    author_email='sidhbansal@gmail.com',
    description='WeNotI - Making basic distributed computing tasks simpler and cheaper',
    url='https://google.com',
    version='0.1',
    py_modules=['wni'],
    install_requires=[
        'Click',
        'Python-socketio==4.4.0',
        'PrettyTable',
    ],
    entry_points='''
        [console_scripts]
        wni=wni:cli
    '''
)
