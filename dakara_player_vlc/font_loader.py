import os
import sys
import logging


SHARE_DIR = "share"
SHARE_DIR_ABSOLUTE = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                  os.pardir,
                                  SHARE_DIR)
FONT_DIR = "fonts"


logger = logging.getLogger("font_loader")


def get_font_loader_class():
    """Get the font loader associated to the current platform
    """
    if 'linux' in sys.platform:
        return FontLoaderLinux

    if 'win' in sys.platform:
        return FontLoaderWindows

    raise NotImplementedError(
            "This operating system is not currently supported"
            )


class FontLoader:
    GREETINGS = "Dummy font loader selected"

    def __init__(self):
        # show type of font loader
        logger.debug(self.GREETINGS)

    def load(self):
        pass

    def unload(self):
        pass

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.unload()


class FontLoaderLinux(FontLoader):
    GREETINGS = "Font loader for Linux selected"
    FONT_DIR_SYSTEM = "/usr/share/fonts"
    FONT_DIR_USER = os.path.join(os.environ['HOME'], ".fonts")

    def __init__(self):
        # call parent constructor
        super().__init__()

        # create list of fonts
        self.fonts_loaded = []

    def load(self):
        # ensure that the user font directory exists
        try:
            os.mkdir(self.FONT_DIR_USER)

        except OSError:
            pass

        self.load_from_directory(os.path.join(
            SHARE_DIR_ABSOLUTE,
            FONT_DIR
            ))

    def load_from_directory(self, directory):
        # check the directory exists
        if not os.path.isdir(directory):
            raise IOError("Directory '{}' does not exist".format(directory))

        logger.debug("Scanning directory '{}' for fonts".format(directory))

        # get the fonts
        font_file_path_list = []
        for font_file_name in os.listdir(directory):
            font_file_path_list.append(os.path.join(directory,
                                       font_file_name))

            logger.debug("Font '{}' found to install".format(font_file_name))

        self.load_from_list(font_file_path_list)

    def load_from_list(self, font_file_path_list):
        for font_file_path in font_file_path_list:
            # get font file name
            font_file_name = os.path.basename(font_file_path)

            # check if the font is installed at system level
            if os.path.isfile(os.path.join(
                    self.FONT_DIR_SYSTEM,
                    font_file_name
                    )):

                logger.debug(
                        "Font '{}' found in system directory".format(
                            font_file_name
                            )
                        )

                continue

            # check if the font is installed at user level
            if os.path.isfile(os.path.join(
                    self.FONT_DIR_USER,
                    font_file_name
                    )):

                logger.debug("Font '{}' found in user directory".format(
                    font_file_name
                    ))

                continue

            # then, if the font is not installed, install it
            font_file_target_path = os.path.join(
                    self.FONT_DIR_USER,
                    font_file_name
                    )

            os.symlink(
                    font_file_path,
                    font_file_target_path
                    )

            # register the font
            self.fonts_loaded.append(font_file_target_path)

            logger.debug("Font '{}' loaded in user directory: '{}'".format(
                font_file_path,
                font_file_target_path
                ))

    def unload(self):
        for font_path in self.fonts_loaded:
            try:
                os.unlink(font_path)
                logger.debug("Font '{}' unloaded".format(
                    font_path
                    ))

            except OSError:
                logger.error("Unable to unload '{}'".format(
                    font_path
                    ))

        self.fonts_loaded = []


class FontLoaderWindows(FontLoader):
    GREETINGS = "Font loader for Windows selected"

    def load(self):
        font_path = os.path.join(
            SHARE_DIR,
            FONT_DIR
            )

        # since there seems to be no workable way to install fonts on Windows
        # through Python, we ask the user to do it by themselve
        print("Please install the following fonts located in the '{}' folder \
and press Enter:".format(font_path))

        for font_file in os.listdir(font_path):
            print(font_file)

        input()
