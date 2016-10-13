import xbmc
import xbmcaddon
import xbmcgui
import time
from subprocess import Popen
import zmq
import os
import _json
import json
import threading
import requests
import signal
from collections import defaultdict

__addon__        = xbmcaddon.Addon()
__addonversion__ = __addon__.getAddonInfo('version')
__addonid__      = __addon__.getAddonInfo('id')
__addonname__    = __addon__.getAddonInfo('name')
__icon__ = __addon__.getAddonInfo('icon')
addon_dir = xbmc.translatePath(__addon__.getAddonInfo('path'))
direct = addon_dir + "/resources/contacts.json"
username = __addon__.getSetting('username')
password = __addon__.getSetting('password')

context = zmq.Context()

headers = {'NGV-Api-Key': 'ietkskrivnost258'}
url = "http://registracija.ietkims.uni-mb.si/gab"
r = requests.get(url, headers=headers)
data = r.json()
str_json = json.dumps(data)
data1 = str_json.encode("ascii")


with open(direct, 'w') as out:
    json.dump(data, out)

time1 = 2000

class SubscribeThread (threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        xbmc.log("starting service IETKIMS nclient")
        if (len(username) < 2 or len(password) < 2):
            __addon__.openSettings()
        """"os.system(addon_dir + "/./vidgui &")"""""
        xbmc.log(addon_dir+"vidgui")
        self.child = Popen(addon_dir + "/vidgui")
        xbmc.log("zagnal vidgui-------------------------------")

    def run(self):
        self.init()
        xbmc.log("nit run")
        try:
            subscriber = context.socket(zmq.SUB)
            subscriber.connect("tcp://127.0.0.1:4003")
            subscriber.setsockopt(zmq.SUBSCRIBE, b"ONREG")
            subscriber.setsockopt(zmq.SUBSCRIBE, b"ONREJECT")
            subscriber.setsockopt(zmq.SUBSCRIBE, b"ONCALL")
            subscriber.setsockopt(zmq.SUBSCRIBE, b"ONINCALL")
            subscriber.RCVTIMEO = 1000
            publisher = context.socket(zmq.PUB)
            publisher.bind("tcp://127.0.0.1:4002")
        except:
            pass
        monitor = xbmc.Monitor()
        xbmc.executebuiltin(
            'Notification(%s, %s, %d, %s)' % (__addonname__, "Service tece123: ", time1, __icon__))
        while not monitor.abortRequested():
            try:
                [command, contents] = subscriber.recv_multipart()
                if (command == b'ONINCALL'):
                    xbmc.log("onincall: " + contents)
                    dialog = xbmcgui.Dialog()
                    ret = dialog.yesno(heading='IETK IMS client', line1='Incomming call',
                                       line2=contents.split(':')[1].split('>')[0], nolabel='reject', yeslabel='answer')
                    xbmc.log('dohodni klic: ' + str(ret))
                    if (ret):
                        publisher.send_multipart([b"ANSWER", b""])
                    else:
                        publisher.send_multipart([b"REJECT", b""])
                if (command == b'ONREG'):
                    dialog = xbmcgui.Dialog()
                    dialog.notification('IETK IMS client', command + contents, xbmcgui.NOTIFICATION_INFO, 5000)
                if (command == b'ONCALL'):
                    dialog = xbmcgui.Dialog()
                    dialog.notification('Kliccc', command + contents, xbmcgui.NOTIFICATION_INFO, 5000)
                    dialog2 = xbmcgui.Dialog()
                    ok = dialog2.ok('IETK IMS', 'Prekini?')
                    if (ok):
                        publisher.send_multipart([b"REJECT", b""])

                if (command == b'ONREJECT'):
                    dialog = xbmcgui.Dialog()
                    dialog.notification('IETK IMS client', command + contents, xbmcgui.NOTIFICATION_INFO, 5000)

            except:
                pass

        xbmc.log("Abort requested. Terminating.")
        os.kill(self.child.pid, signal.SIGKILL)
        xbmc.log("UBIL CHILDA")
        return

    def init(self):
        try:
            socket = context.socket(zmq.REP)
            socket.bind("tcp://*:4001")
            message = socket.recv()
            xbmc.log("Received request: %s" % message)
            xbmc.log("Username : %s " % username)
            xbmc.log("password: %s " % password)
            socket.send_multipart([username.encode('ascii'), password.encode('ascii')])
            xbmc.log("POslal setingse")

        except:
            return




if __name__ == '__main__':
    thread = SubscribeThread()
    thread.start()

