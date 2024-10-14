from setuptools import setup, find_packages

setup(
    name='tap-razorpay',
    version='0.1.0',
    description='Singer.io tap for extracting data from the Razorpay API',
    author='Cohesyve',
    url='https://github.com/Cohesyve/tap-razorpay',
    classifiers=['Programming Language :: Python :: 3 :: Only'],
    py_modules=['tap_razorpay'],
    install_requires=[
        'singer-python==5.12.2',
        'requests==2.25.1',
        'backoff==1.8.0'  # Changed from 1.10.0 to 1.8.0
    ],
    entry_points='''
        [console_scripts]
        tap-razorpay=tap_razorpay:main
    ''',
    packages=find_packages(),
    package_data={
        'tap_razorpay': ['schemas/*.json']
    },
    include_package_data=True,
)