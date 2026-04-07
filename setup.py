from setuptools import setup, find_packages

setup(
    name="navbot-x-isaac-lab",
    version="0.1.0",
    package_dir={"": "source"},
    packages=find_packages(where="source"),
    include_package_data=True,
)