import pupil_labs.realtime_api as this_project


def test_package_metadata() -> None:
    assert hasattr(this_project, "__version__")
    assert this_project.__version__ != "unknown"


def test_import_basic() -> None:
    import pupil_labs.realtime_api.simple as simple_module

    assert simple_module
