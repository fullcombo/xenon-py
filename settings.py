from kivy.uix.screenmanager import Screen, SlideTransition
from kivy.config import Config

class Settings(Screen):
    def apply(self):
        Config.set('app', 'sm5dir', self.ids['sm5dir'].text)
        Config.set('app', 'datadir', self.ids['datadir'].text)
        Config.set('app', 'localprofile', self.ids['localprofile'].text)
        Config.set('app', 'uploadfails', self.ids['uploadfails'].active)
        Config.write()
        self.manager.transition = SlideTransition(direction="right")
        self.manager.current = 'connected'

    def cancel(self):
        self.manager.transition = SlideTransition(direction="right")
        self.manager.current = 'connected'
        self.manager.get_screen('settings').resetForm()

    def resetForm(self):
        self.ids['sm5dir'].text = Config.get('app', 'sm5dir')
        self.ids['datadir'].text = Config.get('app', 'datadir')
        self.ids['localprofile'].text = Config.get('app', 'localprofile')
        self.ids['uploadfails'].text = Config.get('app', 'uploadfails')

    def on_enter(self, *args):
        Config.read("xenon.ini")
        self.ids['sm5dir'].text = Config.get('app', 'sm5dir')
        self.ids['datadir'].text = Config.get('app', 'datadir')
        self.ids['localprofile'].text = Config.get('app', 'localprofile')
        self.ids['uploadfails'].text = Config.get('app', 'uploadfails')
