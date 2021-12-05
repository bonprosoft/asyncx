import pathlib

from setuptools import find_packages, setup

BASE_DIR = pathlib.Path(__file__).resolve().parent
exec((BASE_DIR / "asyncx/_version.py").read_text())

setup(
    name="asyncx",
    version=__version__,  # type: ignore[name-defined]  # NOQA: F821
    packages=find_packages(),
    description="Utility library for asyncio",
    long_description=(BASE_DIR / "README.md").read_text(),
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
    extras_require={
        "docs": [
            "Sphinx>=4.3.0,<5.0.0",
            "sphinx-rtd-theme==1.0.0",
        ],
    },
)
