#!/usr/bin/env python

# Configuration file for the Sphinx documentation builder.
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html


import os
import sys

import toml

sys.path.insert(0, os.path.abspath('../..'))

project_config = toml.load('../../pyproject.toml')
project = project_config['tool']['poetry']['name']
release = project_config['tool']['poetry']['version']
git_url = project_config['tool']['poetry']['repository']
copyright = project_config['tool']['sphinx']['copyright']
author = project_config['tool']['sphinx']['author']
api_dir = project_config['tool']['sphinx']['api_dir']

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.doctest',
    'sphinx.ext.linkcode',
    'sphinx.ext.autosummary',
    'sphinx.ext.coverage',
    'sphinx.ext.todo',
    'sphinx.ext.intersphinx',
    'sphinxcontrib.autoprogram',
    'sphinxcontrib.napoleon'
]

apidoc_module_dir = f'../../{api_dir}'

autoapi_type = 'python'
autoapi_dirs = [apidoc_module_dir]

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
html_theme = 'sphinx_rtd_theme'

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']


def linkcode_resolve(domain, info):
    if domain != 'py':
        return None
    if not info['module']:
        return None

    import importlib, inspect, types
    mod = importlib.import_module(info['module'])

    val = mod
    for k in info['fullname'].split('.'):
        val = getattr(val, k, None)
        if val is None:
            break

    filename = info['module'].replace('.', '/') + '.py'

    if isinstance(
            val,
            (types.ModuleType, types.MethodType, types.FunctionType, types.TracebackType, types.FrameType, types.CodeType)
    ):
        try:
            lines, first = inspect.getsourcelines(val)
            filename += '#L%d-L%d' % (first, first + len(lines) - 1)
        except (IOError, TypeError):
            pass

    return f'{git_url}/blob/main/{filename}'
