"""pupil_labs.realtime_api"""

# .version is generated on install via setuptools_scm, see pyproject.toml
from .version import __version__, __version_info__

from .control import Control
from .discovery import discover_devices

__all__ = ["Control", "discover_devices"]
