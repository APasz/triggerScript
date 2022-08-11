#!/usr/bin/env python3
from ast import literal_eval
from distutils.command.config import config
import os
import sys
import platform
from packaging import version
import logging
import time


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

from triggerConfig import core as coreCF
from triggerConfig import target as targetCF

global curDir
curDir = os.path.dirname(os.path.realpath(__file__))
if targetCF.targetDirectory is not None:
    global tarDir
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
handleFile.setLevel((coreCF.logLevel).upper())
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

import subprocess


def runCOMM(name: str, comm: list, nullOut: bool = False):
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
    except subprocess.CalledProcessError as xcp:
        log.exception(f"subprocess.run ERR | {name}")
        return False


def _checkExist(item: str, isFile: bool, path: list = [], make: bool = False):
    """Checks if a file/folder exists. Create if make is true"""
    log.debug(f"run| item: {item}| isFile: {isFile}| path: {path}| make: {make}")
    if item is None:
        log.error("Item Is Empty!")
    if isinstance(path, str):
        path = [path]
    itemPath = os.path.join(curDir, *path, item)
    typ = "File/Folder"
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

                with open(itemPath, "w") as file:
                    pass
            else:

                os.mkdir(itemPath)
        except Exception as xcp:
            log.exception(f"{typ} Creation Failed!")
            return False
    else:
        log.error(f"{typ} Missing: {itemPath}")


def basicChecks():
    """Checks to ensure required core/target files are present"""
    ok = True
    log.info("Checking For Core Requirements File")
    _checkExist(coreCF.requiredModules, isFile=True, make=True)
    log.info("Checking For Target Directory")
    _checkExist(item=tarDir, isFile=False, make=True)
    log.info("Checking For Archive Directory")
    _checkExist(item=targetCF.archiveDirectory, isFile=False, make=True)
    log.info("Checking For Target Script")
    if not _checkExist(item=targetCF.scriptName, isFile=True, path=tarDir):
        log.critical("Target Script Missing!")
        ok = False
    if targetCF.requiredModules:
        log.info("Checking For Target Requirements File")
        if not _checkExist(item=targetCF.requiredModules, isFile=True, path=tarDir):
            log.error("Target Requirements File Missing")
    if len(targetCF.requiredFiles) > 0:
        for element in targetCF.requiredFiles:
            if _checkExist(item=element, isFile=True, path=tarDir, make=True):
                log.info(f"Target Required File {element} Found")
            else:
                ok = False
    if len(targetCF.optionalFiles) > 0:
        for element in targetCF.optionalFiles:
            if _checkExist(item=element, isFile=True, path=tarDir):
                log.info(f"Target Optional File {element} Found")
    if len(targetCF.requiredFolders) > 0:
        for element in targetCF.requiredFolders:
            if _checkExist(item=element, isFile=False, path=tarDir, make=True):
                log.info(f"Target Required Folder {element} Found")
            else:
                ok = False
    if len(targetCF.optionalFiles) > 0:
        for element in targetCF.optionalFolders:
            if _checkExist(item=element, isFile=False, path=tarDir):
                log.info(f"Target Optional Folder {element} Found")
    log.info("Ensuring pip")
    if not runCOMM(name="Ensure pip", comm=["python", "-m", "ensurepip", "--upgrade"]):
        ok = False
    return ok


log.info("Checking For Required Files/Folders...")
if basicChecks():
    log.info("Basic Checks Successful")
else:
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
            return runCOMM(name="ping", comm=["ping", pingType, "1", host])

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
            せ = time.perf_counter()
            if ping(itemVal):
                え = time.perf_counter()
                log.info(f"{itemName} Ping Successful {round((え - せ) * 1000)}ms")
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


def moduleChecks():
    """Ensures any required python modules are installed."""
    coreReqs = os.path.join(curDir, coreCF.requiredModules)
    pipComm = ["python", "-m", "pip", "-r"]
    if not runCOMM(name="Python pip Core", comm=(pipComm.append(coreReqs))):
        return False
    log.info("Core Modules Installed")
    if targetCF.requiredFiles is not False:
        targetReqs = os.path.join(curDir, targetCF.requiredModules)
        if not runCOMM(name="Python pip Target", comm=(pipComm.append(targetReqs))):
            return False
        log.info("Target Modules Installed")


log.info("Checking Module Requirements...")
if coreCF.checkRequiredPackages:
    if moduleChecks():
        log.info("Module Check Successful")
    else:
        exit()

# MIT APasz
