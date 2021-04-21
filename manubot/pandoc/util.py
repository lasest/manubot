import functools
import logging
import shutil
import subprocess
from typing import Any, Dict, Tuple


@functools.lru_cache()
def get_pandoc_info() -> Dict[str, Any]:
    """
    Return path and version information for the system's pandoc and
    pandoc-citeproc commands. When Pandoc is installed,
    the output will look like:
    ```python
    {
        'pandoc': True,
        'pandoc path': '/PATH_TO_EXECUTABLES/pandoc',
        'pandoc version': (2, 5),
        'pandoc-citeproc': True,
        'pandoc-citeproc path': '/PATH_TO_EXECUTABLES/pandoc-citeproc',
        'pandoc-citeproc version': (0, 15),
    }
    ```

    If the executables are missing, the output will be like:
    ```python
    {
        'pandoc': False,
        'pandoc-citeproc': False,
    }
    ```
    """
    
    stats = dict()
    update_command_info("pandoc", stats)

    if stats["pandoc version"] < (2, 11):
        update_command_info("pandoc-citeproc", stats)
    else:
        stats["pandoc-citeproc"] = False

    logging.info("\n".join(f"{k}: {v}" for k, v in stats.items()))
    return stats


def get_pandoc_version() -> Tuple[int, ...]:
    """
    Return pandoc version as tuple of major and minor
    version numbers, for example: (2, 7, 2)
    """
    pandoc_info = get_pandoc_info()
    if not pandoc_info["pandoc"]:
        # https://twitter.com/dhimmel/status/1327082301994496000
        raise ImportError("missing pandoc command on system.")
    return pandoc_info["pandoc version"]

def update_command_info(command: str, command_info_dict: dict) -> None:
    """
    Appends information about a command to the dictionary
    """

    path = shutil.which(command)
    command_info_dict[command] = bool(path)
    
    if not path:
        return
    
    version = subprocess.check_output(args=[command, "--version"], encoding="utf-8")
    logging.debug(version)
    version, *_discard = version.splitlines()
    _discard, version = version.strip().split()
    from packaging.version import parse as parse_version

    version = parse_version(version).release
    command_info_dict[f"{command} version"] = version
    command_info_dict[f"{command} path"] = path
