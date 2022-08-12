from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class core:
    """Config relating to this script"""

    # Name of requirements file for self
    requiredModules = "requirements.txt"
    # debug | info
    logLevel = "info"
    # Enable fetching from GitHub. If False, archiving is disabled. Will only start the target script.
    gitHub = True
    # Number of times to retry doing anything before quiting
    retry = 3
    # Whether to skip checking if the required packages are installed
    checkRequiredPackages = True
    # Whether to actually start the target script
    launchTarget = True
    # When target script version is archived, this separator + timestamp will be appended
    folderSeperator = ";"
    # Time in milliseconds give to ensure certain actions actually happen before the script proceeds
    paceNorm = 50
    # Time in seconds to give when an error occurs with certain actions before the script tries again
    paceErr = 2.5
    # Address for the LAN gateway
    gateway = None
    # Addresses to ping to ensure those services can be reached, if enabled
    network = {"PyPi": "www.pypi.org"}
    # "Github": "www.github.com",


@dataclass(slots=True, frozen=True)
class target:
    """Config relating to the script to be triggered"""

    # Name of target script
    scriptName = "bot.py"
    # Name of requirements file for target (if not needed, arg = False)
    requiredModules = False
    # Names of the required files for target
    requiredFiles = []
    # Names of the optional files for target
    optionalFiles = []
    # Names of the required folders for target
    requiredFolders = []
    # Names of the optional folders for target
    optionalFolders = []
    # Username/repo (SSCBot | Strider)
    repository = "APasz/Strider"
    # Folder that the target script itself is in. The one that'll be run
    targetDirectory = "active"
    # Folder that old versions will be stored
    archiveDirectory = "archive"
    # Addresses to ping to ensure the target script can start
    network = {"Discord": "www.discord.com"}
    # Check version before replace (only compatible with scripts that have a changelog.json in root where the keys is the version)
    checkVersion = True


# MIT APasz
