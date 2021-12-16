"""pupil_labs.realtime_api"""

# .version is generated on install via setuptools_scm, see pyproject.toml
from .control import Control
from .discovery import discover_devices
from .version import __version__, __version_info__

__all__ = ["Control", "discover_devices"]
