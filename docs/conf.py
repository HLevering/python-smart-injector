# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.coverage",
    "sphinx.ext.doctest",
    "sphinx.ext.extlinks",
    "sphinx.ext.ifconfig",
    "sphinx.ext.napoleon",
    "sphinx.ext.todo",
    "sphinx.ext.viewcode",
]
doctest_global_setup = """
from smart_injector import create_container, StaticContainer, Lifetime, Config
"""
source_suffix = ".rst"
master_doc = "index"
project = "Smart Injector"
year = "2019"
author = "Hendrik Levering"
copyright = "{0}, {1}".format(year, author)
version = release = "0.0.6"

pygments_style = "trac"
templates_path = ["."]
extlinks = {
    "issue": ("https://github.com/hlevering/python-smart-injector/issues/%s", "#"),
    "pr": ("https://github.com/hlevering/python-smart-injector/pull/%s", "PR #"),
}
import sphinx_rtd_theme

html_theme = "sphinx_rtd_theme"
html_theme_path = [
    "_themes",
]
# html_theme_options = {
#    'githuburl': 'https://github.com/hlevering/python-smart-injector/'
# }

html_use_smartypants = True
html_last_updated_fmt = "%b %d, %Y"
html_split_index = False
html_sidebars = {
    "**": ["searchbox.html", "globaltoc.html", "sourcelink.html"],
}
html_short_title = "%s-%s" % (project, version)

napoleon_use_ivar = True
napoleon_use_rtype = False
napoleon_use_param = False
