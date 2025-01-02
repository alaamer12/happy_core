import os
import sys

sys.path.insert(0, os.path.abspath('../..'))

project = 'True Core'
copyright = '2025, True Core Team'
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
    'sphinx_copybutton',
    'sphinx_design',
    'sphinx_tabs.tabs',
    'sphinx_togglebutton',
    'notfound.extension',
    'sphinx_last_updated_by_git',
    'sphinxcontrib.spelling',
    'sphinx_sitemap',
    'versionwarning.extension',
    'sphinxext.opengraph',
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
    'style_nav_header_background': '#2b2b2b',
}

# Dark mode configuration
dark_mode_preset = 'auto'  # Use 'light', 'dark', or 'auto'
dark_mode_code = True
dark_mode_static = True
dark_mode_force_default_theme = True
dark_mode_disable_show_theme_credit = True  # This will remove the credit line
html_css_files = [
  'css/custom.css',
    'dark.css',
]

html_js_files = [
    'js/custom.js',
]

# GitHub repository
html_context = {
    'display_github': True,
    'github_user': 'alaamer12',
    'github_repo': 'true-core',
    'github_version': 'main',
     # Social media links
    'display_github': True,
    'github_user': 'alaamer12',
    'github_repo': 'true-core',
    'github_version': 'main',
    # Additional social links
    'extra_nav_links': {
        'GitHub': 'https://github.com/alaamer12/true-core',
        'PyPI': 'https://pypi.org/project/true-core/',
        # 'Twitter': 'https://twitter.com/alaamer12',  # Replace with your Twitter
        'LinkedIn': 'https://linkedin.com/in/alaamer12',  # Replace with your LinkedIn
    }
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
    "html_image",
    "html_admonition",
    "attrs_inline",
    "replacements",
    "smartquotes",
]

# Copybutton settings
copybutton_prompt_text = r">>> |\.\.\. |\$ |In \[\d*\]: | {2,5}\.\.\.: | {5,8}: "
copybutton_prompt_is_regexp = True

# Sitemap configuration
html_baseurl = 'https://true-core.readthedocs.io/'
sitemap_filename = 'sitemap.xml'
sitemap_url_scheme = '{link}'
sitemap_locales = [None]
sitemap_include_hidden = False

# 404 page configuration
notfound_template = '404.rst'  # Just the filename, not the path
notfound_pagename = '404'
notfound_default_language = 'en'
notfound_urls_prefix = ''

# Last updated by git configuration
html_last_updated_fmt = '%Y-%m-%d'
git_last_updated_mode = 'date'

# Spelling configuration
spelling_lang = 'en_US'
spelling_word_list_filename = 'spelling_wordlist.txt'
spelling_ignore_pypi_package_names = True
spelling_ignore_python_builtins = True
spelling_ignore_importable_modules = True

# Version warning configuration
versionwarning_messages = {
    'latest': ('You are viewing the development version. '
              'The latest stable version is {latest}'),
    '0.1.3': ('You are viewing version 0.1.3 documentation. '
              'This version contains components that have been moved to separate packages in 0.2.0. '
              'See the :doc:`migration_v0.2.0` and :doc:`changelogs/0.2.0` for details.'),
    '0.1.2': ('You are viewing version 0.1.2 documentation. '
              'This version contains components that have been moved to separate packages in 0.2.0. '
              'Please upgrade to version 0.2.0 and follow the migration guide.'),
    '0.1.1': ('You are viewing version 0.1.1 documentation. '
              'This version contains components that have been moved to separate packages in 0.2.0. '
              'Please upgrade to version 0.2.0 and follow the migration guide.'),
    '0.1.0': ('You are viewing version 0.1.0 documentation. '
              'This version contains components that have been moved to separate packages in 0.2.0. '
              'Please upgrade to version 0.2.0 and follow the migration guide.'),
}

versionwarning_default_message = ('You are viewing an old version of True Core documentation. '
                                'Some components shown here have been moved to separate packages in version 0.2.0.')

versionwarning_banner_title = 'Version Notice'
versionwarning_body_selector = 'div[role="main"]'
versionwarning_project_version = release
versionwarning_project_slug = 'true-core'
versionwarning_admonition_type = 'warning'
versionwarning_banner_included_versions = True
versionwarning_default_admonition_type = 'warning'

versionwarning_page_messages = {
    'api_reference.html': ('⚠️ API Breaking Changes: Many components shown in this version '
                         'have been moved to separate packages in version 0.2.0.'),
    'installation.html': ('⚠️ Installation Changes: As of version 0.2.0, additional packages '
                        'need to be installed for full functionality.'),
}

# OpenGraph configuration
ogp_site_url = "https://true-core.readthedocs.io/"
ogp_site_name = "True Core Documentation"
ogp_image = "_static/light_true_icon.png"
ogp_use_first_image = True
ogp_description_length = 300
ogp_type = "website"
ogp_custom_meta_tags = [
    # '<meta name="twitter:card" content="summary_large_image">',
    # '<meta name="twitter:site" content="@alaamer12">',  # Replace with your Twitter handle
    '<meta property="og:locale" content="en_US">',
    '<meta property="og:site_name" content="True Core">',
    '<meta property="og:title" content="True Core - A Boilerplate Utility Package">',
    '<meta property="og:description" content="A comprehensive Python utility package providing boilerplate code and common functionality.">',
    '<meta name="theme-color" content="#2b2b2b">',
]

html_show_sourcelink = False
html_show_sphinx = False
html_show_copyright = True