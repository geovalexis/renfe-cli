from setuptools import find_packages, setup

try:
    from pypandoc import convert_file
    read_md = lambda f: convert_file(f, 'rst')
except ImportError:
    print("warning: pypandoc module not found, could not convert Markdown to RST")
    read_md = lambda f: open(f, 'r').read()

setup(
    name='renfe-cli',
    version='3.3.0',
    description='Get faster RENFE Spanish Trains timetables in your terminal',
    long_description=read_md('README.md'),
    keywords='Get faster RENFE Spanish Trains timetables terminal',
    author='Gerard Castillo',
    author_email='gerardcl@gmail.com',
    url='https://github.com/gerardcl/renfe-cli',
    license='BSD',
    packages = find_packages('src'),
    package_dir = {'': 'src'},
    py_modules=['renfe-cli'],
    include_package_data=True,
    install_requires=[
        'setuptools>=60.9.3',
        'beautifulsoup4==4.10.0',
        'html5lib==1.1',
        'selenium==4.12.0',
        'webdriver-manager==4.0.0',
        'requests==2.31.0',
        'colorama>=0.4.6,<1.0',
    ],
    entry_points="""
        [console_scripts]
        renfe-cli = renfe.cli:main
        """,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: End Users/Desktop',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: MacOS',
        'Operating System :: Unix',
        'Operating System :: POSIX',
        'Operating System :: Microsoft :: Windows',
        'Programming Language :: Python',
        'Topic :: Utilities',
        'Topic :: Terminals',
        'Topic :: Text Processing :: Markup :: HTML',
    ],
    tests_require=['pytest'],
    test_suite = 'pytest',
)
