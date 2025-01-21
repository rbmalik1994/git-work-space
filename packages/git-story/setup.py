from setuptools import setup, find_packages

setup(
    name='git_story',
    version='0.1',
    package_dir={'': 'src'},
    packages=find_packages(where='src'),
    install_requires=[
        'numpy',
        'gitpython',
        'manim',
    ],
    entry_points={
        'console_scripts': [
            'git_story=git_story.main:main',
        ],
    },
)