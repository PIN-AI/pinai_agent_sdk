from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="pinai-agent-sdk",
    version="0.1.23",
    packages=find_packages(),
    install_requires=requirements,
    author="smile",
    author_email="smile@pinai.io",
    description="SDK for PINAI Agent API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://pinai.io",
    project_urls={
        "Bug Tracker": "https://github.com/yourusername/pinai-agent-sdk/issues",
        "Documentation": "https://docs.pinai.io",
        "Source Code": "https://github.com/yourusername/pinai-agent-sdk",
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.10",
    keywords="pinai, agent, sdk, api, machine learning, ai",
) 