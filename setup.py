import pyrastitcher

VERSION = pyrastitcher.version
"""
roll with:

git tag VERSION
git push --tags
python setup.py sdist upload -r pypi
"""

from distutils.core import setup
setup(
    name = 'pyrastitcher',
    packages = [
        'pyrastitcher'
    ],
    version = VERSION,
    description = 'Provides a Python interface to the Terastitcher program.',
    author = 'Jordan Matelsky',
    author_email = 'jordan@neurodata.io',
    url = 'https://github.com/j6k4m8/pyrastitcher',
    download_url = 'https://github.com/j6k4m8/pyrastitcher/tarball/' + VERSION,
    keywords = [
        'brain',
        'microscopy',
        'neuro',
        'neuroscience',
        'EM',
        'stitching',
        'stitch',
        'terastitcher'
    ],
    classifiers = [],
    setup_requires = [],
    install_requires = []
)
