from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='hdaf_filter',  
    version = '0.1.0',
    description='Fourier filtering using the Hermite Distributed Approximation Functions as the low-pass filter',
    url='https://github.com/paul-hernandez-herrera/hdaf_filtering',
    author='Paúl Hernández-Herrera',
    author_email='paul.hernandez@ibt.unam.mx',
    license='BSD 3-clause',
    packages=['hdaf_filter'],
    install_requires=["matplotlib>=3.5.2", 
        "numpy>=1.23.1",
        "setuptools>=58.1.0",
        "tifffile>=2022.7.28"],

    classifiers=[
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: BSD License',  
        'Operating System :: OS Independent',        
        'Programming Language :: Python :: 3.8',
    ],
)