from setuptools import setup, find_packages

setup(
    name="GreenTrace",
    version="0.1.1",
    packages=find_packages(),
    install_requires=[
        "psutil>=7.2.2",
        "py-cpuinfo>=9.0.0",
    ],
    description="Effortless CO₂ Emissions Tracking for Python Code",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/so89bur/GreenTrace",
    author="Sov Bur",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
)
