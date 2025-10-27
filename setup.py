from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("LICENSE", "r", encoding="utf-8") as fh:
    license_text = fh.read()

setup(
    name="dev-reload-utilites",
    version="0.1.0",
    author="Aleksandr Dragunkin",
    author_email="alexandr69@gmail.com",
    description="Utility for centralized management of module reboots in the K3-Mebel 8.1 application",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/your-username/dev_reload_utilites",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Microsoft :: Windows :: Windows 7",
        "Operating System :: Microsoft :: Windows :: Windows 10",
        "Operating System :: Microsoft :: Windows :: Windows 11",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
    ],
    python_requires='>=3.7',
    install_requires=[
        "loguru",
    ],
    package_data={
        'dev_reload_utilites': ['*.py', '.def_module_name'],
    },
    include_package_data=True,
)