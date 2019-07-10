# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# http://www.sphinx-doc.org/en/master/config

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute.
import os
import sys
import pathlib
import inspect
import subprocess


GITHUB_USER_REPO = 'UAVCAN', 'pyuavcan'

DESCRIPTION = 'A full-featured implementation of the UAVCAN protocol stack in Python.'

GIT_HASH = subprocess.check_output('git rev-parse HEAD', shell=True).decode().strip()

DOC_ROOT = pathlib.Path(__file__).absolute().parent
REPOSITORY_ROOT = DOC_ROOT.parent

# The generated files are not documented, but they must be importable to import the target package.
DSDL_GENERATED_ROOT = REPOSITORY_ROOT / '.test_dsdl_generated'

sys.path.insert(0, str(REPOSITORY_ROOT))
sys.path.insert(0, str(DSDL_GENERATED_ROOT))

import pyuavcan.application
assert '/site-packages/' not in pyuavcan.__file__, 'Wrong import source'

PACKAGE_ROOT = pathlib.Path(pyuavcan.__file__).absolute().parent

EXTERNAL_LINKS = {
    'UAVCAN homepage': 'https://uavcan.org/',
    'Support forum':   'https://forum.uavcan.org/',
}

# -- Project information -----------------------------------------------------

project = 'PyUAVCAN'
# noinspection PyShadowingBuiltins
copyright = '2019, UAVCAN Development Team'
author = 'UAVCAN Development Team'

# The short X.Y version
version = '.'.join(map(str, pyuavcan.__version_info__[:2]))
# The full version, including alpha/beta/rc tags
release = pyuavcan.__version__

# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.doctest',
    'sphinx.ext.coverage',
    'sphinx.ext.linkcode',
    'sphinx.ext.todo',
    'sphinx.ext.inheritance_diagram',
    'sphinxarg.ext',
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

# The suffix(es) of source filenames.
source_suffix = ['.rst']

# The master toctree document.
master_doc = 'index'

# Autodoc
autoclass_content = 'bysource'
autodoc_member_order = 'bysource'
autodoc_default_options = {
    'members':              True,
    'undoc-members':        True,
    'special-members':      '__init__',
    'imported-members':     True,
    'inherited-members':    True,
    'show-inheritance':     True,
    'member-order':         'bysource',
}

# For sphinx.ext.todo_
todo_include_todos = True

graphviz_output_format = 'svg'

inheritance_graph_attrs = {
    'rankdir':  'LR',
    'bgcolor':  '"transparent"',    # Transparent background works with any theme.
}
# Foreground colors are from the theme; keep them up to date, please.
inheritance_node_attrs = {
    'color':     '"#000000"',
    'fontcolor': '"#000000"',
}
inheritance_edge_attrs = {
    'color': inheritance_node_attrs['color'],
}

# -- Options for HTML output -------------------------------------------------

html_theme = 'alabaster'

html_theme_options = {
    'github_user':          GITHUB_USER_REPO[0],
    'github_repo':          GITHUB_USER_REPO[1],
    'description':          DESCRIPTION,
    'fixed_sidebar':        True,
    'page_width':           '90%',
    'sidebar_width':        '300px',
    'github_button':        True,
    'extra_nav_links':      EXTERNAL_LINKS,
    'sidebar_collapse':     False,
    'body_text':            '#000',  # black on white, no excuses
    # Fonts:
    'caption_font_family':  'sans-serif',
    'font_family':          'sans-serif',
    'caption_font_size':    '1em',
    'code_font_size':       '1em',
    'font_size':            '1em',
}

html_sidebars = {
    '**': [
        'about.html',
        'navigation.html',
        'relations.html',
        'searchbox.html',
        'donate.html',
    ]
}

html_context = {
}

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']

# ----------------------------------------------------------------------------


# Inspired by https://github.com/numpy/numpy/blob/27b59efd958313491d51bc45d5ffdf1173b8f903/doc/source/conf.py#L311
def linkcode_resolve(domain: str, info: dict):
    def report_exception(exc: Exception) -> None:
        print(f'linkcode_resolve(domain={domain!r}, info={info!r}) exception:', repr(exc), file=sys.stderr)

    if domain != 'py':
        return None

    obj = sys.modules.get(info['module'])
    for part in info['fullname'].split('.'):
        try:
            obj = getattr(obj, part)
        except Exception as ex:
            report_exception(ex)
            return None

    obj = inspect.unwrap(obj)

    if isinstance(obj, property):   # Manual unwrapping for special cases
        obj = obj.fget or obj.fset

    fn = None
    try:
        fn = inspect.getsourcefile(obj)
    except TypeError:
        pass
    except Exception as ex:
        report_exception(ex)
    if not fn:
        return None

    path = os.path.relpath(fn, start=str(REPOSITORY_ROOT))
    try:
        source_lines, lineno = inspect.getsourcelines(obj)
        path += f'#L{lineno}-L{lineno + len(source_lines) - 1}'
    except Exception as ex:
        report_exception(ex)

    return f'https://github.com/{GITHUB_USER_REPO[0]}/{GITHUB_USER_REPO[1]}/blob/{GIT_HASH}/{path}'


for p in map(str, [DSDL_GENERATED_ROOT, REPOSITORY_ROOT]):
    if os.environ.get('PYTHONPATH'):
        os.environ['PYTHONPATH'] += os.path.pathsep + p
    else:
        os.environ['PYTHONPATH'] = p

os.environ['SPHINX_APIDOC_OPTIONS'] = ','.join(k for k, v in autodoc_default_options.items() if v is True or v is None)

subprocess.check_call(
    f'sphinx-apidoc -o apidoc_generated --force --follow-links --separate --no-toc --module-first {PACKAGE_ROOT}',
    env=os.environ,
    shell=True,
)
