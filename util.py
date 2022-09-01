import os
import logging
import sys
import shutil

log = logging.getLogger("TSlog")


def check_exist(itemPath: str, isFile: bool) -> bool:
    """Checks if a file/folder exists"""
    log.debug(f"{isFile=} | {itemPath=}")
    if os.path.exists(itemPath):
        log.info(f"{isFile=} Exists: {itemPath=}")
        return True
    else:
        log.warning(f"{isFile=} Missing: {itemPath=}")
        return False


def remove_thing(itemPath: str, isFile: bool) -> bool:
    """Removes a file/folder"""
    log.debug(f"run| {isFile=}| {itemPath=}")
    if not check_exist(itemPath=itemPath, isFile=isFile):
        return False
    if isFile:
        try:
            os.remove(itemPath)
            log.debug(f"DeleteFile {itemPath=}")
            return True
        except Exception:
            log.exception("DeleteFile")
            return False
    else:
        try:
            os.rmdir(itemPath)
            log.debug(f"DeleteEmptyFolder {itemPath=}")
            return True
        except OSError:
            try:
                shutil.rmtree(itemPath)
                log.debug(f"DeleteNonEmptyFolder {itemPath=}")
                return True
            except Exception:
                log.exception(f"DeleteNonEmptyFodler")
                return False
        except Exception:
            log.exception("DeleteEmptyFolder")
            return False


def same_name(item: str, isFile: bool) -> str:
    """Return file/folder name but appeneded with -#"""
    log.debug(f"run| {isFile=}| {item=}")
    ext = None
    if isFile:
        item, ext = item.rsplit(".", maxsplit=1)
        ext = "." + ext
    log.debug(f"{item=}| {ext=}")
    if "-" in item[-4:]:
        item, var = item.split(" -")
        var = str(int(var) + 1)
        itemEdit = item + " -" + var
    else:
        itemEdit = item + " -1"
    if isFile and (ext is not None):
        itemEdit = itemEdit + ext
    log.debug(f"{itemEdit=}")
    return itemEdit


def make_thing(itemPath: str, isFile: bool, overwrite: bool = False) -> bool:
    """Makes an empty file/folder"""
    log.debug(f"run| {isFile=}| {overwrite=}| {itemPath=}")
    if os.path.exists(itemPath):
        if overwrite:
            os.remove(itemPath)
            log.debug(f"{overwrite=}| {itemPath=}")
        else:
            log.debug("MakeThing")
            path, item = itemPath.rsplit(os.sep, maxsplit=1)
            item = same_name(item=item, isFile=isFile)
            itemPath = os.path.join(path, item)
    if isFile:
        try:
            with open(itemPath, "w"):
                pass
            log.debug("Make File")
            return True
        except Exception:
            log.exception("Make File")
            return False
    else:
        try:
            os.mkdir(itemPath)
            log.debug("Make Directory")
            return True
        except Exception:
            log.exception("Make Directory")
            return False


def copymove_thing(
    source: str, destination: str, isFile: bool, copy: bool, overwrite: bool = False
) -> bool:
    """Copyies or moves thing from one place to another"""
    log.debug(f"run| {isFile=}| {overwrite=}| {source=}| {destination=}")
    if not check_exist(itemPath=source, isFile=isFile):
        log.error("SRC doesn't exist, nothing to copy")
    if os.path.exists(destination):
        log.warning(f"DST already exists, {overwrite=}")
        if overwrite:
            log.debug("Overwrite")
            remove_thing(itemPath=destination, isFile=isFile)
        else:
            log.debug("CopyMove")
            path, item = destination.rsplit(os.sep, maxsplit=1)
            item = same_name(item=item, isFile=isFile)
            destination = os.path.join(path, item)
    if copy:
        if isFile:
            try:
                shutil.copy(src=source, dst=destination)
                log.info(f"File Copied| {source=}\n{destination=}")
                return True
            except Exception:
                log.exception("Copy File")
                return False
        else:
            try:
                shutil.copytree(src=source, dst=destination)
                log.debug(f"Folder Copied| {source=}\n{destination=}")
                return True
            except Exception:
                log.exception(f"Copy Folder")
                return False
    else:
        try:
            shutil.move(src=source, dst=destination)
            log.debug(f"{isFile=} Moved| {source=}\n{destination=}")
            return True
        except Exception:
            log.exception("Move File/Folder")
            return False
