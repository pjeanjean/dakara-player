from unittest import TestCase
from unittest.mock import Mock, patch
from threading import Event
from queue import Queue
from configparser import ConfigParser
import logging
import os

from vlc import State, EventType

from dakara_player_vlc.version import __version__ as dakara_player_vlc_version
from dakara_player_vlc.vlc_player import (
        VlcPlayer,
        mrl_to_path,
        SHARE_DIR_ABSOLUTE,
        IDLE_BG_PATH,
        TRANSITION_BG_PATH,
        )


# shut down vlc_player logging
logging.getLogger("vlc_player").setLevel(logging.CRITICAL)


class VlcPlayerTestCase(TestCase):
    """Test the VLC player module
    """
    def setUp(self):
        # create instance parameter
        self.instance_parameter = ""

        # create fullscreen flag
        self.fullscreen = "yes"

        # create kara folder
        self.kara_folder = SHARE_DIR_ABSOLUTE

        # create media parameter
        self.media_parameter = "no-video"

        # create idle background path
        self.idle_background_path = IDLE_BG_PATH

        # create transition background path
        self.transition_background_path = TRANSITION_BG_PATH

        # create transition duration
        self.transition_duration = 1

        # create a subtitle
        self.subtitle_path = os.path.join(
                SHARE_DIR_ABSOLUTE,
                "test_screen.ass"
                )

        # create a mock text generator
        self.text_generator = Mock()

        # create song path
        self.song_file_path = IDLE_BG_PATH

        # create playlist entry
        self.playlist_entry = {
                'id': 0,
                'song': {
                    'file_path': os.path.basename(self.song_file_path),
                    }
                }

        # create config
        self.config = ConfigParser()
        self.config['vlc'] = {
                'instanceParameter': self.instance_parameter,
                'karaFolder': self.kara_folder,
                'mediaParameter': self.media_parameter,
                'idleBgPath': self.idle_background_path,
                'transitionBgPath': self.transition_background_path,
                'transitionDuration': self.transition_duration,
                'fullscreen': self.fullscreen,
                }

        # create vlc player
        self.vlc_player = VlcPlayer(
                Event(),
                Queue(),
                self.config['vlc'],
                self.text_generator
                )

        self.vlc_player.set_song_end_callback(lambda self, event: None)
        self.vlc_player.set_error_callback(lambda self, event: None)

    def get_event_and_callback(self):
        """Get an event and a callback that sets this event
        """
        event = Event()

        def callback(*args, **kwargs):
            event.set()

        return event, callback

    def test_play_idle_screen(self):
        """Test the display of the idle screen
        """
        # mock the text generator
        self.text_generator.create_idle_text.return_value = self.subtitle_path

        # create an event for when the player starts to play
        is_playing, callback_is_playing = self.get_event_and_callback()
        self.vlc_player.event_manager.event_attach(
                EventType.MediaPlayerPlaying,
                callback_is_playing
                )

        # pre assertions
        self.assertIsNone(self.vlc_player.player.get_media())
        self.assertEqual(self.vlc_player.player.get_state(),
                         State.NothingSpecial)

        # call the method
        self.vlc_player.play_idle_screen()

        # wait for the player to start actually playing
        is_playing.wait()

        # call assertions
        self.text_generator.create_idle_text.assert_called_once_with({
            'notes': [
                "VLC " + self.vlc_player.vlc_version,
                "Dakara player " + dakara_player_vlc_version
                ]
            })

        # post assertions
        self.assertEqual(self.vlc_player.player.get_state(),
                         State.Playing)

        self.assertIsNotNone(self.vlc_player.player.get_media())
        media = self.vlc_player.player.get_media()
        file_path = mrl_to_path(media.get_mrl())
        self.assertEqual(file_path, self.idle_background_path)
        # TODO check which subtitle file is read
        # seems impossible to do for now

    def test_play_song(self):
        """Test to play of a song

        First, the transition screen is played, then the song itself.
        """
        # mock the text generator
        self.text_generator.create_transition_text.return_value = \
            self.subtitle_path

        # create an event for when the player starts to play
        is_playing, callback_is_playing = self.get_event_and_callback()
        self.vlc_player.event_manager.event_attach(
                EventType.MediaPlayerPlaying,
                callback_is_playing
                )

        # pre assertions
        self.assertIsNone(self.vlc_player.playing_id)
        self.assertFalse(self.vlc_player.in_transition)
        self.assertIsNone(self.vlc_player.player.get_media())
        self.assertEqual(self.vlc_player.player.get_state(),
                         State.NothingSpecial)

        # call the method
        self.vlc_player.play_song(self.playlist_entry)

        # wait for the player to start actually playing the transition
        is_playing.wait()

        # reset the event to catch when the player starts to play the song
        is_playing.clear()

        # call assertions
        self.text_generator.create_transition_text.assert_called_once_with(
                self.playlist_entry
                )

        # post assertions for transition screen
        self.assertIsNotNone(self.vlc_player.playing_id)
        self.assertTrue(self.vlc_player.in_transition)
        self.assertEqual(self.vlc_player.player.get_state(),
                         State.Playing)

        self.assertIsNotNone(self.vlc_player.player.get_media())
        media = self.vlc_player.player.get_media()
        file_path = mrl_to_path(media.get_mrl())
        self.assertEqual(file_path, self.transition_background_path)
        # TODO check which subtitle file is read
        # seems impossible to do for now

        # wait for the player to start actually playing the song
        is_playing.wait()

        # post assertions for song
        self.assertFalse(self.vlc_player.in_transition)
        self.assertEqual(self.vlc_player.player.get_state(),
                         State.Playing)

        self.assertIsNotNone(self.vlc_player.player.get_media())
        media = self.vlc_player.player.get_media()
        file_path = mrl_to_path(media.get_mrl())
        self.assertEqual(file_path, self.song_file_path)

    @patch('dakara_player_vlc.vlc_player.os.path.isfile')
    def test_play_song_error_file(self, mock_isfile):
        """Test to play a file that does not exist
        """
        # mock the system call
        mock_isfile.return_value = False

        # pre assertions
        self.assertIsNone(self.vlc_player.playing_id)
        self.assertIsNone(self.vlc_player.player.get_media())
        self.assertEqual(self.vlc_player.player.get_state(),
                         State.NothingSpecial)

        # call the method
        self.vlc_player.play_song(self.playlist_entry)

        # call assertions
        mock_isfile.assert_called_once_with(self.song_file_path)

        # post assertions
        self.assertIsNone(self.vlc_player.playing_id)
        self.assertIsNone(self.vlc_player.player.get_media())
        self.assertEqual(self.vlc_player.player.get_state(),
                         State.NothingSpecial)


class MrlToPathTestCase(TestCase):
    """Test the `mrl_to_path` function
    """
    def test(self):
        """Test to call the function with various arguments
        """
        self.assertEqual(mrl_to_path('file:///a/b/c'), '/a/b/c')
        self.assertEqual(mrl_to_path('file:///a/b%20b/c'), '/a/b b/c')
