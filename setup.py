# setup.py
from setuptools import setup, find_packages

setup(
    name='media-file-tools',
    version='1.1.0',
    description='Organize your digital media files',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='Tom Sarantis',
    url='https://github.com/saranti/media-file-tools',
    packages=find_packages(),
    py_modules=['movie_sort_to_df',
                'series_details',
                'common',
                'find_music_dupes'],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
    install_requires=[
        'pandas>=2.2.2',
        'requests>=2.32.3',
        'beautifulsoup4>=4.12.3',
        'tabulate>=0.9.0',
        'tinytag>=1.10.1',
    ],
    test_suite='tests',
)
