import setuptools


with open('./README.md', 'r', encoding='utf-8') as file:
    long_description = file.read()


setuptools.setup(
    name='wampify',
    version='0.1.0',
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
        'Typing :: Typed',
        'Topic :: Internet',
        'Topic :: Communications',
        'Framework :: AsyncIO',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    packages=setuptools.find_packages(where='.'),
    install_requires=[
        'autobahn',
        'pydantic'
    ],
    python_requires='>=3.6',
)