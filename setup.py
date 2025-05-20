#!/usr/bin/env python3
from setuptools import setup, find_packages

setup(
    name="mcp-pitagoras",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "mcp>=1.5.0",
        "pandas>=2.0.0",
        "numpy>=1.24.0",
        "scipy>=1.10.0",
        "scikit-learn>=1.2.0",
        "matplotlib>=3.7.0",
        "seaborn>=0.12.0",
        "python-dotenv>=1.0.0",
        "httpx>=0.24.0",
        "plotly>=5.13.0",
        "statsmodels>=0.14.0"
    ],
    entry_points={
        "console_scripts": [
            "mcp-pitagoras=mcp_server.main:main",
        ],
    },
    author="MCP Pitagoras Team",
    author_email="info@example.com",
    description="MCP server for Pitagoras API integration and data analysis",
    python_requires=">=3.9",
)