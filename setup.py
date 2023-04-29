from setuptools import setup, find_packages


setup(
    name="api_hunter_cli",
    version="0.2.0",
    description="CLI tool for finding hidden apis in a certain url.",
    author="Charly Molero",
    author_email="perez.moleroc@gmail.com",
    url="https://github.com/engcarlosperezmolero/api_hunter_cli",
    packages=find_packages(),
    install_requires=[
        "playwright",
        "typer[all]",
        "yaspin",
        "inquirer",
    ],
    entry_points={
        "console_scripts": [
            "apihunter=api_hunter_cli.main:app",
            "api-hunter-cli-post-install=api_hunter_cli.post_install:install_chromium",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    python_requires=">=3.7",
)
