# Pupil Labs Real-Time Python API Client

[![ci](https://github.com/pupil-labs/realtime-python-api/actions/workflows/main.yml/badge.svg)](https://github.com/pupil-labs/realtime-python-api/actions/workflows/main.yml)
[![documentation](https://img.shields.io/badge/docs-mkdocs-708FCC.svg?style=flat)](https://pupil-labs.github.io/realtime-python-api/)
[![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/uv)
[![ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![pre-commit](https://img.shields.io/badge/pre_commit-black?logo=pre-commit&logoColor=FAB041)](https://github.com/pre-commit/pre-commit)
[![pypi version](https://img.shields.io/pypi/v/pupil-labs-realtime-api.svg)](https://pypi.org/project/pupil-labs-realtime-api/)
[![python versions](https://img.shields.io/pypi/pyversions/pupil-labs-realtime-api)](https://pypi.org/project/pupil-labs-realtime-api/)

Python Client for the Pupil Labs Real-Time API

`pupil_labs.realtime_api` is a Python module to wrap around the [Pupil Labs Real-Time Network API](https://github.com/pupil-labs/realtime-network-api).

It also offers some convenience functions like gaze↔frame matching and exposes easy-to-use functions and classes to get started without having to know much about advanced programming or network communication!

## Installation

```
pip install pupil-labs-realtime-api
```

or

```bash
pip install -e git+https://github.com/pupil-labs/realtime-python-api.git
```

> [!IMPORTANT]
> This package is only available for Pupil Invisible and Neon, Pupil Core uses a different API. Please have a look at:
> [Pupil Core Network API](https://docs.pupil-labs.com/core/developer/network-api/) if you need streaming capabilities > for Pupil Core.
