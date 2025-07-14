"""
Setup script for PDF Credit Card Expense Extractor.
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read the README file
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text(encoding="utf-8") if readme_file.exists() else ""

# Read requirements
requirements_file = Path(__file__).parent / "requirements.txt"
if requirements_file.exists():
    with open(requirements_file, 'r', encoding='utf-8') as f:
        requirements = [
            line.strip() 
            for line in f 
            if line.strip() and not line.startswith('#') and not line.startswith('-')
        ]
else:
    requirements = [
        "pdfplumber>=0.9.0",
        "PyYAML>=6.0",
        "tabulate>=0.9.0",
        "python-dateutil>=2.8.0",
        "colorama>=0.4.0",
        "regex>=2023.0.0"
    ]

# Filter out built-in modules and development dependencies
core_requirements = []
for req in requirements:
    # Skip built-in modules
    builtin_modules = ['argparse', 'decimal', 'configparser', 'pathlib']
    if any(req.startswith(module) for module in builtin_modules):
        continue
    
    # Skip development dependencies
    dev_deps = ['pytest', 'black', 'flake8', 'mypy', 'sphinx', 'setuptools', 'wheel', 'twine']
    if any(req.startswith(dep) for dep in dev_deps):
        continue
    
    core_requirements.append(req)

# Optional dependencies
extras_require = {
    'dev': [
        'pytest>=7.0.0',
        'pytest-cov>=4.0.0',
        'black>=23.0.0',
        'flake8>=6.0.0',
        'mypy>=1.0.0',
    ],
    'docs': [
        'sphinx>=6.0.0',
        'sphinx-rtd-theme>=1.2.0',
    ],
    'performance': [
        'psutil>=5.9.0',
        'cachetools>=5.0.0',
    ],
    'fuzzy': [
        'fuzzywuzzy>=0.18.0',
        'python-Levenshtein>=0.20.0',
    ]
}

# All optional dependencies
extras_require['all'] = [
    dep for deps in extras_require.values() for dep in deps
]

setup(
    name="pdf-credit-card-extractor",
    version="1.0.0",
    author="PDF Extractor Team",
    author_email="team@pdfextractor.com",
    description="Extract credit card transactions from PDF statements using pdfplumber",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/pdfextractor/pdf-credit-card-extractor",
    project_urls={
        "Bug Tracker": "https://github.com/pdfextractor/pdf-credit-card-extractor/issues",
        "Documentation": "https://pdf-credit-card-extractor.readthedocs.io/",
        "Source Code": "https://github.com/pdfextractor/pdf-credit-card-extractor",
    },
    
    # Package configuration
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    include_package_data=True,
    package_data={
        "pdf_extractor": [
            "patterns/*.yaml",
            "patterns/*.json",
            "config/*.yaml",
            "config/*.json",
        ],
    },
    
    # Dependencies
    python_requires=">=3.8",
    install_requires=core_requirements,
    extras_require=extras_require,
    
    # Entry points for CLI
    entry_points={
        "console_scripts": [
            "pdf-extractor=pdf_extractor.cli.main:cli_entry_point",
            "pdf-credit-extractor=pdf_extractor.cli.main:cli_entry_point",
        ],
    },
    
    # Classification
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Financial and Insurance Industry",
        "Topic :: Office/Business :: Financial",
        "Topic :: Text Processing :: Markup",
        "Topic :: Utilities",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
        "Environment :: Console",
        "Natural Language :: English",
    ],
    
    # Keywords for discovery
    keywords=[
        "pdf", "credit-card", "transactions", "extraction", "pdfplumber",
        "financial", "banking", "statement", "parser", "cli", "avianca"
    ],
    
    # Additional metadata
    license="MIT",
    platforms=["any"],
    zip_safe=False,
    
    # Test configuration
    test_suite="tests",
    tests_require=extras_require['dev'],
    
    # Options
    options={
        "bdist_wheel": {
            "universal": False,  # Not universal (Python 3 only)
        },
    },
)