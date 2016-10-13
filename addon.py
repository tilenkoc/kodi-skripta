import xbmc
import xbmcaddon
import xbmcgui
import urllib, json
import pyxbmct
import threading
from collections import defaultdict
import zmq



__addon__ = xbmcaddon.Addon()
__addonname__ = __addon__.getAddonInfo('name')
__icon__ = __addon__.getAddonInfo('icon')
addon_dir = xbmc.translatePath(__addon__.getAddonInfo('path'))
contacts = addon_dir + "/resources/contacts.json"
slika = addon_dir + "/resources/ikona.png"
ACTION_PREVIOUS_MENU = 10
xbfont_left = 0x00000000
xbfont_right = 0x00000001
xbfont_center_x = 0x00000002
xbfont_center_y = 0x00000004
xbfont_truncated = 0x00000008
context = zmq.Context()



class Gui(pyxbmct.AddonDialogWindow):
    def __init__(self, title=''):
        super(Gui, self).__init__(title)
        self.setGeometry(1000, 720, 6, 6)
        self.socketSub = context.socket(zmq.SUB)
        self.socketPub = context.socket(zmq.PUB)
        self.socketPub.bind("tcp://127.0.0.1:4004")
        self.topicPub = "CALL"
        self.buttons = []
        self.names = []
        self.PhoneBook = defaultdict(list)
        self.set_info_controls()
        self.set_connect()
        xbmc.log('Startan PROBA ADDON : ----------------------------')

    def set_info_controls(self):
        with open(contacts) as data_file:
            data = json.load(data_file)
        row = 0
        column = 0
        for i in data['contacts']:
            if column > 5:
                column = 0
                row += 1
            name = i['full_name']
            number = i['numbers']
            self.names.append(name)
            for j in number:
                self.PhoneBook[name].append(j)
            self.buttons.append(pyxbmct.Button(name,  textOffsetY=80, alignment=xbfont_center_x, focusTexture=slika, noFocusTexture=slika, focusedColor='0xFFFF00FF'))
            self.placeControl(self.buttons[-1], row, column, pad_y=15)
            column += 1


    def set_connect(self):
        length = len(self.buttons)
        for i in range(0, len(self.buttons)):
            self.connect(self.buttons[i], self.get_btn_id(i))
            self.buttons[i].controlRight(self.buttons[(i + 1) % length])  # i+1%10 will wrap the navigation)
            self.buttons[(i + 1) % length].controlLeft(self.buttons[i])
            if (i+6) >= length:
                self.buttons[i].controlDown(self.buttons[i%6])
                self.buttons[i%6].controlUp(self.buttons[i])
            else:
                self.buttons[i].controlDown(self.buttons[(i+6) % length])
                self.buttons[(i + 6) % length].controlUp(self.buttons[i])
            self.setFocus(self.buttons[0])

    def get_btn_id(self, i):
        def get_id():
            self.preveri_stevilko(i)
        return get_id

    def display_dialog(self, id):
        dialog = xbmcgui.Dialog()
        dialog.ok('XBMC', 'Izbrali smo  ' + str(self.names[id]))

    def preveri_stevilko(self, index):

        ime = self.names[int(index)]
        if ime in self.names:
            length = len(self.PhoneBook[ime])  # dobimo stevilo sip stevilk uporabnika
            sip = []
            for i in self.PhoneBook[ime]:
                sip.append(i)
            if length > 1:
                dialog2 = xbmcgui.Dialog()
                izbran = dialog2.select('Izberi stevilko za uporabnika ' + str(ime), sip)

                if izbran > -1:  # posljemo stevilko ki smo jo izbrali
                    dataPub = str(sip[izbran]).encode("ascii")
                    self.socketPub.send_multipart([b"CALL", dataPub])
                    dialog = xbmcgui.Dialog()
                    dialog.notification('Klicem:', str(dataPub), xbmcgui.NOTIFICATION_INFO, 5000)
            else:
                dataPub = str(sip[0]).encode("ascii")
                self.socketPub.send_multipart([b"CALL", dataPub])
                dialog = xbmcgui.Dialog()
                dialog.notification('Klicem:', str(dataPub), xbmcgui.NOTIFICATION_INFO, 5000)


gui = Gui('Phonebook')
gui.doModal()
del gui
xbmc.log("ADD-ON CLOSEE")

"""
 a = 0
        j = 1
        for i in data['contacts']:
            if a>6:
                a = 0
                j = j+1
            name = i['full_name']
            self.buttons.append(xbmcgui.ControlButton(-170 + a * 180, j*175, 150, 150, name, focusTexture=slika, noFocusTexture=slika,alignment=xbfont_truncated, textColor='0xFF0000FF', focusedColor='0xFFFF00FF'))
            # (x, y, width, height, label[, focusTexture, noFocusTexture, textOffsetX, textOffsetY, alignment, font, textColor, disabledColor, angle, shadowColor, focusedColor])
            self.labels.append(xbmcgui.ControlLabel(-170 + a * 170, j * 175 + 150, 150, 30, name))
            self.addControl(self.buttons[-1])  # last button in array
            self.addControl(self.labels[-1])
            a = a+1


        length = len(self.buttons)
        for i in range(0, length):
            self.buttons[i].controlRight(self.buttons[(i + 1) % length])  # i+1%10 will wrap the navigation)
            self.buttons[(i + 1) % length].controlLeft(self.buttons[i])"""