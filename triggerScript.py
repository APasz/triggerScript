#!/usr/bin/env python3
import json
import logging
import os
import platform
import subprocess
import sys
import time
from datetime import datetime as datetime


import util

pajoin = os.path.join

PID = os.getpid()
print(f"*** Starting ***\nPID: {PID}")


logINIT = 5
scriptName = (os.path.basename(__file__)).removesuffix(".py")
log = logging.getLogger("TSlog")
logging.addLevelName(logging.DEBUG, "DBUG")

handleConsole = logging.StreamHandler(sys.stdout)
handleConsole.setFormatter(
    logging.Formatter("%(asctime)s |:| %(funcName)s | %(message)s", "%H:%M:%S")
)
handleConsole.setLevel(logINIT)
log.addHandler(handleConsole)


curDir = os.path.dirname(os.path.realpath(__file__))

handleFile = logging.FileHandler(
    filename=pajoin(curDir, "TSlog.log"),
    encoding="utf-8",
    mode="a",
)
handleFile.setFormatter(
    logging.Formatter(
        "%(asctime).19s %(created).2f | %(levelname).4s |:| %(funcName)s | %(message)s",
    )
)
handleFile.setLevel(logINIT)
log.addHandler(handleFile)

try:
    log.info("TRY MODULE IMPORT")
    from packaging import version
    import netifaces

    from triggerConfig import CORE as coreCF
    from triggerConfig import TARGET as targetCF
except Exception:
    log.exception("IMPORT FAILED")


if version.parse(platform.python_version()) <= version.parse("3.10.0"):
    log.fatal("Python 3.10.0 or greater is required!")
    exit()


tarDir = pajoin(curDir, targetCF.targetDirectory)
log.setLevel("DEBUG")
log.critical(
    f"""Starting...
    PID: {PID}
    Platform: {platform.system()} | {platform.node()}
    Python: {platform.python_version()}
    Current Directory: {curDir}
    Current Working: {os.getcwd()}
    Target Directory: {tarDir}"""
)


def run_comm(name: str, comm: list, wd: str | None = None, nullOut: bool = False):
    log.debug(f"{name} | {comm}")
    try:
        if nullOut:
            commReturn = subprocess.run(
                comm, cwd=wd, stdout=subprocess.DEVNULL, check=True
            )
            log.debug(commReturn.returncode)
            return True
        else:
            commReturn = subprocess.run(comm, cwd=wd, check=True)
            log.debug(commReturn.returncode)
            return True
    except subprocess.CalledProcessError:
        log.exception(f"subprocess.run ERR | {name}")
        return False


def basicChecks():
    """Checks to ensure required core/target files are present"""
    ok = True
    log.info("Checking For Core Requirements File")
    if util.check_exist(itemPath=pajoin(curDir, coreCF.requiredModules), isFile=True):
        log.info(f"Core {coreCF.requiredModules}: Found")
    else:
        log.error(f"Core {coreCF.requiredModules=}: Missing!")
        ok = False

    log.info("Checking For Target Directory")
    if util.check_exist(itemPath=tarDir, isFile=False):
        log.info(f"Target Directory {targetCF.targetDirectory}: Found")
    else:
        log.error(f"Target Directory {targetCF.targetDirectory=}: Missing!")
        if util.make_thing(itemPath=tarDir, isFile=False):
            log.info(f"Target Directory {targetCF.targetDirectory}: Made")

    log.info("Checking For Archive Directory")
    if util.check_exist(
        itemPath=pajoin(curDir, targetCF.archiveDirectory), isFile=False
    ):
        log.info(f"Archive Directory {targetCF.archiveDirectory}: Found")
    else:
        log.error(f"Archive Directory {targetCF.archiveDirectory=}: Missing!")
        if util.make_thing(
            itemPath=pajoin(curDir, targetCF.archiveDirectory), isFile=False
        ):
            log.info(f"Target Directory {targetCF.targetDirectory}: Made")

    log.info("Checking For Target Script")
    if util.check_exist(itemPath=pajoin(tarDir, targetCF.scriptName), isFile=True):
        log.info(f"Target Script {targetCF.scriptName}: Found")
    else:
        log.critical(f"Target Script {targetCF.scriptName=}: Missing!")
        ok = False

    if targetCF.requiredModules:
        log.info("Checking For Target Requirements File")
        if util.check_exist(
            itemPath=pajoin(tarDir, targetCF.requiredModules), isFile=True
        ):
            log.info(f"Target {targetCF.requiredFiles}: Found")
        else:
            log.error(f"Target {targetCF.requiredFiles=}: Missing!")
            ok = False

    if len(targetCF.requiredFiles) > 0:
        for element in targetCF.requiredFiles:
            if util.check_exist(itemPath=pajoin(tarDir, element), isFile=True):
                log.info(f"Target Required File {element}: Found")
            else:
                log.error(f"Target Required File {element}: Missing!")
                ok = False

    if len(targetCF.requiredFolders) > 0:
        for element in targetCF.requiredFolders:
            if util.check_exist(itemPath=pajoin(tarDir, element), isFile=False):
                log.info(f"Target Required Folder {element}: Found")
            else:
                log.error(f"Target Required Folder {element}: Missing!")
                if util.make_thing(itemPath=pajoin(tarDir, element), isFile=False):
                    log.info(f"Target Required Folder {element}: Made")

    log.info("Ensuring PiP")
    if run_comm(name="Ensure pip", comm=["python", "-m", "ensurepip", "--upgrade"]):
        log.info("PiP Ensured")
    else:
        log.error("Unable To Ensure PiP")
        ok = False
    return ok


log.info("Performing Basic Checks...")
if basicChecks():
    log.info("Basic Checks Successful")
else:
    log.fatal("Basic Checks Failed!")
    exit()


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
                log.info(
                    f"{itemName} Ping Successful {round((st - en) * 1000)}ms")
                time.sleep((coreCF.paceNorm / 1000))
            else:
                log.error(f"Unsuccessful Pinging {itemName}")
                bad += 1

        if bad > 0:
            retryCount += 1
            if retryCount == retryMax:
                log.fatal("Reached Maximum Retries!")
                return False
            time.sleep(coreCF.paceErr)
        else:
            break
    return True


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
        f"{pajoin(curDir, coreCF.requiredModules)}",
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
            f"{pajoin(curDir, targetCF.requiredModules)}",
        ]
        if not run_comm(name="Python pip Target", comm=targetReqs):
            return False
        log.info("Target Modules Installed")
    else:
        return True
    return True


log.info("Checking Module Requirements...")
if coreCF.checkRequiredPackages:
    if moduleChecks():
        log.info("Module Check Successful")
    else:
        log.fatal("Module Checks Failed!")
        exit()


def getVersionJSON(target: bool, filename: str = "changelog.json") -> str | bool:
    """Gets last key from the changelog.json in either gitDown or target directory"""
    if target:
        fold = "gitDown"
    else:
        fold = targetCF.targetDirectory
    file = pajoin(curDir, fold, filename)
    if not util.check_exist(itemPath=pajoin(fold, filename), isFile=True):
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
arcDir = pajoin(curDir, targetCF.archiveDirectory, targetBak)


def copyRequired(item: str, isFile: bool):
    """Copies required files/folders from target"""
    log.debug(f"copyRequired| {item=}")
    src = pajoin(arcDir, item)
    dst = pajoin(tarDir, item)
    if util.copymove_thing(
        source=src, destination=dst, isFile=isFile, copy=True, overwrite=True
    ):
        log.debug("Required Item Copied")
        return True
    else:
        log.error(f"Unable To Copy Required Item {isFile=}| {item=}")
        return False


def gitClone() -> bool:
    """Downloads default branch of repo. Moves what's in active to archive."""
    log.debug("run")
    from git import Repo

    gitURL = f"http://github.com/{targetCF.repository}.git"
    gitFold = pajoin(curDir, "gitDown")
    if os.path.exists(gitFold):
        util.remove_thing(itemPath=gitFold, isFile=False)
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
    if util.copymove_thing(source=tarDir, destination=arcDir, isFile=False, copy=False):
        log.info(f"Moved! {tarDir=}\n{arcDir=}")
    else:
        log.error(f"Unable To Move! {tarDir=}\n{arcDir=}")
        return False
    log.info("Moving gitclone to active")
    if util.copymove_thing(
        source=gitFold, destination=tarDir, isFile=False, copy=False
    ):
        log.info(f"Moved! {gitFold=}\n{tarDir=}")
    else:
        log.error(f"Unable To Move! {gitFold=}\n{tarDir=}")
        return False
    return True


if coreCF.gitHub:
    log.info("Downloading From Github...")
    if gitClone():
        log.info("Complete")
    else:
        log.error("Github Clone Failed!")
    log.info("Copying Required Files...")
    for item in targetCF.requiredFiles:
        copyRequired(item=item, isFile=True)
    log.info("Copy Successful")
    log.info("Copying Required Folders...")
    for item in targetCF.requiredFolders:
        copyRequired(item=item, isFile=False)
    log.info("Copy Successful")
else:
    log.info("Github Not Enabled... Skipping")

if targetCF.network is not None:
    log.info("Performing Target Network Checks")
    if networkChecks(core=False):
        log.info("Target Network Checks Successful")
    else:
        log.error("Target Networks Unreachable!")


def triggerTarget():
    """Run the target script"""
    log.info("Trigging Target Script")
    while True:
        botCOMM = ["python", targetCF.scriptName]
        try:
            run_comm(name="TriggerTarget", comm=botCOMM, wd=tarDir)
        except Exception as xcp:
            log.exception("TryTriggerTarget")
            time.sleep(coreCF.paceErr)
            if str(targetCF.restartCode) not in xcp.returncode:
                break
    return int(xcp.returncode)


log.info("Ready To Trigger Script...")
if coreCF.launchTarget:
    returncode = triggerTarget()
    log.critical(f"Target Script Exited! {returncode=}")


# MIT APasz
