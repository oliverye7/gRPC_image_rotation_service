from setuptools import setup

setup(
    name='gRPC Image Rotation Service',
    version='1.0.0',
    description='Neuralink Technical Challenge',
    author='Oliver Ye',
    author_email='oliverye@berkeley.edu',
    license='MIT',
    install_requires=[
        'grpcio',
        'grpcio-tools',
        'numpy',
        'opencv_python',
        'Pillow',
        'protobuf',
    ],
    python_requires="~=3.9"
)

