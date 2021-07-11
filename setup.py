import sys
from setuptools import setup


if sys.version_info < (3, 0):
    sys.stderr.write("Sorry, Python < 3.0 is not supported\n")
    sys.exit(1)


setup(name='picotui',
      version='1.2.1',
      description="""A simple text user interface (TUI) library.""",
      long_description=open('README.rst').read(),
      url='https://github.com/pfalcon/picotui',
      author='Paul Sokolovsky',
      author_email='pfalcon@users.sourceforge.net',
      license='MIT',
      packages=['picotui'])
