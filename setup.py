from setuptools import setup, find_packages

setup(
    name="pyan",
    setup_requires=["setuptools_scm"],
    use_scm_version=True,
    description="Offline call graph generator for Python 3",
    url="https://github.com/itsayellow/pyan",
    packages=find_packages(),
    include_package_data=True,
    entry_points={"console_scripts": ["pyan=pyan.pyan:main"]},
    zip_safe=False,
)
