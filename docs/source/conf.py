import os
import sys

sys.path.insert(0, os.path.abspath('../..'))

project = 'True Core'
copyright = '2024, True Core Team'
author = 'True Core Team'
version = '1.0'
release = '1.0'

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.viewcode',
    'sphinx.ext.napoleon',
    'sphinx.ext.intersphinx',
    'sphinx_autodoc_typehints',
    'myst_parser',
    'sphinx_rtd_theme',
    'sphinx_rtd_dark_mode',
]

templates_path = ['_templates']
exclude_patterns = []
html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']

# Theme options
html_theme_options = {
    'logo_only': True,
    'navigation_depth': 4,
    'collapse_navigation': True,
    'sticky_navigation': True,
    'style_nav_header_background': '#2980B9',
}

# Dark mode configuration
dark_mode_preset = 'auto'  # Use 'light', 'dark', or 'auto'
html_css_files = [
    'dark.css',
]

# GitHub repository
html_context = {
    'display_github': True,
    'github_user': 'alaamer12',
    'github_repo': 'true-core',
    'github_version': 'main',
}

html_logo = '_static/light_true_icon.png'
html_favicon = '_static/light_true_icon.png'

# Napoleon settings
napoleon_google_docstring = True
napoleon_numpy_docstring = True
napoleon_include_init_with_doc = True
napoleon_include_private_with_doc = True
napoleon_include_special_with_doc = True
napoleon_use_admonition_for_examples = True
napoleon_use_admonition_for_notes = True
napoleon_use_admonition_for_references = True
napoleon_use_ivar = True
napoleon_use_param = True
napoleon_use_rtype = True
napoleon_type_aliases = None

# Autodoc settings
autodoc_default_options = {
    'members': True,
    'member-order': 'bysource',
    'special-members': '__init__',
    'undoc-members': True,
    'exclude-members': '__weakref__'
}

# Intersphinx settings
intersphinx_mapping = {
    'python': ('https://docs.python.org/3', None),
}

# MyST settings
myst_enable_extensions = [
    "colon_fence",
    "deflist",
]
