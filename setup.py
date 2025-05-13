from setuptools import setup, find_packages
setup(
    name="edu_pad",
    version="0.0.1",
    author="Juliana Pena",
    author_email="juliana.pena@est.iudigital.edu.co",
    description="",
    py_modules=["actividad1","actividad2"],
    install_requires=[
        "pandas",
        "openpyxl",
        "requests",
        "beautifulsoup4",
        "sqlalchemy"
    ]
)
#pip install -e .
