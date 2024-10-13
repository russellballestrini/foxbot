from setuptools import setup, find_packages

requires = [
    'twisted',   # foxbot.py
    'requests',  # plugins/quotes.py
    #'pywapi',    # plugins/weather.py
    'beautifulsoup4',  # plugins/urinfo.py
    'hurry.filesize',  # plugins/urinfo.py
]

setup( 
    name         = 'foxbot',
    version      = '0.0.1',
    description  = 'foxbot | the dynamic plugin IRC bot',
    keywords     = 'foxbot IRC bot dynamic plugin',
    
    author       = 'Russell Ballestrini',
    author_email = 'russell@ballestrini.net',
    url          = 'https://bitbucket.org/russellballestrini/foxbot',

    platforms    = ['All'],
    license      = 'MIT',

    py_modules   = ['foxbot'],
    
    include_package_data = True,
    install_requires     = requires,
    long_description = open('README.rst').read(),

    entry_points = {
      'console_scripts': [
        'foxbot = foxbot:main',
      ],
    },

)

# setup keyword args: http://peak.telecommunity.com/DevCenter/setuptools

# built and uploaded to pypi with this:
# python setup.py sdist bdist_egg register upload
