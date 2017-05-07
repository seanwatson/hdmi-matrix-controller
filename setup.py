from setuptools import setup

setup(
    name='HDMI Matrix Controller',
    version='0.1',
    description='Control an HDMI matrix.',
    author='Sean Watson',
    license='MIT',
    py_modules=['hdmi_matrix_controller'],
    install_requires=[
        'pyserial',
    ],
    zip_safe=False
)
