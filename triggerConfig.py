from dataclasses import dataclass


@dataclass(slots=True)
class TARGET:
    """Config relating to the script to be triggered"""

    # Name of target script
    # Default = "bot.py"
    scriptName = "bot.py"
    # Name of requirements file for target (if not needed, arg = False)
    # Default = "requirements.txt"
    requiredModules = "requirements.txt"
    # Names of the required files for target. If Github is enabled, will copy these over when updating
    # Default = ["config.py", "config.json"]
    requiredFiles = ["config.py", "config.json"]
    # Names of the required folders for target. If Github is enabled, will copy these over when updating
    # Default = ["secrets"]
    requiredFolders = ["secrets"]
    # Github username/repo
    # (SSCBot | Strider)
    # Default = "APasz/Strider"
    repository = "APasz/Strider"
    # Folder that the target script itself is in. The one that'll be run.
    # Default = "active"
    targetDirectory = "active"
    # Folder that old versions will be stored
    # Default = "archive"
    archiveDirectory = "archive"
    # Addresses to ping to ensure the target script can start
    # Default = {"Discord": "www.discord.com"}
    network = {"Discord": "www.discord.com"}
    # Check version before replace
    # (only compatible with scripts that have a changelog.json in root where the keys are the version,
    # like in the changelog.json bundled with this script)
    # Default = True
    checkVersion = True
    # Code script will output when restart is intended
    # Default = 94
    restartCode = 94


@dataclass(slots=True)
class CORE:
    """Config relating to this script"""

    # Name of requirements file for self
    # Default = "requirements.txt"
    requiredModules = "requirements.txt"
    # "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL", "FATAL"
    # Case insensitive
    # Default = "INFO"
    logLevel = "DEBUG"
    # Enable fetching from GitHub. If False, archiving is disabled. Will only start the target script.
    # Default = True
    gitHub = True
    # Number of times to retry doing anything before quiting
    # Default = 3
    retry = 3
    # Whether to check if the required packages are installed
    # Default = True
    checkRequiredPackages = True
    # Whether to actually start the target script
    # Default = True
    launchTarget = True
    # When target script version is archived, this separator + timestamp will be appended
    # Default = ";"
    folderSeperator = ";"
    # Time in milliseconds give to ensure certain actions actually happen before the script proceeds
    # Default = 75
    paceNorm = 75
    # Time in seconds to give when an error occurs with certain actions before the script tries again
    # Default = 3
    paceErr = 3
    # Address for the LAN gateway
    # Default = None
    gateway = None
    # Addresses to ping to ensure those services can be reached, if enabled
    # Default = {"Github": "www.github.com", "PyPi": "www.pypi.org"}
    network = {"PyPi": "www.pypi.org"}


# MIT APasz
