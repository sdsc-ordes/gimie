# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = "gimie"
copyright = "2023, SDSC-ORD"
author = "SDSC-ORD"
release = "0.6.1"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    "sphinx.ext.napoleon",
    "sphinx.ext.autodoc",
    "sphinx.ext.doctest",
    "sphinx.ext.intersphinx",
    "sphinx.ext.coverage",
    "sphinx.ext.viewcode",
    "sphinx.ext.githubpages",
    "sphinx.ext.autosectionlabel",
    "sphinx_click",
    "sphinx_copybutton",
    "sphinx_design",
    "myst_parser",
    "sphinxawesome_theme.highlighting",
]

templates_path = ["_templates"]

source_suffix = {
    ".rst": "restructuredtext",
    ".md": "markdown",
}


exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "sphinxawesome_theme"
html_static_path = ["_static"]
html_logo = "logo_notext.svg"
html_favicon = "favicon.ico"


# -- Extension configuration -------------------------------------------------

# Options for intersphinx

intersphinx_mapping = {
    "python": ("https://docs.python.org/", None),
    "rdflib": ("https://rdflib.readthedocs.io/en/stable/", None),
    "calamus": ("https://calamus.readthedocs.io/en/latest/", None),
}
