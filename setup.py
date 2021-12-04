from setuptools import find_packages, setup

setup(
    name="asyncx",
    version="0.0.1",
    packages=find_packages(),
    description="Utility library for asyncio",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Yuki Igarashi",
    author_email="me@bonprosoft.com",
    url="https://github.com/bonprosoft/asyncx",
    license="MIT License",
    classifiers=[
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX",
        "Operating System :: MacOS",
        "Operating System :: Unix",
    ],
    package_data={"asyncx": ["py.typed"]},
)
