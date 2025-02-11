#!/usr/bin/env python
# Copyright 2016, Yahoo Inc.
# Licensed under the terms of the Apache License, Version 2.0. See the LICENSE file associated with the project for terms.
import datetime as dt
import io
import os
import re
import subprocess as sbp
from typing import Optional

from setuptools import find_packages, setup


def _version() -> str:
    """
    Grab the version from the root package.
    """
    with io.open("graphtik/__init__.py", "rt", encoding="utf8") as f:
        return re.search(r'__version__ = "(.*?)"', f.read()).group(1).strip()


def _ask_git_version() -> Optional[str]:
    try:
        return sbp.check_output(
            "git describe --always".split(), universal_newlines=True
        ).strip()
    except Exception:
        pass


version = _version()
git_ver = _ask_git_version()
txt_ver = f"{version}+{git_ver}" if git_ver and git_ver != version else version

with open("README.rst") as f:
    long_description = (
        f.read()
        .replace("|version|", txt_ver)
        .replace("|release|", txt_ver)
        .replace("|today|", dt.datetime.now().isoformat())
    )
    long_description = re.sub(
        r":(?:ref|class|rst:dir):`([^`]+?)(?: <[^>]+>)?`", r"*\1*", long_description
    )


plot_deps = [
    "pydot",
    # filter/context decorators renamed, Markup()/escape() from MarkupSafe.
    "jinja2>=3",
    # Direct use now due to jinja2-3+.
    "MarkupSafe",
]
matplot_deps = plot_deps + ["matplotlib"]
sphinx_deps = plot_deps + ["sphinx >=2", "sphinxext-opengraph"]
test_deps = list(
    set(
        matplot_deps
        + sphinx_deps
        + [
            "pytest",
            "pytest-sugar",
            "pytest-sphinx>=0.2.1",  # internal API changes
            "pytest-cov",
            "dill",
            "sphinxcontrib-spelling",
            "html5lib",  # for sphinxext TCs
            "readme-renderer",  # for PyPi landing-page
            "pandas",
        ]
    )
)
dev_deps = test_deps + ["build", "black", "pylint", "mypy", "pip-tools"]

setup(
    name="graphtik",
    version=version,
    description="A Python lib for solving & executing graphs of functions, with `pandas` in mind",
    long_description=long_description,
    long_description_content_type="text/x-rst",
    author="Kostis Anagnostopoulos, Huy Nguyen, Arel Cordero, Pierre Garrigues, Rob Hess, "
    "Tobi Baumgartner, Clayton Mellina",
    author_email="ankostis@gmail.com",
    url="http://github.com/pygraphkit/graphtik",
    project_urls={
        "Documentation": "https://graphtik.readthedocs.io/",
        "Release Notes": "https://graphtik.readthedocs.io/en/latest/changes.html",
        "Sources": "https://github.com/pygraphkit/graphtik",
        "Bug Tracker": "https://github.com/pygraphkit/graphtik/issues",
    },
    packages=find_packages(exclude=["test"]),
    package_data={
        "graphtik": ["py.typed"],
        "graphtik.sphinxext": ["*.css"],
    },
    python_requires=">=3.7",
    install_requires=[
        "networkx",
        "boltons",  # for IndexSet
    ],
    extras_require={
        ## NOTE: update also "extras" in README/quick-start section .
        "plot": plot_deps,
        "matplot": matplot_deps,
        "sphinx": sphinx_deps,
        "test": test_deps,
        # May help for pickling (deprecated) `parallel` tasks.
        # See :term:`marshalling` and :func:`set_marshal_tasks()` configuration.
        "dill": ["dill"],
        "all": dev_deps,
        "dev": dev_deps,
    },
    tests_require=test_deps,
    license="Apache-2.0",
    keywords=[
        "graph",
        "computation graph",
        "DAG",
        "directed acyclic graph",
        "executor",
        "scheduler",
        "etl",
        "workflow",
        "pipeline",
    ],
    classifiers=[
        "Development Status :: 4 - Beta",
        "License :: OSI Approved :: Apache Software License",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Natural Language :: English",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: OS Independent",
        "Operating System :: POSIX",
        "Operating System :: Unix",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Libraries",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Scientific/Engineering",
        "Topic :: Software Development",
    ],
    zip_safe=True,
    platforms="Windows,Linux,Solaris,Mac OS-X,Unix",
)
