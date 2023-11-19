# type: ignore

import argparse
import os
import platform
import shutil
import subprocess
import sys
from io import UnsupportedOperation
from pathlib import Path

autostart_entry = [
    "[Desktop Entry]",
    "Type=Application",
    "Exec=esbgm",
    "X-GNOME-Autostart-enabled=true",
    "NoDisplay=false",
    "Hidden=false",
    "Name[en_US]=ESBGM",
    "Comment[en_US]=Run background music when emulationstation is up",
    "X-GNOME-Autostart-Delay=0",
]


def is_decorated():
    if platform.system().lower() == "windows":
        return os.getenv("ANSICON") is not None or os.getenv("ConEmuANSI") == "ON" or os.getenv("Term") == "xterm"

    if not hasattr(sys.stdout, "fileno"):
        return False

    try:
        return os.isatty(sys.stdout.fileno())
    except UnsupportedOperation:
        return False


DEFAULT_MUSIC_FOLDER = Path(os.path.expanduser("~/RetroPie/roms/musics"))
AUTOSTART_RETROPIE_PATH = Path("/opt/retropie/configs/all/autostart.sh")


def install_from_pip(prerelease: bool):
    """
    Installs es-bgm from pip
    """
    if not prerelease:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-U", "es-bgm"])
    else:
        print("Installing prerelease version")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-U", "es-bgm", "--pre"])


def uninstall_from_pip():
    """
    Uninstalls es-bgm from pip
    """
    subprocess.check_call([sys.executable, "-m", "pip", "uninstall", "es-bgm"])


lines_to_add_to_autostart = [
    # on startup, remove any musicpaused flag if present
    "rm -f ~/.musicpaused.flag",
    "/home/pi/.local/bin/esbgm > /dev/null 2>&1 &",
]


def add_autostart_script():
    """
    Places the autostart script to the appropriate folder
    """
    print("Adding the autostart script...", end="")
    if AUTOSTART_RETROPIE_PATH.exists():
        # Prepend the running of esbgm to the autostart script
        # We are in a retropie. Update the file if possible
        with AUTOSTART_RETROPIE_PATH.open("r+") as fs:
            line_found = any("esbgm" in line for line in fs)
            fs.seek(0)
            if not line_found:
                s = fs.read()
                fs.seek(0)
                for linetowrite in lines_to_add_to_autostart:
                    fs.write(f"{linetowrite}\n")
                fs.write(s)

    else:
        autostart_folder = Path(os.path.expanduser("~/.config/autostart"))
        if not autostart_folder.exists():
            autostart_folder.mkdir(parents=True, exist_ok=True)

        desktop_entry = Path(autostart_folder, "ESBGM.desktop")
        if not desktop_entry.exists():
            with desktop_entry.open("w") as fs:
                for entry in autostart_entry:
                    fs.write(entry + "\n")

    print("OK")


def remove_autostart_script():
    """
    Removes the autostart script
    """
    print("Removing the autostart entry...", end="")
    if AUTOSTART_RETROPIE_PATH.exists():
        with AUTOSTART_RETROPIE_PATH.open("r") as fs:
            lines = fs.readlines()
        with AUTOSTART_RETROPIE_PATH.open("w") as fs:
            for line in lines:
                if "esbgm" not in line and "musicpaused" not in line:
                    fs.write(line)
    else:
        desktop_entry = Path(os.path.expanduser("~/.config/autostart/esbgm.desktop"))
        desktop_entry.unlink(missing_ok=True)
    print("OK")


def create_default_music_folder():
    """
    Adds the default music folder
    """
    print("Creating the default music folder...", end="")
    DEFAULT_MUSIC_FOLDER.mkdir(parents=True, exist_ok=True)

    music_folder_file = Path(DEFAULT_MUSIC_FOLDER, "PLACE_YOUR_MUSIC_HERE")
    if not music_folder_file.exists():
        music_folder_file.write_text("Place your music files in this directory (.ogg and .mp3 supported)")

    print("OK")


DEFAULT_MENU_OPTIONS_FOLDER = Path(os.path.expanduser("~/RetroPie/retropiemenu/"))
DISABLE_BACKGROUND_MUSIC = Path(DEFAULT_MENU_OPTIONS_FOLDER, "Disable background music.sh")
ENABLE_BACKGROUND_MUSIC = Path(DEFAULT_MENU_OPTIONS_FOLDER, "Enable background music.sh")


def add_menu_options():
    if DEFAULT_MENU_OPTIONS_FOLDER.exists():
        with DISABLE_BACKGROUND_MUSIC.open("w") as fs:
            fs.write("#/bin/bash\n")
            fs.write("mkdir -p ~/.config/esbgm\n")
            fs.write("touch ~/.config/esbgm/disable.flag\n")

        with ENABLE_BACKGROUND_MUSIC.open("w") as fs:
            fs.write("#/bin/bash\n")
            fs.write("rm -f ~/.config/esbgm/disable.flag\n")


RUNCOMMAND_HOOKS_DIR = Path("/opt/retropie/configs/all")


def add_runcommand_hooks():
    if RUNCOMMAND_HOOKS_DIR.exists():
        onstart = Path(RUNCOMMAND_HOOKS_DIR, "runcommand-onstart.sh")
        if onstart.exists():
            onstartorig = Path(RUNCOMMAND_HOOKS_DIR, "runcommand-onstart.sh.orig")
            shutil.copy(onstart, onstartorig)
        with onstart.open("w") as fs:
            fs.write("touch ~/.musicpaused.flag")

        onend = Path(RUNCOMMAND_HOOKS_DIR, "runcommand-onend.sh")
        if onend.exists():
            onendorig = Path(RUNCOMMAND_HOOKS_DIR, "runcommand-onend.sh.orig")
            shutil.copy(onend, onendorig)
        with onend.open("w") as fs:
            fs.write("rm -f ~/.musicpaused.flag")


def remove_menu_options():
    DISABLE_BACKGROUND_MUSIC.unlink(missing_ok=True)
    ENABLE_BACKGROUND_MUSIC.unlink(missing_ok=True)


def ensure_python_version():
    """
    Ensures that the python version that runs this script is compatible
    """


class Installer:
    CURRENT_PYTHON = sys.executable
    CURRENT_PYTHON_VERSION = sys.version_info[:2]

    def __init__(
        self,
        accept_all=False,
    ):
        self._accept_all = accept_all

    def run(self, prerelease: bool = False):
        try:
            self.install(prerelease)
        except subprocess.CalledProcessError as e:
            print("error", f"An error has occured: {str(e)}")
            print(e.output.decode())

            return e.returncode

        print(
            "EmulationStation BGM installed successfully. Now go and put your music files inside "
            f"the folder {DEFAULT_MUSIC_FOLDER} and reboot."
        )

        return 0

    def uninstall(self):
        print("Uninstalling esbgm...")

        uninstall_from_pip()
        remove_autostart_script()

    def customize_install(self):
        if not self._accept_all:
            print("Before we start, please answer the following questions.")
            print("You may simply press the Enter key to leave unchanged.")

            modify_path = input("Modify PATH variable? ([y]/n) ") or "y"
            if modify_path.lower() in {"n", "no"}:
                self._modify_path = False

            print("")

    def customize_uninstall(self):
        if not self._accept_all:
            print()

            uninstall = input("Are you sure you want to uninstall Poetry? (y/[n]) ") or "n"
            if uninstall.lower() not in {"y", "yes"}:
                return False

            print("")

        return True

    def install(self, prerelease: bool):
        """
        Installs Poetry in $POETRY_HOME.
        """
        print("Installing esbgm...")

        install_from_pip(prerelease)
        add_menu_options()
        add_runcommand_hooks()
        add_autostart_script()
        create_default_music_folder()

        return 0

    # def _which_python(self):
    #     """Decides which python executable we'll embed in the launcher script."""
    #     allowed_executables = ["python3", "python"]
    #     if WINDOWS:
    #         allowed_executables += ["py.exe -3", "py.exe -2"]
    #
    #     # \d in regex ensures we can convert to int later
    #     version_matcher = re.compile(r"^Python (?P<major>\d+)\.(?P<minor>\d+)\..+$")
    #     fallback = None
    #     for executable in allowed_executables:
    #         try:
    #             raw_version = subprocess.check_output(
    #                 executable + " --version", stderr=subprocess.STDOUT, shell=True
    #             ).decode("utf-8")
    #         except subprocess.CalledProcessError:
    #             continue
    #
    #         match = version_matcher.match(raw_version.strip())
    #         if match:
    #             return executable
    #
    #         if fallback is None:
    #             # keep this one as the fallback; it was the first valid executable we
    #             # found.
    #             fallback = executable
    #
    #     if fallback is None:
    #         raise RuntimeError(
    #             "No python executable found in shell environment. Tried: "
    #             + str(allowed_executables)
    #         )
    #
    #     return fallback


def main():
    parser = argparse.ArgumentParser(description="Installs the latest version of BGM for EmulationStation")

    parser.add_argument(
        "-f",
        "--force",
        help="install on top of existing version",
        dest="force",
        action="store_true",
        default=False,
    )
    parser.add_argument(
        "-y",
        "--yes",
        help="accept all prompts",
        dest="accept_all",
        action="store_true",
        default=False,
    )
    parser.add_argument(
        "--prerelease", help="use prerelease package", dest="prerelease", action="store_true", default=False
    )
    parser.add_argument(
        "--uninstall",
        help="uninstall poetry",
        dest="uninstall",
        action="store_true",
        default=False,
    )

    args = parser.parse_args()

    installer = Installer(accept_all=args.accept_all)

    if args.uninstall:
        return installer.uninstall()

    return installer.run(prerelease=args.prerelease)


if __name__ == "__main__":
    sys.exit(main())
