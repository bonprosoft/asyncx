from setuptools import find_packages, setup

setup(
    name="asyncx",
    version="0.0.1",
    packages=find_packages(),
    author="Yuki Igarashi",
    author_email="me@bonprosoft.com",
    url="https://github.com/bonprosoft/asyncx",
    license="MIT License",
    package_data={"asyncx": ["py.typed"]},
)
