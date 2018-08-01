from kivy.uix.screenmanager import Screen, NoTransition, SlideTransition
from kivy.config import Config
from requests import get, put
from hashlib import sha256 as sha
from threading import Thread, Event
from pathlib import Path
from json import load, loads, dump
from time import sleep
import xml.etree.ElementTree as XML
from os import listdir
from glob import glob

class SubmitScores(Screen):

    def communicate_with_server(self, host):
        status.text = "Oh shit we're doing the thing!"

        status.text = "Getting score data from server..."
        Config.read("xenon.ini")
        count_r = get(host + 'api/manifest/count', headers={'Authorization': 'Bearer ' + Config.get('auth', 'access_token')})
        status.text = "Found " + count_r.text + " scores."
        progress.value = 0

        manifest = Path('manifest.json')
        status.text = "Downloading score manifest..."
        manifest_r = get(host + 'api/manifest', headers={'Authorization': 'Bearer ' + Config.get('auth', 'access_token'), 'Accept': 'application/json'})
        manifest_json = manifest_r.text
        mani = loads(manifest_json)
        with open(manifest, 'w') as outfile:
            dump(mani, outfile)

        if Config.get('app', 'localprofile') is not '':
            stats = XML.parse(Path(Config.get('app', 'datadir') + '/Save/LocalProfiles/' + Config.get('app', 'localprofile') + '/Stats.xml'))
            statsroot = stats.getroot()
            playerguid = statsroot.find('./GeneralData/Guid').text

        else:
            playerguid = ''

        uploadpath = Path(Config.get('app', 'datadir') + '/Save/Upload')
        uploads = listdir(uploadpath)
        uploadscount = len(uploads)
        uploadfailsbool = Config.get('app', 'uploadfails')
        progress.max = uploadscount
        with open(Path("catalog.json")) as cjhandle:
            catalog = load(cjhandle)
        status.text = "Found " + str(uploadscount) + " scores."
        newscorescount = 0
        newuploads = {}
        for upload in uploads:
            handle = XML.parse(Path(uploadpath, upload))  # open an individual upload file
            uploadroot = handle.getroot()  # establish the root of the XML file
            uploadguid = uploadroot.find('./RecentSongScores/HighScoreForASongAndSteps/HighScore/PlayerGuid').text
            if str(uploadroot.find('./RecentSongScores/HighScoreForASongAndSteps/HighScore/Grade').text) == 'Failed':
                if str(uploadfailsbool) == 'False':
                    status.text = "Skipping " + uploadroot.find('./RecentSongScores/HighScoreForASongAndSteps/HighScore/Guid').text
                    progress.value += 1
                    continue
            if playerguid == uploadguid:  # begin hashing the simfile and make sure it's in the catalog
                songloc = uploadroot.find('./RecentSongScores/HighScoreForASongAndSteps/Song').attrib['Dir']
                songstr = Config.get('app', 'sm5dir') + '/' + songloc
                songglob = glob(songstr + '/*.sm')
                try:
                    songpath = Path(songglob[0])
                except IndexError:
                    songglob = glob(songstr + '/*.dwi')
                    try:
                        songpath = Path(songglob[0])
                    except IndexError:
                        status.text = "Skipping " + uploadroot.find('./RecentSongScores/HighScoreForASongAndSteps/HighScore/Guid').text
                        progress.value += 1
                        continue

                hash = sha()
                with open(songpath, 'rb') as f:
                    buffer = f.read()
                    hash.update(buffer)
                sha256 = hash.hexdigest().upper()
                for entry in catalog:
                    if sha256 in entry['SHA256']:
                        stepstype = uploadroot.find('./RecentSongScores/HighScoreForASongAndSteps/Steps').attrib['StepsType']
                        difficulty = uploadroot.find('./RecentSongScores/HighScoreForASongAndSteps/Steps').attrib['Difficulty']
                        for chart in entry['catalog']:
                            if chart['stepstype'] == stepstype and chart['difficulty'] == difficulty:
                                chartid = chart['id']
                                break
                            else:
                                chartid = 0
                        break
                    else:
                        chartid = 0
                if chartid is 0:  # we didn't find a matching hash/stepstype/difficulty in the catalog
                    status.text = "Skipping " + uploadroot.find('./RecentSongScores/HighScoreForASongAndSteps/HighScore/Guid').text
                    progress.value += 1
                    continue
                #  check if it's in the manifest!
                with open(Path("manifest.json")) as manifest:
                    mjson = load(manifest)
                if uploadroot.find('./RecentSongScores/HighScoreForASongAndSteps/HighScore/Guid').text in mjson:
                    status.text = "Skipping " + uploadroot.find('./RecentSongScores/HighScoreForASongAndSteps/HighScore/Guid').text
                    progress.value += 1
                    continue

                # if we've made it this far with the file, it's a new score and should be uploaded
                newuploads[progress.value] = {
                    'chart_id': chartid,
                    'W1': uploadroot.find('./RecentSongScores/HighScoreForASongAndSteps/HighScore/TapNoteScores/W1').text,
                    'W2': uploadroot.find('./RecentSongScores/HighScoreForASongAndSteps/HighScore/TapNoteScores/W2').text,
                    'W3': uploadroot.find('./RecentSongScores/HighScoreForASongAndSteps/HighScore/TapNoteScores/W3').text,
                    'W4': uploadroot.find('./RecentSongScores/HighScoreForASongAndSteps/HighScore/TapNoteScores/W4').text,
                    'W5': uploadroot.find('./RecentSongScores/HighScoreForASongAndSteps/HighScore/TapNoteScores/W5').text,
                    'Miss': uploadroot.find('./RecentSongScores/HighScoreForASongAndSteps/HighScore/TapNoteScores/Miss').text,
                    'Held': uploadroot.find('./RecentSongScores/HighScoreForASongAndSteps/HighScore/HoldNoteScores/Held').text,
                    'LetGo': uploadroot.find('./RecentSongScores/HighScoreForASongAndSteps/HighScore/HoldNoteScores/LetGo').text,
                    'x_MachineGuid': uploadroot.find('./MachineGuid').text,
                    'x_Grade': uploadroot.find('./RecentSongScores/HighScoreForASongAndSteps/HighScore/Grade').text,
                    'x_Score': uploadroot.find('./RecentSongScores/HighScoreForASongAndSteps/HighScore/Score').text,
                    'x_PercentDP': uploadroot.find('./RecentSongScores/HighScoreForASongAndSteps/HighScore/PercentDP').text,
                    'x_MaxCombo': uploadroot.find('./RecentSongScores/HighScoreForASongAndSteps/HighScore/MaxCombo').text,
                    'x_StageAward': uploadroot.find('./RecentSongScores/HighScoreForASongAndSteps/HighScore/StageAward').text,
                    'x_PeakComboAward': uploadroot.find('./RecentSongScores/HighScoreForASongAndSteps/HighScore/PeakComboAward').text,
                    'x_Modifiers': uploadroot.find('./RecentSongScores/HighScoreForASongAndSteps/HighScore/Modifiers').text,
                    'x_DateTime': uploadroot.find('./RecentSongScores/HighScoreForASongAndSteps/HighScore/DateTime').text,
                    'x_PlayerGuid': uploadroot.find('./RecentSongScores/HighScoreForASongAndSteps/HighScore/PlayerGuid').text,
                    'x_HitMine': uploadroot.find('./RecentSongScores/HighScoreForASongAndSteps/HighScore/TapNoteScores/HitMine').text,
                    'x_AvoidMine': uploadroot.find('./RecentSongScores/HighScoreForASongAndSteps/HighScore/TapNoteScores/AvoidMine').text,
                    'x_CheckpointMiss': uploadroot.find('./RecentSongScores/HighScoreForASongAndSteps/HighScore/TapNoteScores/CheckpointMiss').text,
                    'x_CheckpointHit': uploadroot.find('./RecentSongScores/HighScoreForASongAndSteps/HighScore/TapNoteScores/CheckpointHit').text,
                    'x_MissedHold': uploadroot.find('./RecentSongScores/HighScoreForASongAndSteps/HighScore/HoldNoteScores/MissedHold').text,
                    'x_Stream': uploadroot.find('./RecentSongScores/HighScoreForASongAndSteps/HighScore/RadarValues/Stream').text,
                    'x_Voltage': uploadroot.find('./RecentSongScores/HighScoreForASongAndSteps/HighScore/RadarValues/Voltage').text,
                    'x_Air': uploadroot.find('./RecentSongScores/HighScoreForASongAndSteps/HighScore/RadarValues/Air').text,
                    'x_Freeze': uploadroot.find('./RecentSongScores/HighScoreForASongAndSteps/HighScore/RadarValues/Freeze').text,
                    'x_Chaos': uploadroot.find('./RecentSongScores/HighScoreForASongAndSteps/HighScore/RadarValues/Chaos').text,
                    'x_Notes': uploadroot.find('./RecentSongScores/HighScoreForASongAndSteps/HighScore/RadarValues/Notes').text,
                    'x_TapsAndHolds': uploadroot.find('./RecentSongScores/HighScoreForASongAndSteps/HighScore/RadarValues/TapsAndHolds').text,
                    'x_Jumps': uploadroot.find('./RecentSongScores/HighScoreForASongAndSteps/HighScore/RadarValues/Jumps').text,
                    'x_Holds': uploadroot.find('./RecentSongScores/HighScoreForASongAndSteps/HighScore/RadarValues/Holds').text,
                    'x_Mines': uploadroot.find('./RecentSongScores/HighScoreForASongAndSteps/HighScore/RadarValues/Mines').text,
                    'x_Hands': uploadroot.find('./RecentSongScores/HighScoreForASongAndSteps/HighScore/RadarValues/Hands').text,
                    'x_Rolls': uploadroot.find('./RecentSongScores/HighScoreForASongAndSteps/HighScore/RadarValues/Rolls').text,
                    'x_Lifts': uploadroot.find('./RecentSongScores/HighScoreForASongAndSteps/HighScore/RadarValues/Lifts').text,
                    'x_Fakes': uploadroot.find('./RecentSongScores/HighScoreForASongAndSteps/HighScore/RadarValues/Fakes').text,
                    'x_Disqualified': uploadroot.find('./RecentSongScores/HighScoreForASongAndSteps/HighScore/Disqualified').text,
                    'x_Pad': uploadroot.find('./RecentSongScores/HighScoreForASongAndSteps/HighScore/Pad').text,
                    'x_StageGuid': uploadroot.find('./RecentSongScores/HighScoreForASongAndSteps/HighScore/StageGuid').text,
                    'x_Guid': uploadroot.find('./RecentSongScores/HighScoreForASongAndSteps/HighScore/Guid').text
                }
                status.text = "Found " + uploadroot.find('./RecentSongScores/HighScoreForASongAndSteps/HighScore/Guid').text
                progress.value += 1
                newscorescount += 1
                continue
            else:
                status.text = "Skipping " + uploadroot.find('./RecentSongScores/HighScoreForASongAndSteps/HighScore/Guid').text
                progress.value += 1
                continue
        upload = put(host + 'api/scores', headers={'Authorization': 'Bearer ' + Config.get('auth','access_token'), 'Accept': 'application/json'}, json=newuploads)
        status.text = "Uploaded " + str(newscorescount) + " new scores."
        sleep(3)
        self.manager.current='connected'
        return

    def on_enter(self, *args):
        host = 'http://xenon.laravel/'
        global progress
        progress = self.ids['progress']
        progress.max = 5
        global status
        status = self.ids['status']
        status.text = "Preparing to upload scores..."
        task_event = Event()
        task_event.clear()
        comm = Thread(target=self.communicate_with_server, args=(host,))
        comm.start()
