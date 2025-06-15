from setuptools import setup, find_packages
setup(
    name="piv",
    version="0.0.1",
    author="Nikol Tamayo",
    author_email="",
    description="",
    py_modules=["actividad1","actividad2"],
    install_requires=[
        "pandas==2.2.3",
        "openpyxl",
        "requests==2.32.3",
        "beautifulsoup4",
        "sqlalchemy",
        "scikit-learn>=0.24.0",
        "matplotlib",
        "seaborn",
        "statsmodels",
        "streamlit",
        "plotly"
    ]
)

