from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class triggerConfig:
    """Class for triggerScript configuration"""

    # Name of target script
    targetScript = "bot.py"
    # SSCBot | Strider
    repo = "Strider"
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
    # Folder that the target script itself is in. The one that'll be run
    targetDirectory = "active"
    # Folder that old versions will be stored
    targetArchive = "archive"
    # When target script version is archived, this separator + timestamp will be appended
    folderSeperator = ";"
    # Time give to ensure certain actions actually happen before the script proceeds
    # milliseconds
    paceNorm = 50
    # Time to give when an error occurs with certain actions before the script tries again
    # seconds
    paceErr = 2.5
    # Addresses to ping to ensure the target script can function
    netChecks = {
        "Gateway": None,
        "Github": "www.github.com",
        "Discord": "www.discord.com",
    }
