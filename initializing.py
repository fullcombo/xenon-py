from kivy.uix.screenmanager import Screen
from requests import get
from hashlib import sha256 as sha
from threading import Thread, Event
from pathlib import Path
from lzma import decompress

class Initializing(Screen):

    def communicate_with_server(self, sha_url):
        host = 'http://xenon.laravel/'

        sha_request = get(sha_url)
        status.text = "Connection established successfully."
        progress.value += 1
        status.text = "Checking for simfile catalog..."
        catalog = Path('catalog.json')
        if catalog.exists():
            progress.value += 1
        else:
            status.text = "Requesting simfile catalog..."
            webxz = get(host + 'catalog.json.xz')
            catalogstream = webxz.content
            status.text = "Extracting simfile catalog..."
            cxz = decompress(catalogstream)
            catjson = open('catalog.json', 'wb')
            catjson.write(cxz)
            progress.value += 1

        status.text = "Verifying simfile catalog..."
        hash = sha()
        with open('catalog.json', 'rb') as catalog:
            buffer = catalog.read()
            hash.update(buffer)
        if sha_request.text == hash.hexdigest():
            status.text = "Simfile catalog verified."
            progress.value += 1
        else:
            status.text = "Catalog integrity failure."

        self.manager.current = "connected"
        return

    def on_enter(self, *args):
        host = 'http://xenon.laravel/'
        global progress
        progress = self.ids['progress']
        progress.max = 5
        global status
        status = self.ids['status']
        status.text = "Establishing connection to server..."
        sha_url = host + 'api/catalog/sha'
        task_event = Event()
        task_event.clear()
        comm = Thread(target=self.communicate_with_server, args=(sha_url,))
        comm.start()
