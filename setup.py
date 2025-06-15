from setuptools import setup, find_packages

setup(
    name="piv",
    version="0.1.0",
    author="Nikol Tamayo",
    description="Paquete de análisis financiero para Meta Platforms con modelo ARIMA y dashboard",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
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
        "plotly",
        "streamlit"
    ],
    include_package_data=True,
    python_requires=">=3.8"
)

