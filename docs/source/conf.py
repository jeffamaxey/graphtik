# Copyright 2016, Yahoo Inc.
# Licensed under the terms of the Apache License, Version 2.0. See the LICENSE file associated with the project for terms.

# -*- coding: utf-8 -*-
#
# graphtik documentation build configuration file, created by
# sphinx-quickstart on Tue Jun 16 19:10:27 2016.
#
# This file is execfile()d with the current directory set to its
# containing dir.
#
# Note that not all possible configuration values are present in this
# autogenerated file.
#
# All configuration values have a default; values that are commented out
# serve to show the default.

import doctest
import importlib
import inspect
import io
import logging
import os
import re
import subprocess as sbp
import sys
from functools import partial

import packaging.version
from enchant.tokenize import (
    EmailFilter,
    Filter,
    MentionFilter,
    URLFilter,
    unit_tokenize,
)
from sphinx.application import Sphinx

from graphtik.config import set_plot_annotator
from graphtik.base import default_plot_annotator

log = logging.getLogger(__name__)


# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
sys.path.insert(0, os.path.abspath("../../"))

# -- General configuration ------------------------------------------------

# If your documentation needs a minimal Sphinx version, state it here.
needs_sphinx = "2.0"

os.environ["PYENCHANT_IGNORE_MISSING_LIB"] = "1"

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.coverage",
    "sphinx.ext.linkcode",
    "sphinx.ext.extlinks",
    "sphinx.ext.intersphinx",
    # "sphinx.ext.doctest",  # doctests maintained by pytest
    "sphinxcontrib.spelling",
    "graphtik.sphinxext",
]


# Need functional doctests for graphtik-directive to work ok.
doctest_default_flags = (
    doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS | doctest.REPORT_NDIFF
)

extlinks = {
    "gh": ("https://github.com/yahoo/graphkit/issues/%s", "yahoo#"),
    "gg": ("https://github.com/pygraphkit/graphtik/issues/%s", "#"),
}

## Plot graphs with links to docs & tooltips with sources.
set_plot_annotator(
    partial(default_plot_annotator, url_fmt="../reference.html#%s", link_target="_top")
)

try:
    git_commit = sbp.check_output("git rev-parse HEAD".split()).strip().decode()
except Exception:
    git_commit = None

github_slug = "pygraphkit/graphtik"


def linkcode_resolve(domain, info):
    """Produce URLs to GitHub sources, for ``sphinx.ext.linkcode``"""
    if domain != "py":
        return None
    if not info["module"]:
        return None

    modname = info["module"]
    item = importlib.import_module(modname)
    filename = modname.replace(".", "/")
    if git_commit:
        uri = f"https://github.com/{github_slug}/blob/{git_commit}/{filename}.py"
    else:
        uri = f"https://github.com/{github_slug}/blob/master/{filename}.py"

    ## Get the lineno from the last valid object
    # that has one.
    #
    item_name = info["fullname"]
    step_names = item_name.split(".")
    steps = []
    for name in step_names:
        child = getattr(item, name, None)
        if not child:
            break
        item = child
        steps.append((name, item))
    for name, item in reversed(steps):
        try:
            source, lineno = inspect.getsourcelines(item)
            end_lineno = lineno + len(source) - 1
            uri = f"{uri}#L{lineno}-L{end_lineno}"
            break
        except TypeError as ex:
            assert "module, class, method, function," in str(ex), ex
        except Exception as ex:
            log.warning(
                "Ignoring error while linking sources of '%s:%s': %s(%s)",
                modname,
                item_name,
                type(ex).__name__,
                ex,
            )

    return uri


rst_epilog = """
.. _Graphkit: https://github.com/yahoo/graphkit
.. _Graphviz: https://graphviz.org
.. _pydot: https://github.com/pydot/pydot
.. |pydot.Dot| replace:: ``pydot.Dot``
.. _pydot.Dot: https://github.com/pydot/pydot
"""


class SpellingFilter(Filter):
    """Skip small 3-letter words."""

    def _plot(self, word):
        return unit_tokenize(word.lower())

    def _skip(self, word):
        return len(word) <= 3


# spelling_word_list_filename = "spelling_wordlist.txt"
spelling_filters = [SpellingFilter, MentionFilter, URLFilter]

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# The suffix of source filenames.
source_suffix = ".rst"

# The encoding of source files.
# source_encoding = 'utf-8-sig'

# The master toctree document.
master_doc = "index"

# General information about the project.
project = "graphtik"
copyright = "2016, Yahoo Vision and Machine Learning Team: Huy Nguyen, Arel Cordero, Pierre Garrigues, Tobi Baumgartner, Rob Hess"

# The version info for the project you're documenting, acts as replacement for
# |version| and |release|, also used in various other places throughout the
# built documents.

# Parse the Travis tag as a version, if it's available, or else use a default.
try:
    with io.open("../../graphtik/__init__.py", "rt", encoding="utf8") as f:
        version = re.search(r'__version__ = "(.*?)"', f.read()).group(1)
except FileNotFoundError:
    version = "0.0.0"
version = f"src: {version}"

try:
    git_ver = sbp.check_output("git describe --always".split(), universal_newlines=True)
    version = f"{version}, git: {git_ver}"
except Exception:
    pass

version_str = os.environ.get("TRAVIS_TAG", version)
version_parse = packaging.version.parse(version_str)

# The short X.Y version.
version = ".".join(version_parse.public.split(".")[:2])
# The full version, including alpha/beta/rc tags.
release = version_parse.public

# The language for content autogenerated by Sphinx. Refer to documentation
# for a list of supported languages.
# language = None

# There are two options for replacing |today|: either, you set today to some
# non-false value, then it is used:
# today = ''
# Else, today_fmt is used as the format for a strftime call.
# today_fmt = '%B %d, %Y'

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
exclude_patterns = []

# The reST default role (used for this markup: `text`) to use for all
# documents.
# default_role = None

# If true, '()' will be appended to :func: etc. cross-reference text.
# add_function_parentheses = True

# If true, the current module name will be prepended to all description
# unit titles (such as .. function::).
# add_module_names = True

# If true, sectionauthor and moduleauthor directives will be shown in the
# output. They are ignored by default.
# show_authors = False

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = "sphinx"

# A list of ignored prefixes for module index sorting.
# modindex_common_prefix = []

# If true, keep warnings as "system message" paragraphs in the built documents.
# keep_warnings = False


# -- Options for HTML output ----------------------------------------------

# Theme options are theme-specific and customize the look and feel of a theme
# further.  For a list of options available for each theme, see the
# documentation.
html_theme_options = {}

# The name for this set of Sphinx documents.  If None, it defaults to
# "<project> v<release> documentation".
# html_title = None

# A shorter title for the navigation bar.  Default is the same as html_title.
# html_short_title = None

# The name of an image file (relative to this directory) to place at the top
# of the sidebar.
# html_logo = None

# The name of an image file (within the static path) to use as favicon of the
# docs.  This file should be a Windows icon file (.ico) being 16x16 or 32x32
# pixels large.
# html_favicon = None

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
# html_static_path = ['_static']

# Add any extra paths that contain custom files (such as robots.txt or
# .htaccess) here, relative to this directory. These files are copied
# directly to the root of the documentation.
# html_extra_path = []

# If not '', a 'Last updated on:' timestamp is inserted at every page bottom,
# using the given strftime format.
html_last_updated_fmt = "%b %d, %Y"

# If true, SmartyPants will be used to convert quotes and dashes to
# typographically correct entities.
# html_use_smartypants = True

# Custom sidebar templates, maps document names to template names.
# html_sidebars = {}

# Additional templates that should be rendered to pages, maps page names to
# template names.
# html_additional_pages = {}

# If false, no module index is generated.
# html_domain_indices = True

# If false, no index is generated.
# html_use_index = True

# If true, the index is split into individual pages for each letter.
# html_split_index = False

# If true, links to the reST sources are added to the pages.
html_show_sourcelink = False

# If true, "Created using Sphinx" is shown in the HTML footer. Default is True.
# html_show_sphinx = True

# If true, "(C) Copyright ..." is shown in the HTML footer. Default is True.
# html_show_copyright = True

# If true, an OpenSearch description file will be output, and all pages will
# contain a <link> tag referring to it.  The value of this option must be the
# base URL from which the finished HTML is served.
# html_use_opensearch = ''

# This is the file name suffix for HTML files (e.g. ".xhtml").
# html_file_suffix = None

# Output file base name for HTML help builder.
htmlhelp_basename = "graphtikdoc"


# -- Options for LaTeX output ---------------------------------------------

latex_elements = {
    # The paper size ('letterpaper' or 'a4paper').
    #'papersize': 'letterpaper',
    # The font size ('10pt', '11pt' or '12pt').
    #'pointsize': '10pt',
    # Additional stuff for the LaTeX preamble.
    #'preamble': '',
}

# Grouping the document tree into LaTeX files. List of tuples
# (source start file, target name, title,
#  author, documentclass [howto, manual, or own class]).
latex_documents = [
    (
        "index",
        "graphtik.tex",
        "graphtik Documentation",
        "Yahoo Vision and Machine Learning Team: Huy Nguyen, Arel Cordero, Pierre Garrigues, Tobi Baumgartner, Rob Hess",
        "manual",
    )
]

# The name of an image file (relative to this directory) to place at the top of
# the title page.
# latex_logo = None

# For "manual" documents, if this is true, then toplevel headings are parts,
# not chapters.
# latex_use_parts = False

# If true, show page references after internal links.
# latex_show_pagerefs = False

# If true, show URL addresses after external links.
# latex_show_urls = False

# Documents to append as an appendix to all manuals.
# latex_appendices = []

# If false, no module index is generated.
# latex_domain_indices = True


# -- Options for manual page output ---------------------------------------

# One entry per manual page. List of tuples
# (source start file, name, description, authors, manual section).
man_pages = [
    (
        "index",
        "graphtik",
        "graphtik Documentation",
        [
            "Yahoo Vision and Machine Learning Team: Huy Nguyen, Arel Cordero, Pierre Garrigues, Tobi Baumgartner, Rob Hess"
        ],
        1,
    )
]

# If true, show URL addresses after external links.
# man_show_urls = False


# -- Options for Texinfo output -------------------------------------------

# Grouping the document tree into Texinfo files. List of tuples
# (source start file, target name, title, author,
#  dir menu entry, description, category)
texinfo_documents = [
    (
        "index",
        "graphtik",
        "graphtik Documentation",
        "Yahoo Vision and Machine Learning Team: Huy Nguyen, Arel Cordero, Pierre Garrigues, Tobi Baumgartner, Rob Hess",
        "graphtik",
        "It's DAGs all the way down.",
        "Miscellaneous",
    )
]

# Documents to append as an appendix to all manuals.
# texinfo_appendices = []

# If false, no module index is generated.
# texinfo_domain_indices = True

# How to display URL addresses: 'footnote', 'no', or 'inline'.
# texinfo_show_urls = 'footnote'

# If true, do not generate a @detailmenu in the "Top" node's menu.
# texinfo_no_detailmenu = False

# Example configuration for intersphinx: refer to the Python standard library.
intersphinx_mapping = {
    "python": ("https://docs.python.org/3.8/", None),
    "networkx": ("https://networkx.github.io/documentation/latest/", None),
    "boltons": ("https://boltons.readthedocs.io/en/latest/", None),
    "dill": ("https://dill.readthedocs.io/en/latest/", None),
    "sphinx": ("https://www.sphinx-doc.org/en/master/", None),
}


def setup(app: Sphinx):
    # for documenting the configurations of the new `graphtik` directive.
    app.add_object_type(
        "confval",
        "confval",
        objname="configuration value",
        indextemplate="pair: %s; configuration value",
    )
