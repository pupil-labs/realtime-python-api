#!/usr/bin/env python3
try:
    from importlib.metadata import version as import_version
except ImportError:
    from importlib_metadata import version as import_version

extensions = [
    "jaraco.packaging.sphinx",
    "rst.linker",
    "sphinx_toolbox.more_autodoc",
    "sphinx.ext.autodoc",
    "sphinx.ext.todo",
    "sphinx.ext.viewcode",
]

master_doc = "index"

link_files = {
    "../CHANGES.rst": dict(
        using=dict(GH="https://github.com"),
        replace=[
            dict(
                pattern=r"(Issue #|\B#)(?P<issue>\d+)",
                url="{package_url}/issues/{issue}",
            ),
            dict(
                pattern=r"(?m:^((?P<scm_version>v?\d+(\.\d+){1,2}))\n[-=]+\n)",
                with_scm="{text}\n{rev[timestamp]:%d %b %Y}\n",
            ),
            dict(
                pattern=r"PEP[- ](?P<pep_number>\d+)",
                url="https://peps.python.org/pep-{pep_number:0>4}/",
            ),
        ],
    )
}

# Be strict about any broken references:
nitpicky = True
nitpick_ignore = [
    ("py:class", "aiortsp.rtsp.reader.RTSPReader"),
    ("py:class", "asyncio.streams.StreamReader"),
    ("py:class", "asyncio.streams.StreamWriter"),
    ("py:class", "numpy.uint8"),
    ("py:class", "typing_extensions.Literal"),
    # TODO: find work-around for recursive reference:
    ("py:class", "pupil_labs.realtime_api.simple.device.Device"),
    ("py:class", "pupil_labs.realtime_api.streaming.gaze.DualMonocularGazeData"),
]


# Include Python intersphinx mapping to prevent failures
# jaraco/skeleton#51
extensions += ["sphinx.ext.intersphinx"]
intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "av": ("https://pyav.org/docs/stable", None),
    "numpy": ("https://numpy.org/doc/stable/", None),
    "zeroconf": ("https://python-zeroconf.readthedocs.io/en/stable/", None),
}

html_theme = "furo"
autosummary_generate = True

project = "Pupil Labs' Realtime Python API"
release = import_version("pupil-labs-realtime-api")
# for example take major/minor
version = ".".join(release.split(".")[:2])
html_title = f"{project} {release}"

todo_include_todos = True
todo_emit_warnings = True

github_username = "pupil-labs"
github_repository = "realtime-python-api"
