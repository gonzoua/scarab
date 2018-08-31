"""Packaging settings."""


from codecs import open
from os.path import abspath, dirname, join
from subprocess import call

from setuptools import Command, find_packages, setup

from scarab import __version__


this_dir = abspath(dirname(__file__))
with open(join(this_dir, 'README.md'), encoding='utf-8') as file:
    long_description = file.read()


class RunTests(Command):
    """Run all tests."""
    description = 'run tests'
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        """Run all tests!"""
        errno = call(['py.test', '--cov=scarab', '--cov-report=term-missing'])
        raise SystemExit(errno)


setup(
    name = 'scarab',
    version = __version__,
    description = 'A FreBSD Bugzilla CLI client.',
    long_description = long_description,
    url = 'https://github.com/gonzoua/scarab',
    author = 'Oleksandr Tymoshenko',
    author_email = 'gonzo@bluezbox.com',
    license = 'BSD 3-clause "New" or "Revised License"',
    classifiers = [
	'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Utilities',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
    ],
    keywords = 'bugzilla cli freebsd',
    packages = find_packages(exclude=['docs', 'tests*']),
    install_requires = [
        'python-magic',
    ],
    extras_require = {
        'test': ['coverage', 'pytest', 'pytest-cov'],
    },
    entry_points = {
        'console_scripts': [
            'scarab=scarab.cli:main',
        ],
    },
    cmdclass = {'test': RunTests},
)
