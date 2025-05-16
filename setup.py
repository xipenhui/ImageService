from setuptools import setup, find_packages

setup(
    name="imageservice",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "requests",
        "pydantic-settings",
        "Pillow",
    ],
) 