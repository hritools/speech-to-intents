import setuptools


VERSION = '0.0.2'


with open('README.md', 'r') as f:
    long_description = f.read()


with open('requirements.txt') as f:
    required = f.read().splitlines()


setuptools.setup(
    name='speechtointents',
    version=VERSION,
    author='Vlad Kurenkov',
    author_email='v.kurenkov@nnopolis.ru',
    description='Speech to intents',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://cordelianew.university.innopolis.ru/gitea/hri/speech-to-intents',
    packages=setuptools.find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
    ],
    install_requires=required,
)
