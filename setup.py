import io
import os

from setuptools import find_packages, setup

here = os.path.abspath(os.path.dirname(__file__))

# Import the README and use it as the long-description.
with io.open(os.path.join(here, "README.md"), encoding="utf-8") as f:
    long_description = "\n" + f.read()

with open("requirements.txt") as f:
    required = f.read().splitlines()

setup(
    name="kgsearch",
    version="0.0.1",
    author="Raphael Sourty",
    author_email="raphael.sourty@gmail.com",
    description="Minimalist visual search engine for Knowledge Graph.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="BSD-3",
    url="https://github.com/raphaelsty/kgsearch",
    package_data={
        "kgsearch": [
            "web/app.html",
            "data/data.csv",
        ]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    packages=find_packages(),
    include_package_data=True,
    install_requires=required,
    python_requires=">=3.7",
    entry_points={
        "console_scripts": ["kg=kgsearch:start"],
    },
)
