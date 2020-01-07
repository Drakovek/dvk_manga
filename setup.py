import setuptools

console_scripts = [
    "dvk-mangadex = dvk_manga.mangadex:main",
    "dvk-manga-test = dvk_manga.tests.test_mangadex:main"]

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="dvk-manga",
    version="0.2.6",
    author="Drakovek",
    author_email="DrakovekMail@gmail.com",
    description="Modules for downloading manga in the .dvk file format.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Drakovek/dvk_manga",
    packages=setuptools.find_packages(),
    install_requires=["beautifulsoup4", "dvk-archive", "tqdm"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent"
    ],
    python_requires='>=3.6',
    entry_points={"console_scripts": console_scripts}
)
