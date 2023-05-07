from setuptools import setup, find_packages
from pathlib import Path
import re

PACKAGENAME = 'vfxnaming'
PACKAGE_NICENAME = 'VFX Naming Conventions Framework'

module_dir = Path(__file__).parents[0]
version_module = module_dir.joinpath('src', PACKAGENAME, '_version.py')

version_str = "0.0.0"
with open(version_module) as fp:
    version_str = re.match(
        r'.*__version__ = [\',\"](.*?)[\',\"]',
        fp.read(),
        re.DOTALL
    ).group(1)

# Get the long description from the README file
with open(module_dir.joinpath('README.rst'), encoding='utf-8') as fp:
    long_description = fp.read()


setup(
    name=PACKAGENAME,
    version=version_str,
    description=PACKAGE_NICENAME,
    long_description=long_description,
    long_description_content_type='text/x-rst',
    url='https://github.com/xiancg/vfxnaming',
    download_url=f'https://github.com/xiancg/vfxnaming/archive/v{version_str}.tar.gz',
    author='Chris Granados- Xian',
    author_email='info@chrisgranados.com',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3.7'
    ],
    package_dir={'': 'src'},
    packages=find_packages(where='src'),
    python_requires='>=3.7, <4',
    extras_require={
        'dev': ['pytest', 'pytest-cov', 'pytest-datafiles', 'python-coveralls', 'flake8'],
        'docs': ['sphinx', 'sphinx-rtd-theme']
    },
    include_package_data=True
)
