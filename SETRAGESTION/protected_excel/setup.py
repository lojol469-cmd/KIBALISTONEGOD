from setuptools import setup
from Cython.Build import cythonize  # type: ignore

setup(
    name="license_manager",
    ext_modules=cythonize("license_manager.pyx"),
)