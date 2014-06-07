"""Taggart PyPI Package."""

import os
from distutils.core import setup


def get_version():
    """Return latest version noted in changefile."""
    lastline = [line for line in read('CHANGES.txt').split('\n') if line][-1]
    version = lastline.split(',')[0]
    return version[1:]


def read(filename):
    """Read file contents."""
    f = open(os.path.join(os.path.dirname(__file__), filename))
    contents = f.read()
    f.close()
    return contents


setup_args = dict(
    name='taggart',
    version=get_version(),
    description='Taggart is a simple file tagger.',
    long_description=read('README.md'),
    author='Mark R. Gollnick &#10013;',
    author_email='mark.r.gollnick@gmail.com',
    url='https://github.com/markgollnick/taggart/',
    py_modules=['taggart']
)


if __name__ == '__main__':
    setup(**setup_args)
