# -*- coding: utf-8 -*-
#
# Glue documentation build configuration file, created by
# sphinx-quickstart on Mon Jun 25 12:05:47 2012.
#
# This file is execfile()d with the current directory set to its containing dir.
#
# Note that not all possible configuration values are present in this
# autogenerated file.
#
# All configuration values have a default; values that are commented out
# serve to show the default.

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#sys.path.insert(0, os.path.abspath('.'))

import os
ON_RTD = os.environ.get('READTHEDOCS') == 'True'

import warnings

# -- General configuration -----------------------------------------------------

# If your documentation needs a minimal Sphinx version, state it here.
needs_sphinx = '1.6'

# Import matplotlib now to make sure the warning doesn't cause the Sphinx build
# to fail
with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    try:
        import sip
    except ImportError:
        pass
    else:
        sip.setapi('QString', 2)
        sip.setapi('QVariant', 2)
        sip.setapi('QDate', 2)
        sip.setapi('QDateTime', 2)
        sip.setapi('QTextStream', 2)
        sip.setapi('QTime', 2)
        sip.setapi('QUrl', 2)
    import PyQt5  # noqa
    import matplotlib.pyplot as plt  # noqa

# Add any Sphinx extension module names here, as strings. They can be extensions
# coming with Sphinx (named 'sphinx.ext.*') or your custom ones.
extensions = ['sphinx.ext.autodoc', 'sphinx.ext.todo', 'sphinx.ext.coverage',
              'sphinx.ext.mathjax', 'sphinx.ext.viewcode',
              'sphinx_automodapi.automodapi', 'numpydoc',
              'sphinx.ext.intersphinx', 'sphinx_automodapi.smart_resolver',
              'sphinxcontrib.spelling']


# Add the redirect.py plugin which is in this directory
import sys
sys.path.insert(0, os.path.abspath('.'))
extensions.append('redirect')

# Workaround for RTD where the default encoding is ASCII
if ON_RTD:
    import locale
    locale.setlocale(locale.LC_ALL, 'C.UTF-8')

intersphinx_cache_limit = 10     # days to keep the cached inventories
intersphinx_mapping = {
    'sphinx': ('https://www.sphinx-doc.org/en/latest/', None),
    'python': ('https://docs.python.org/3.7', None),
    'matplotlib': ('https://matplotlib.org', None),
    'numpy': ('https://docs.scipy.org/doc/numpy', None),
    'astropy': ('http://docs.astropy.org/en/stable/', None),
    'echo': ('https://echo.readthedocs.io/en/latest/', None),
}

numpydoc_show_class_members = False
autosummary_generate = True
automodapi_toctreedirnm = 'api'

# At the moment, sphinx-automodapi causes a warning to appear about autoattribute being
# registered twice, but this will be fixed in the next release.
suppress_warnings = ['app.add_directive', 'app.add_node']

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# The suffix of source filenames.
source_suffix = '.rst'

# The encoding of source files.
#source_encoding = 'utf-8-sig'

# The master toctree document.
master_doc = 'index'

# General information about the project.
project = u'Glue'
copyright = u'2012-2019, Chris Beaumont, Thomas Robitaille, Michelle Borkin'

# The version info for the project you're documenting, acts as replacement for
# |version| and |release|, also used in various other places throughout the
# built documents.
#
from pkg_resources import get_distribution
version = release = get_distribution('glue-core').version

# The language for content autogenerated by Sphinx. Refer to documentation
# for a list of supported languages.
#language = None

# There are two options for replacing |today|: either, you set today to some
# non-false value, then it is used:
#today = ''
# Else, today_fmt is used as the format for a strftime call.
#today_fmt = '%B %d, %Y'

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
exclude_patterns = ['_build', '_templates', '.eggs']

# The reST default role (used for this markup: `text`) to use for all documents.
#default_role = None

# If true, '()' will be appended to :func: etc. cross-reference text.
#add_function_parentheses = True

# If true, the current module name will be prepended to all description
# unit titles (such as .. function::).
#add_module_names = True

# If true, sectionauthor and moduleauthor directives will be shown in the
# output. They are ignored by default.
#show_authors = False

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = 'sphinx'

# A list of ignored prefixes for module index sorting.
#modindex_common_prefix = []


# -- Options for HTML output ---------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
try:  # use ReadTheDocs theme, if installed
    import sphinx_rtd_theme
    html_theme = 'sphinx_rtd_theme'
    html_theme_path = [sphinx_rtd_theme.get_html_theme_path(), ]
except ImportError:
    pass

# Theme options are theme-specific and customize the look and feel of a theme
# further.  For a list of options available for each theme, see the
# documentation.
#html_theme_options = {}


# The name for this set of Sphinx documents.  If None, it defaults to
# "<project> v<release> documentation".
#html_title = None

# A shorter title for the navigation bar.  Default is the same as html_title.
#html_short_title = None

# The name of an image file (relative to this directory) to place at the top
# of the sidebar.
html_logo = '_static/logo.png'

# The name of an image file (within the static path) to use as favicon of the
# docs.  This file should be a Windows icon file (.ico) being 16x16 or 32x32
# pixels large.
#html_favicon = None

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']

# If not '', a 'Last updated on:' timestamp is inserted at every page bottom,
# using the given strftime format.
#html_last_updated_fmt = '%b %d, %Y'

# If true, SmartyPants will be used to convert quotes and dashes to
# typographically correct entities.
#html_use_smartypants = True

# Custom sidebar templates, maps document names to template names.
#html_sidebars = {}

# Additional templates that should be rendered to pages, maps page names to
# template names.
#html_additional_pages = {}

# If false, no module index is generated.
#html_domain_indices = True

# If false, no index is generated.
#html_use_index = True

# If true, the index is split into individual pages for each letter.
#html_split_index = False

# If true, links to the reST sources are added to the pages.
#html_show_sourcelink = True

# If true, "Created using Sphinx" is shown in the HTML footer. Default is True.
#html_show_sphinx = True

# If true, "(C) Copyright ..." is shown in the HTML footer. Default is True.
#html_show_copyright = True

# If true, an OpenSearch description file will be output, and all pages will
# contain a <link> tag referring to it.  The value of this option must be the
# base URL from which the finished HTML is served.
#html_use_opensearch = ''

# This is the file name suffix for HTML files (e.g. ".xhtml").
#html_file_suffix = None

# Output file base name for HTML help builder.
htmlhelp_basename = 'Gluedoc'


# -- Options for LaTeX output --------------------------------------------------

latex_elements = {
    # The paper size ('letterpaper' or 'a4paper').
    #'papersize': 'letterpaper',

    # The font size ('10pt', '11pt' or '12pt').
    #'pointsize': '10pt',

    # Additional stuff for the LaTeX preamble.
    #'preamble': '',
}

# Grouping the document tree into LaTeX files. List of tuples
# (source start file, target name, title, author, documentclass [howto/manual]).
latex_documents = [
    ('index', 'Glue.tex', u'Glue Documentation',
     u'Chris Beaumont, Thomas Robitaille, Michelle Borkin', 'manual'),
]

# The name of an image file (relative to this directory) to place at the top of
# the title page.
#latex_logo = None

# For "manual" documents, if this is true, then toplevel headings are parts,
# not chapters.
#latex_use_parts = False

# If true, show page references after internal links.
#latex_show_pagerefs = False

# If true, show URL addresses after external links.
#latex_show_urls = False

# Documents to append as an appendix to all manuals.
#latex_appendices = []

# If false, no module index is generated.
#latex_domain_indices = True


# -- Options for manual page output --------------------------------------------

# One entry per manual page. List of tuples
# (source start file, name, description, authors, manual section).
man_pages = [
    ('index', 'glue', u'Glue Documentation',
     [u'Chris Beaumont, Thomas Robitaille, Michelle Borkin'], 1)
]

# If true, show URL addresses after external links.
#man_show_urls = False


# -- Options for Texinfo output ------------------------------------------------

# Grouping the document tree into Texinfo files. List of tuples
# (source start file, target name, title, author,
#  dir menu entry, description, category)
texinfo_documents = [
    ('index', 'Glue', u'Glue Documentation',
     u'Chris Beaumont, Thomas Robitaille, Michelle Borkin', 'Glue', 'One line description of project.',
     'Miscellaneous'),
]

# Documents to append as an appendix to all manuals.
#texinfo_appendices = []

# If false, no module index is generated.
#texinfo_domain_indices = True

# How to display URL addresses: 'footnote', 'no', or 'inline'.
#texinfo_show_urls = 'footnote'

todo_include_todos = True
autoclass_content = 'both'

nitpick_ignore = [('py:class', 'object'), ('py:class', 'str'),
                  ('py:class', 'list'), ('py:obj', 'numpy array'),
                  ('py:obj', 'integer'), ('py:obj', 'Callable'),
                  ('py:obj', 'list'),
                  ('py:class', 'PyQt5.QtWidgets.QMainWindow'),
                  ('py:class', 'PyQt5.QtWidgets.QWidget'),
                  ('py:class', 'PyQt5.QtWidgets.QTextEdit'),
                  ('py:class', 'PyQt5.QtWidgets.QTabBar'),
                  ('py:class', 'PyQt5.QtWidgets.QLabel'),
                  ('py:class', 'PyQt5.QtWidgets.QComboBox'),
                  ('py:class', 'PyQt5.QtWidgets.QMessageBox'),
                  ('py:class', 'PyQt5.QtWidgets.QDialog'),
                  ('py:class', 'PyQt5.QtWidgets.QToolBar'),
                  ('py:class', 'PyQt5.QtWidgets.QStyledItemDelegate'),
                  ('py:class', 'PyQt5.QtCore.QMimeData'),
                  ('py:class', 'PyQt5.QtCore.QAbstractListModel'),
                  ('py:class', 'PyQt5.QtCore.QThread'),
                  ('py:obj', "str ('file' | 'directory' | 'label')"),
                  ('py:obj', 'function(application)'),
                  ('py:class', 'builtins.object'),
                  ('py:class', 'builtins.list'),
                  ('py:class', 'builtins.type'),
                  ('py:class', 'glue.viewers.histogram.layer_artist.HistogramLayerBase'),
                  ('py:class', 'glue.viewers.scatter.layer_artist.ScatterLayerBase'),
                  ('py:class', 'glue.viewers.image.layer_artist.ImageLayerBase'),
                  ('py:class', 'glue.viewers.image.layer_artist.RGBImageLayerBase'),
                  ('py:mod', 'glue.core'),
                  ('py:mod', 'glue.viewers'),
                  ('py:mod', 'glue.viewers.scatter'),
                  ('py:mod', 'glue.viewers.common'),
                  ('py:mod', 'glue.viewers.common.qt.mouse_mode'),
                  ('py:mod', 'glue.viewers.common.qt.toolbar_mode'),
                  ('py:mod', 'glue.dialogs.custom_component'),
                  ('py:class', 'glue.external.echo.core.HasCallbackProperties'),
                  ('py:class', 'glue.external.echo.core.CallbackProperty'),
                  ('py:class', 'glue.external.echo.selection.SelectionCallbackProperty'),
                  ('py:class', 'glue.viewers.image.state.BaseImageLayerState'),
                  ('py:class', 'glue.viewers.common.qt.data_viewer_with_state.DataViewerWithState')
              ]

# coax Sphinx into treating descriptors as attributes
# see https://bitbucket.org/birkenfeld/sphinx/issue/1254/#comment-7587063
from glue.utils.qt.widget_properties import WidgetProperty
WidgetProperty.__get__ = lambda self, *args, **kwargs: self

viewcode_follow_imported_members = False

linkcheck_ignore = [r'https://www.glueviz.org.s3']
linkcheck_retries = 5
linkcheck_timeout = 10
