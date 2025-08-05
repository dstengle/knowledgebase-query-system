from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="kb-query-interface",
    version="0.1.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="Natural language query interface for RDF knowledge bases",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/kb-query-interface",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    python_requires=">=3.8",
    install_requires=[
        "rdflib>=6.2.0",
        "SPARQLWrapper>=2.0.0",
        "pyyaml>=6.0",
        "nltk>=3.8",
    ],
    extras_require={
        "dev": [
            "pytest>=7.2.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "mypy>=1.0.0",
        ],
        "nlp": [
            "spacy>=3.5.0",
            "wordnet>=0.1.0",
            "gensim>=4.3.0",
        ],
        "api": [
            "fastapi>=0.95.0",
            "uvicorn>=0.21.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "kb-query=kb_query.cli:main",
        ],
    },
)
