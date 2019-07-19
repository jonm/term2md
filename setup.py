from setuptools import setup, find_packages

__version__ = '0.1.2'

def read(filename):
    with open(filename) as f:
        return f.read()

setup(
    name = 'term2md',
    version = __version__,
    description = 'convert terminal control characters to Markdown',
    long_description = read('README.md'),
    author = 'Jon Moore',
    url = 'https://github.com/jonm/term2md',
    packages = find_packages(),
    include_package_data = True,
    license='MIT',
    setup_requires=["pytest-runner"],
    tests_require=["pytest"]
)
