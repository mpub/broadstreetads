from setuptools import setup

setup(name="broadstreetads",
      version="0.1",
      description="Utilities to ease access to the Broadstreet Ads API from python.",
      py_modules=['broadstreetads'],
      license='BSD',
      author="Vanguardistas LLC",
      author_email='brian@vanguardistas.net',
      install_requires=['requests'],
      classifiers=[
          "Intended Audience :: Developers",
          "Operating System :: OS Independent",
          "License :: OSI Approved :: BSD License",
          "Programming Language :: Python :: 2",
          "Programming Language :: Python :: 2.6",
          "Programming Language :: Python :: 2.7",
          ],
      test_suite='tests',
      )
