from .core import NefitClient
from .exceptions import NefitResponseException
from .version import version, __version__

__all__ = (
    'NefitClient',
    'NefitResponseException',
    'version',
    '__version__',
)

if __name__ == "__main__":
    from .cli import CLI
    cli = CLI()
    cli.run()
