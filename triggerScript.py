#!/usr/bin/env python3
import os
import sys
import platform
from packaging import version
import logging


PID = os.getpid()
print(f"*** Starting ***\nPID: {PID}")
curDir = os.path.dirname(os.path.realpath(__file__))
scriptName = (os.path.basename(__file__)).removesuffix(".py")
log = logging.getLogger(scriptName)
log.setLevel(logging.DEBUG)
logging.addLevelName(logging.DEBUG, "DBUG")

handleConsole = logging.StreamHandler(sys.stdout)
handleConsole.setFormatter(logging.Formatter("%(asctime)s | %(message)s", "%H:%M:%S"))
handleConsole.setLevel(logging.DEBUG)
log.addHandler(handleConsole)

if version.parse(platform.python_version()) < version.parse("3.10.0"):
    log.critical("Python 3.10.0 or greater is required!")
    exit()

from triggerConfig import triggerConfig as tCon

handleFile = logging.FileHandler(
    filename=f"{curDir}{os.sep}{scriptName}.log",
    encoding="utf-8",
    mode="a",
)
handleFile.setFormatter(
    logging.Formatter(
        "%(asctime).19s %(created).2f | %(levelname).4s |:| %(funcName)s | %(message)s",
    )
)
handleFile.setLevel((tCon.logLevel).upper())
log.addHandler(handleFile)


log.critical(
    f"""Starting...
    PID: {PID}
    Platform: {platform.system()} | {platform.node()}
    Python: {platform.python_version()}
    Current directory: {curDir}
    Current working: {os.getcwd()}"""
)


def _checkExists(items: list, make: bool = False) -> bool:
    """Checks if any files/folders in a list are missing"""
    log.debug("run")
    bad = []
    for item in items:
        itemFull = os.path.join(curDir, item)
        if not os.path.exists(itemFull):
            log.error(f"File/Folder Missing: {item}")
            bad.append(itemFull)
    if len(bad) == 0:
        return True
    elif make:
        for element in bad:
            try:
                os.mkdir(element)
            except Exception as xcp:
                log.exception("CheckMake")
                exit()


def _checkTargetDir(make: bool = False) -> bool:
    log.info("Checking for target dir (and archive dir)")
    items = [tCon.targetDirectory]
    if tCon.gitHub is True:
        items.append(tCon.targetArchive)
    return _checkExists(items=items, make=make)


if not _checkTargetDir():
    log.warning("Required folders missing! Attempting to create...")
    if _checkTargetDir(make=True):
        log.info("Folders Created!")


def _checkTargetScr() -> bool:
    log.info("Checking for target script")
    return _checkExists(items=[os.path.join(tCon.targetDirectory, tCon.targetScript)])


if not _checkTargetScr():
    log.critical("Target Script Not Found!")
    exit()

"python -m ensurepip --upgrade"
