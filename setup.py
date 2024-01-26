import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="hexpython",
    version="0.0.1",
    author="Elis Grahn",
    author_email="elis.grahn.2003@gmail.com",
    description="hexpy - a hobby project which eases working with hexagonal grids",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/elisgrahn/hexpy",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.10",
)
