from setuptools import setup
from setuptools import find_packages

# TODO
# nltk.download('perluniprops')
# ^ I had to run that in the Python interpreter to make the build work.
# This prob shouldn't happen.

setup(
    name="emojipasta",
    description="Generate emojipasta from text.",
    version="1.0.0",
    url="https://github.com/Kevinpgalligan/emojipasta",
    author="Kevin Galligan",
    author_email="galligankevinp@gmail.com",
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules"
    ],
    packages=find_packages("src"),
    package_dir={'': 'src'},
    install_requires=[
        "nltk"
    ]
)
