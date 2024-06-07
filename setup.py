# setup.py
from setuptools import setup, find_packages

setup(
    name='media-file-tools',
    version='1.0.0',
    description='Organize your digital media files',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='Tom Sarantis',
    url='https://github.com/saranti/media-file-tools',
    packages=find_packages(),
    py_modules=['movie_sort_to_df', 'series_details', 'common'],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
    install_requires=[
        'pandas',
        'requests',
        'beautifulsoup4',
    ],
    test_suite='tests',
)
