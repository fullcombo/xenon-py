from kivy.app import App
from kivy.properties import StringProperty
from kivy.uix.screenmanager import ScreenManager, Screen, NoTransition
from kivy.config import Config
from kivy.core.window import Window
from threading import Thread
from requests import post

from connected import Connected
from initializing import Initializing
from settings import Settings
from submitscores import SubmitScores

global host
host = 'http://xenon.laravel/'

class Login(Screen):
    def login_worker(self, loginText, passwordText):
        url = host + 'oauth/token'
        app = App.get_running_app()
        app.username = loginText
        app.password = passwordText
        response = post(url, data={'username': app.username, 'password': app.password, 'grant_type': 'password', 'client_id': 2, 'client_secret': 'XEh8Q8JKmOvTNX2g7QXtrRLzwSO1XQuWpge04zRB'})
        rj = response.json()
        if response.status_code is not 200:
            self.resetForm()
            self.ids['status'].text = rj.get('message')
        else:
            Config.read('xenon.ini')
            Config.set('auth', 'access_token', rj.get('access_token'))
            Config.set('auth', 'refresh_token', rj.get('refresh_token'))
            Config.write()
            self.manager.current='connected'
        return

    def do_login(self, loginText, passwordText):
        button = self.ids['thebutton']
        button.text = 'Logging in...'
        button.disabled = True
        comm = Thread(target=self.login_worker, args=(loginText, passwordText,))
        comm.start()

    def resetForm(self):
        self.ids['login'].text = ""
        self.ids['password'].text = ""
        self.ids['thebutton'].disabled = False
        self.ids['thebutton'].text = "Log In"

    def __init__(self, **kwargs):
        super(Login, self).__init__(**kwargs)
        Window.bind(on_key_down=self._on_keyboard_down)

    def _on_keyboard_down(self, instance, keyboard, keycode, text, modifiers):
        if keycode in (40, 88):
            self.do_login(self.ids['login'].text, self.ids['password'].text)

class Xenon(App):
    def build_config(self, config):
        config.setdefaults('kivy', {
            'log_enable': '0',
            'exit_on_escape': '0'
        })
        config.setdefaults('graphics', {
            'height': '400',
            'width': '800',
            'resizable': 0
        })
        config.setdefaults('auth', {
            'access_token': '0',
            'refresh_token': '0'
        })
        config.setdefaults('app', {
            'sm5dir': '',
            'datadir': '',
            'localprofile': '',
            'uploadfails': '0'
        })

    username = StringProperty(None)
    password = StringProperty(None)

    def build(self):
        Window.clearcolor = (0.333, 0.466, 0.2, 1)
        self.icon = 'icon.png'
        manager = ScreenManager()
        manager.add_widget(Login(name='login'))
        manager.add_widget(Connected(name='connected'))
        manager.add_widget(Initializing(name='initializing'))
        manager.add_widget(Settings(name='settings'))
        manager.add_widget(SubmitScores(name='submitscores'))
        Config.read('xenon.ini')
        if Config.get('auth', 'access_token') is not '0':
            manager.transition = NoTransition()
            manager.current = 'initializing'
        return manager


if __name__ == '__main__':
    Xenon().run()
