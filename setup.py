import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("LICENSE.txt", "r", encoding="utf-8") as fh:
    license = fh.read()

setuptools.setup(
    name="aoh",
    version="0.1",
    author="Daniele Baisero",
    author_email="daniele.baisero@gmail.com",
    description="A package to for AOH model development",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gitlab.com/daniele.baisero/aoh",
    packages=setuptools.find_packages(),
    license=license,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: ISC",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.8',
    install_requires=['gdal'],
    extras_require={
        'test': ['pytest'],
        'apps': ['iucn_modlib @ git+https://gitlab.com/daniele.baisero/iucn-modlib', 'pandas']}
    )