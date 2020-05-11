try: # for pip >= 10
    from pip._internal.req import parse_requirements
except ImportError: # for pip <= 9.0.3
    from pip.req import parse_requirements

from setuptools import setup, find_packages
import pip
import os

setup(
    name="Passive Sonar Preprocessing",
    version="0.1",
    packages=find_packages(),
    description="passive sonar preprocessing for classification experiments",
    install_reqs=parse_requirements(os.path.join('container', 'requirements.txt'))
)
