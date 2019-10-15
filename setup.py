#!/usr/bin/env python
import setuptools
with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
      name='pipeframe',
      version='0.0.2',
      description='PipeFrame - Simple module to write multiprocessing data pipelines with python.',
      long_description=long_description,
      long_description_content_type="text/markdown",
      author='Ricardo Pascal',
      author_email='voorloop@gmail.com',
      url='https://github.com/voorloopnul/pipeframe',
      packages=setuptools.find_packages(),
      python_requires='>=3.4',
      )
