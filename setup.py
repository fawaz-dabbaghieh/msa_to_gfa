#!/usr/bin/env python3
import sys
from distutils.core import setup
from setuptools import setup, find_packages

CURRENT_PYTHON = sys.version_info[:2]
REQUIRED_PYTHON = (3, 3)

# This check and everything above must remain compatible with Python 2.7.
if CURRENT_PYTHON < REQUIRED_PYTHON:
    sys.stderr.write("msa_to_gfa requires Python 3.3 or higher and "
                     "you current verions is {}".format(CURRENT_PYTHON))
    sys.exit(1)

setup(name='msa_to_gfa',
      version='1.0.1',
      description='convertes an MSA in FASTA to a GFA1 file with imbedded paths',
      author='Fawaz Dabbaghie',
      author_email='fawaz@hhu.de',
      url='https://github.com/fawaz-dabbaghieh/msa_to_gfa',
      packages=find_packages(),
      # scripts=['bin/main.py'],
      license="LICENSE.TXT",
      long_description=open("README.md").read(),
      long_description_content_type='text/markdown',
#       install_requires=["protobuf == 3.11.3",
#                         "pystream-protobuf == 1.5.1"],
      # other arguments here...
      entry_points={
          "console_scripts": [
              "msa_to_gfa=msa_to_gfa.main:main"
          ]}
      )
