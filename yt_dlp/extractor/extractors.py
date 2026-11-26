import contextlib
import os

from ..plugins import load_plugins

# Attempt to import the lazy loader. If this fails, surface the ImportError
# instead of silently falling back to the eager import path which can mask
# the underlying missing-dependency error.
try:
    from .lazy_extractors import _LAZY_LOADER, _PLUGIN_CLASSES, _ALL_CLASSES
except ImportError:
    # Re-raise so CI/tools see the real cause instead of importing the
    # eager extractor bundle (which may pull in unavailable optional
    # dependencies and produce confusing ModuleNotFoundError later).
    raise

# NB: Must be before other imports so that plugins can be correctly injected
_PLUGIN_CLASSES = load_plugins("extractor", "IE")

_LAZY_LOADER = False
if not os.environ.get("YTDLP_NO_LAZY_EXTRACTORS"):
    with contextlib.suppress(ImportError):
        from .lazy_extractors import *  # noqa: F403
        from .lazy_extractors import _ALL_CLASSES

        _LAZY_LOADER = True

if not _LAZY_LOADER:
    from ._extractors import *  # noqa: F403

    _ALL_CLASSES = [  # noqa: F811
        klass
        for name, klass in globals().items()
        if name.endswith("IE") and name != "GenericIE"
    ]
    _ALL_CLASSES.append(GenericIE)  # noqa: F405

globals().update(_PLUGIN_CLASSES)
_ALL_CLASSES[:0] = _PLUGIN_CLASSES.values()

from .common import _PLUGIN_OVERRIDES  # noqa: F401
