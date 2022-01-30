import setuptools


with open('./README.md', 'r', encoding='utf-8') as file:
    long_description = file.read()


setuptools.setup(
    name='wampify',
    version='0.0.1.3',
    author='Aidar Turkenov',
    author_email='a.k.turken0v@gmail.com',
    description='Web Application Messaging Protocol Framework',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/aturkenov/wampify',
    project_urls={
        'Bug Tracker': 'https://github.com/aturkenov/wampify/issues',
        'Discussions': 'https://github.com/aturkenov/wampify/discussions',
    },
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    packages=setuptools.find_packages(where='.'),
    install_requires=[
        'autobahn',
        'orjson',
        'pydantic'
    ],
    python_requires='>=3.6',
)