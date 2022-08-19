from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()
    
setup(name="sharepointio",
      version="0.0.4",
      description="An easy use of Office365-REST-Python-Client to download/upload/list sharepoint files",
      long_description=long_description,
      author="Thomas PICAL, Hervé MIGNOT",
      author_email="no-reply@noreply.com",
      packages=["sharepointio"],
      install_requires=["Office365-REST-Python-Client", "temp", "pathlib2"],
      license="Apache 2.0",
      classifiers=[
            "Development Status :: 2 - Pre-Alpha",
            "Topic :: Internet :: WWW/HTTP",
            "Topic :: Communications :: File Sharing",
            "Topic :: Office/Business",
            "Topic :: Utilities",
            "Intended Audience :: Developers",
            "Programming Language :: Python :: 3.8",
            "License :: OSI Approved :: Apache Software License",
            "Operating System :: OS Independent",
      ]
     )