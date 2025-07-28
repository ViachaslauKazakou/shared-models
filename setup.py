"""Setup script for shared-models package."""

from setuptools import setup, find_packages

setup(
    name="shared-models",
    packages=find_packages(),
    package_data={
        "shared_models": ["*.py"],
    },
    include_package_data=True,
)
