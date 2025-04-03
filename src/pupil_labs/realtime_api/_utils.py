import warnings
from collections.abc import Callable
from functools import wraps
from typing import Any, TypeVar, cast

F = TypeVar("F", bound=Callable[..., Any])


def deprecated(
    since: str,
    removal_in: str | None = None,
    alternative: str | None = None,
    message: str | None = None,
) -> Callable[[F], F]:
    """Add decorator to mark functions or methods as deprecated.

    Args:
        since: Version when the function was first deprecated.
        removal_in: Version when the function will be removed.
        alternative: Suggested alternative to use instead.
        message: Custom message to include in the warning.

    Returns:
        Decorated function that issues a deprecation warning when called.

    """

    def decorator(func: F) -> F:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            warning_message = f"{func.__name__} is deprecated since version {since}."

            if removal_in:
                warning_message += f" It will be removed in version {removal_in}."

            if alternative:
                warning_message += f" Use {alternative} instead."

            if message:
                warning_message += f" {message}"

            warnings.warn(warning_message, DeprecationWarning, stacklevel=2)
            return func(*args, **kwargs)

        if func.__doc__:
            func.__doc__ += f"\n\n.. deprecated:: {since}\n"
            if removal_in:
                func.__doc__ += f"   Will be removed in version {removal_in}.\n"
            if alternative:
                func.__doc__ += f"   Use {alternative} instead.\n"
            if message:
                func.__doc__ += f"   {message}\n"

        return cast(F, wrapper)

    return decorator
