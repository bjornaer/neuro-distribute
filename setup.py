from setuptools import setup

setup(
    name="neuro",
    version="0.0.1",
    description="process RPC calls",
    url="",
    author="Max Schulkin",
    author_email="max.schulkin@gmail.com",
    packages=["neuro"],
    zip_safe=False,
    entry_points={
        "console_scripts": [
            "neuro = neuro.server:main",
        ]
    },
)