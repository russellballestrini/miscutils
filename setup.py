from setuptools import setup, find_packages


# get list of requirement strings from requirements.txt
def remove_whitespace(x):
    return "".join(x.split())


def sanitize(x):
    return not x.startswith("#") and x != ""


with open("requirements.txt", "r") as f:
    requires = filter(sanitize, map(remove_whitespace, f.readlines()))


setup(
    name="miscutils",
    version="0.0.07",
    description="Random misc lib utils for Python needed in lots of my projs",
    keywords="random misc lib utils for Python",
    # long_description=open("README.rst").read(),
    author="Russell Ballestrini",
    author_email="russell@ballestrini.net",
    url="https://github.com/russellballestrini/miscutils",
    platforms=["All"],
    license="Public Domain",
    packages=find_packages(),
    include_package_data=True,
    install_requires=requires,
    classifiers=[
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
    ],
)

# this isn't hosted in pypi, it's open source and you may include it using
# something like this in your project's requirements.txt.
#
# my miscutils checked out via git as an editable package.
# git+https://github.com/russellballestrini/miscutils.git#egg=miscutils
