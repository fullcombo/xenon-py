from kivy.uix.screenmanager import Screen, SlideTransition, NoTransition
from kivy.config import Config
from os import environ
from pathlib import Path

class Connected(Screen):
    def disconnect(self):
        self.manager.transition = SlideTransition(direction="right")
        self.manager.current = 'login'
        self.manager.get_screen('login').resetForm()
    def settings(self):
        self.manager.transition = SlideTransition(direction="left")
        self.manager.current = 'settings'
    def on_enter(self, *args):
        Config.read("xenon.ini")
        if Config.get('app','datadir') is '':
            appdata = Path(environ['APPDATA'] + '/StepMania 5')
            if appdata.exists():
                Config.set('app', 'datadir', appdata)
                Config.write()
            else:  # user has provided their own folder
                pass

        if Config.get('app','sm5dir') is '':
            self.settings()
    def submitscores(self):
        self.manager.transition = NoTransition()
        self.manager.current = 'submitscores'
