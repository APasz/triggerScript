#!/usr/bin/env python3
import json
import logging
import os
import platform
import shutil
import subprocess
import sys
import time
from datetime import datetime as datetime

from packaging import version

from triggerConfig import CORE as coreCF

if not isinstance(targetCF.targetDirectory, str):
    targetCF.targetDirectory = "active"
from triggerConfig import TARGET as targetCF

if not isinstance(targetCF.archiveDirectory, str):
    targetCF.archiveDirectory = "archive"

PID = os.getpid()
print(f"*** Starting ***\nPID: {PID}")
scriptName = (os.path.basename(__file__)).removesuffix(".py")
log = logging.getLogger(scriptName)
log.setLevel(logging.DEBUG)
logging.addLevelName(logging.DEBUG, "DBUG")

handleConsole = logging.StreamHandler(sys.stdout)
handleConsole.setFormatter(
    logging.Formatter("%(asctime)s |:| %(funcName)s | %(message)s", "%H:%M:%S")
)
handleConsole.setLevel(logging.DEBUG)
log.addHandler(handleConsole)

if version.parse(platform.python_version()) < version.parse("3.10.0"):
    log.critical("Python 3.10.0 or greater is required!")
    exit()

curDir = os.path.dirname(os.path.realpath(__file__))
tarDir = os.path.join(curDir, targetCF.targetDirectory)

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
handleFile.setLevel(coreCF.logLevel.upper())
log.addHandler(handleFile)

log.critical(
    f"""Starting...
	PID: {PID}
	Platform: {platform.system()} | {platform.node()}
	Python: {platform.python_version()}
	Current Directory: {curDir}
	Current Working: {os.getcwd()}
	Target Directory: {tarDir}"""
)


def run_comm(name: str, comm: list, nullOut: bool = False):
    log.debug(f"{name} | {comm}")
    try:
        if nullOut:
            commReturn = subprocess.run(comm, stdout=subprocess.DEVNULL, check=True)
            log.debug(commReturn.returncode)
            return True
        else:
            commReturn = subprocess.run(comm, check=True)
            log.debug(commReturn.returncode)
            return True
    except subprocess.CalledProcessError:
        log.exception(f"subprocess.run ERR | {name}")
        return False


def check_exist(
    item: str, isFile: bool, path: list | str = [], make: bool = False
) -> bool:
    """Checks if a file/folder exists. Create if make is true"""
    log.debug(f"run| item: {item}| isFile: {isFile}| path: {path}| make: {make}")
    if item is None:
        log.error("Item Is Empty!")
    if isinstance(path, str):
        path = [path]
    itemPath = os.path.join(curDir, *path, item)
    if isFile:
        typ = "File"
    else:
        typ = "Folder"
    if os.path.exists(itemPath):
        log.debug(f"exists: {itemPath}")
        return True
    elif make:
        try:
            if isFile:
                with open(itemPath, "w"):
                    pass
            else:
                os.mkdir(itemPath)
            return True
        except Exception:
            log.exception(f"{typ} Creation Failed!")
            return False
    else:
        log.error(f"{typ} Missing: {itemPath}")
        return False


def basicChecks():
    """Checks to ensure required core/target files are present"""
    ok = True
    log.info("Checking For Core Requirements File")
    check_exist(coreCF.requiredModules, isFile=True, make=True)
    log.info("Checking For Target Directory")
    check_exist(item=tarDir, isFile=False, make=True)
    log.info("Checking For Archive Directory")
    check_exist(item=targetCF.archiveDirectory, isFile=False, make=True)
    log.info("Checking For Target Script")
    if not check_exist(item=targetCF.scriptName, isFile=True, path=tarDir, make=True):
        log.critical("Target Script Missing!")
        ok = False
    if targetCF.requiredModules:
        log.info("Checking For Target Requirements File")
        if not check_exist(item=targetCF.requiredModules, isFile=True, path=tarDir):
            log.error("Target Requirements File Missing")
    if len(targetCF.requiredFiles) > 0:
        for element in targetCF.requiredFiles:
            if check_exist(item=element, isFile=True, path=tarDir, make=True):
                log.info(f"Target Required File {element} Found")
            else:
                ok = False
    if len(targetCF.optionalFiles) > 0:
        for element in targetCF.optionalFiles:
            if check_exist(item=element, isFile=True, path=tarDir):
                log.info(f"Target Optional File {element} Found")
    if len(targetCF.requiredFolders) > 0:
        for element in targetCF.requiredFolders:
            if check_exist(item=element, isFile=False, path=tarDir, make=True):
                log.info(f"Target Required Folder {element} Found")
            else:
                ok = False
    if len(targetCF.optionalFiles) > 0:
        for element in targetCF.optionalFolders:
            if check_exist(item=element, isFile=False, path=tarDir):
                log.info(f"Target Optional Folder {element} Found")
    log.info("Ensuring pip")
    if not run_comm(name="Ensure pip", comm=["python", "-m", "ensurepip", "--upgrade"]):
        ok = False
    return ok


log.info("Checking For Required Files/Folders...")
if basicChecks():
    log.info("Basic Checks Successful")
else:
    log.error("Basic Checks Failed!")
    exit()

import netifaces

sysFolded = (platform.system()).casefold()


def networkChecks(core: bool):
    log.debug("run")
    if sysFolded == "windows":
        pingType = "-n"
    else:
        pingType = "-c"

    def ping(host):
        if host is None:
            host = netifaces.gateways()["default"][netifaces.AF_INET][0]
        if host:
            return run_comm(name="ping", comm=["ping", pingType, "1", host])

    retryMax = coreCF.retry + 1
    retryCount = 0
    while True and core is True:
        log.info("Pinging Gateway")
        if ping(host=coreCF.gateway):
            log.info("Gateway Ping Successful")
            break
        else:
            retryCount += 1
            if retryCount == retryMax:
                time.sleep((coreCF.paceErr * 20))
            time.sleep(coreCF.paceErr)

    retryCount = 0
    while True:
        if core is True:
            netChecks = coreCF.network
        else:
            netChecks = targetCF.network
        bad = 0
        for itemName, itemVal in netChecks.items():
            log.info(f"Pinging {itemName}")
            st = time.perf_counter()
            if ping(itemVal):
                en = time.perf_counter()
                log.info(f"{itemName} Ping Successful {round((st - en) * 1000)}ms")
                time.sleep((coreCF.paceNorm / 1000))
            else:
                log.error(f"Unsuccessful Pinging {itemName}")
                bad += 1

        if bad > 0:
            retryCount += 1
            if retryCount == retryMax:
                log.error("Reached Maximum Retries!")
                exit()
            time.sleep(coreCF.paceErr)
        else:
            break


log.info("Checking Network...")
if networkChecks(core=True):
    log.info("Core Network Checks Completed")
else:
    log.error("Core Network Checks Failed!")


def moduleChecks():
    """Ensures any required python modules are installed."""
    coreReqs = [
        "python",
        "-m",
        "pip",
        "install",
        "-r",
        f"{os.path.join(curDir, coreCF.requiredModules)}",
    ]
    if not run_comm(name="Python pip Core", comm=coreReqs):
        return False
    log.info("Core Modules Installed")
    log.debug(f"tarReqMod: {targetCF.requiredModules}")
    if targetCF.requiredModules is not False:
        targetReqs = [
            "python",
            "-m",
            "pip",
            "install",
            "-r",
            f"{os.path.join(curDir, targetCF.requiredModules)}",
        ]
        if not run_comm(name="Python pip Target", comm=targetReqs):
            return False
        log.info("Target Modules Installed")
    else:
        return True


log.info("Checking Module Requirements...")
if coreCF.checkRequiredPackages:
    if moduleChecks():
        log.info("Module Check Successful")
    else:
        log.error("Module Checks Failed!")
        exit()


def deleteThing(item: str):
    """Given a path will try to delete it as file, then empty folder, then non-empty folder"""
    if not os.path.exists(item):
        return False
    try:
        os.remove(item)
        log.debug(f"deleteFile {item=}")
        return True
    except IsADirectoryError:
        try:
            os.rmdir(item)
            log.debug(f"deleteEmptyFolder {item=}")
            return True
        except OSError:
            try:
                shutil.rmtree(item)
                log.debug(f"deleteNonEmptyFolder {item=}")
                return True
            except Exception:
                log.exception(f"deleteNonEmptyFodler {item=}")
                return False
        except Exception:
            log.exception(f"deleteEmptyFolder {item=}")
            return False
    except Exception:
        log.exception(f"deleteFile {item=}")
        return False


def moveThing(
    name: str,
    source: str,
    destination: str,
    copy: bool = False,
    overwrite: bool = False,
):
    if os.path.exists(source):
        log.debug(f"Thing Exists SRC: {source}")
    if os.path.exists(destination):
        log.warning(f"Thing Exists DST: {destination}")
        if overwrite:
            deleteThing(item=destination)
        else:
            if "-" in destination[-3:]:
                var = int(destination[-2:].removeprefix("-"))
                var = var + 1
                destination = destination + f" -{var}"
    try:
        if copy:
            shutil.copy(src=source, dst=destination)
            return True
        else:
            shutil.move(src=source, dst=destination)
            return True
        time.sleep(coreCF.paceNorm / 100)
    except Exception:
        log.exception(name)
        return False


def getVersionJSON(target: bool, filename: str = "changelog.json") -> str | bool:
    """Gets last key from the changelog.json in either gitDown or target directory"""
    if target:
        fold = "gitDown"
    else:
        fold = targetCF.targetDirectory
    file = os.path.join(curDir, fold, filename)
    if not check_exist(item=filename, isFile=True, path=[fold]):
        return False
    try:
        with open(file, "r") as text:
            chanJSON = json.load(text)
            return str(list(chanJSON.keys())[-1])
    except Exception:
        log.exception("Changelog JSON File Open")
        return False


def compareVersion():
    log.info("Compare Version Numbers")
    tarVer = getVersionJSON(target=True)
    gitVer = getVersionJSON(target=False)
    if tarVer or gitVer is False:
        return False
    else:
        return version.parse(tarVer) < version.parse(gitVer)


curDT = datetime.today().strftime("%Y-%m-%d_%H:%M")
targetBak = f"{targetCF.repository.split('/')[-1]} {coreCF.folderSeperator} {curDT}"
arcDir = os.path.join(curDir, targetCF.archiveDirectory, targetBak)


def copyRequired(item: str, isFile: bool):
    """Copies required files/folders from target"""
    itemPath = os.path.join(curDir, item)


def gitClone() -> bool:
    """Downloads default branch of repo. Moves what's in active to archive."""
    log.debug("run")
    from git import Repo

    gitURL = f"http://github.com/{targetCF.repository}.git"
    gitFold = os.path.join(curDir, "gitDown")
    os.mkdir(gitFold)
    try:
        Repo.clone_from(gitURL, gitFold)
    except Exception:
        log.exception("Github Clone")
    log.info("Repository Clone Successful")

    if targetCF.checkVersion:
        if not compareVersion():
            log.info("Git Version <= Target Version")
            return False
    log.info("Moving active to archive")
    moveThing(name="Move active to archive", source=tarDir, destination=arcDir)
    log.info("Moving gitclone to active")
    # os.rmdir(tarDir)
    moveThing(name="Move gitclone to active", source=gitFold, destination=tarDir)
    return True


if coreCF.gitHub:
    log.info("Downloading From Github...")
    if gitClone():
        log.info("Complete")
    else:
        log.error("Github Clone Failed!")
    log.info("Copying Required Files...")
    if copyRequired():
        log.info("Copy Successful")
    else:
        log.error("Copying Failed!")
    log.info("Copying Required Folders...")
    if copyRequired():
        log.info("Copy Successful")
    else:
        log.error("Copying Failed!")
else:
    log.info("Github Not Enabled... Skipping")


# MIT APasz
