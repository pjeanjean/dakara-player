import os
import logging
from codecs import open
from configparser import ConfigParser

from jinja2 import Environment, FileSystemLoader


SHARE_DIR = 'share'
SHARE_DIR_ABSOLUTE = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                  os.pardir,
                                  SHARE_DIR)


TRANSITION_TEMPLATE_NAME = "transition.ass"
TRANSITION_TEXT_NAME = "transition.ass"


IDLE_TEMPLATE_NAME = "idle.ass"
IDLE_TEXT_NAME = "idle.ass"


ICON_MAP_FILE = "font-awesome.ini"


LINK_TYPE_NAMES = {
    'OP': "Opening",
    'ED': "Ending",
    'IN': "Insert song",
    'IS': "Image song"
}


logger = logging.getLogger("text_generator")


class TextGenerator:
    def __init__(self, config, tempdir):
        self.tempdir = tempdir
        # load icon mapping
        self.load_icon_map()

        # load templates
        self.load_templates(config)

        # set text paths
        self.transition_text_path = os.path.join(
                self.tempdir,
                TRANSITION_TEXT_NAME
                )

        self.idle_text_path = os.path.join(
                self.tempdir,
                IDLE_TEXT_NAME
                )

    def load_templates(self, config):
        # create Jinja2 environment
        self.environment = Environment(
                loader=FileSystemLoader(SHARE_DIR_ABSOLUTE)
                )

        # add filter for converting font icon name to character
        self.environment.filters['icon'] = self.convert_icon

        # add filter for work link type complete name
        self.environment.filters['link_type_name'] = (
            self.convert_link_type_name
        )

        transition_template_path = config.get(
                'transitionTemplateName',
                TRANSITION_TEMPLATE_NAME
                )

        idle_template_path = config.get('idleTemplateName', IDLE_TEMPLATE_NAME)

        # load templates
        self.load_transition_template(transition_template_path)
        self.load_idle_template(idle_template_path)

    def convert_icon(self, name):
        """Convert the name of an icon to its code

        Args:
            name (str): name of the icon.

        Returns:
            str: corresponding character.
        """
        return chr(int(self.icon_map.get(name, '0020'), 16))

    @staticmethod
    def convert_link_type_name(link_type):
        """Convert the short name of a link type to its long name

        Args:
            link_type (str): short name of the link type.

        Returns:
            str: long name of the link type.
        """
        return LINK_TYPE_NAMES[link_type]

    def create_idle_text(self, info):
        """ Create custom idle text and save it

            Args:
                info: dictionnary of additionnal information.

            Returns:
                path of the text containing the idle screen content.
        """
        # using the template
        idle_text = self.idle_template.render(
                **info
                )

        with open(self.idle_text_path, 'w', encoding='utf8') as file:
            file.write(idle_text)

        logger.debug("Create idle screen text file in \
\"{}\"".format(self.idle_text_path))

        return self.idle_text_path

    def create_transition_text(self, playlist_entry):
        """ Create custom transition text and save it

            Args:
                playlist_entry: dictionary containing keys for the playlist
                    entry.

            Returns:
                path of the text containing the transition screen
                content.
        """
        transition_text = self.transition_template.render(playlist_entry)

        with open(self.transition_text_path, 'w', encoding='utf8') as file:
            file.write(transition_text)

        logger.debug("Create transition screen text file in \
\"{}\"".format(self.transition_text_path))

        return self.transition_text_path

    def load_icon_map(self):
        """ Load the icon map
        """
        icon_map_path = os.path.join(SHARE_DIR_ABSOLUTE, ICON_MAP_FILE)

        if not os.path.isfile(icon_map_path):
            raise IOError("Icon font map file '{}' not found".format(
                icon_map_path
                ))

        icon_map = ConfigParser()
        icon_map.read(icon_map_path)
        self.icon_map = icon_map['map']

    def load_transition_template(self, template_name):
        """ Load transition screen text template file

            Load the default or customized ASS template for
            transition screen.
        """
        template_path = os.path.join(SHARE_DIR_ABSOLUTE, template_name)
        template_default_path = os.path.join(SHARE_DIR,
                                             TRANSITION_TEMPLATE_NAME)

        if os.path.isfile(template_path):
            pass

        elif os.path.isfile(template_default_path):
            logger.warning("Transition template file not found \"{}\", \
using default one".format(template_path))

            template_name = TRANSITION_TEMPLATE_NAME

        else:
            raise IOError("No template file for transition screen found")

        logger.debug("Loading transition template file \"{}\"".format(
            template_path
            ))

        self.transition_template = self.environment.get_template(template_name)

    def load_idle_template(self, template_name):
        """ Load idle screen text template file

            Load the default or customized ASS template for
            idle screen.
        """
        template_path = os.path.join(SHARE_DIR_ABSOLUTE, template_name)
        template_default_path = os.path.join(SHARE_DIR_ABSOLUTE,
                                             IDLE_TEMPLATE_NAME)

        if os.path.isfile(template_path):
            pass

        elif os.path.isfile(template_default_path):
            logger.warning("Idle template file not found \"{}\", \
using default one".format(template_path))

            template_name = IDLE_TEMPLATE_NAME

        else:
            raise IOError("No template file for idle screen found")

        logger.debug("Loading idle template file \"{}\"".format(
            template_path
            ))

        self.idle_template = self.environment.get_template(template_name)