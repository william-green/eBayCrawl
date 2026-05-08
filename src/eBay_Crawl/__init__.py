def __getattr__(name):
    if name == "main":
        from .main import main as _main

        return _main
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = ["main"]
