import setuptools


with open('requirements.txt') as f:
    install_requires = list(f)

setuptools.setup(
    use_scm_version=True,
    setup_requires=['setuptools_scm'],
    install_requires=install_requires,
)
