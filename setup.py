from setuptools import setup, find_packages

setup(
    name='tse_to_xyce',
    version='0.4.0',
    packages=find_packages(exclude=('tests', 'xyce_thcc_lib')),
    install_requires=[],
    url='https://www.typhoon-hil.com/',
    include_package_data=True,
    license='MIT',
    author='Typhoon HIL',
    author_email=f'marcos.moccelini@typhoon-hil.com',
    description='Typhoon HIL Schematic Editor to Xyce converter'
)
