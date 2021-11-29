from setuptools import setup

setup(
    name='get_time_package',
    version='0.1',
    description='description',
    url='http://github.com/name/package_name',
    author='Your Name',
    author_email='email@example.com',
    license='MIT',
    packages=['pack.get_time_package'],
    namespace_packages=['pack'],
    install_requires=[
        'requests==2.26.0'
    ],
    entry_points={
        'console_scripts': [
            'get_time=pack.get_time_package.get_time_module:main',
        ]
    }
)