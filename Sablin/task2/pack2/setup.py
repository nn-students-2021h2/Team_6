from setuptools import setup

setup(
    name='pretty_print_package',
    version='0.1',
    description='description',
    url='http://github.com/name/package_name',
    author='Your Name',
    author_email='email@example.com',
    license='MIT',
    packages=['pack.pretty_print_package'],
    namespace_packages=['pack'],
    install_requires=[
        'requests==2.26.0',
        # 'get_time_package'
    ],
    entry_points={
        'console_scripts': [
        ]
    }
)