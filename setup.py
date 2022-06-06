from setuptools import setup, find_namespace_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

with open("VERSION", "r") as fh:
    version = fh.read().strip()

setup(
    name="cltl.factual_question_processing",
    description="The Leolani Responder module for factual question answering",
    version=version,
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/leolani/cltl-questionprocessor",
    license='MIT License',
    authors={
        "Krause": ("Lea Krause", "l.krause@vu.nl"),
        "Baez Santamaria": ("Selene Baez Santamaria", "s.baezsantamaria@vu.nl"),
        "Baier": ("Thomas Baier", "t.baier@vu.nl")
    },
    package_dir={'': 'src'},
    packages=find_namespace_packages(include=['cltl.*', 'cltl_service.*'], where='src'),
    package_data={'cltl.factual_question_processing': []},
    python_requires='>=3.7',
    install_requires=[
        'requests~=2.25',
        "cltl.combot"
    ],
    extras_require={
        "service": [
            "cltl.combot",
            "emissor"
        ]
    },
    setup_requires=['flake8']
)
