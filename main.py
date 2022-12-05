from direct.showbase.ShowBase import ShowBase
from direct.task import Task
from panda3d.core import loadPrcFile, VirtualFileSystem, Filename, Loader
from direct.gui.DirectGui import *
from PyQt5 import QtWidgets
import sys

'''Setup the Panda3D environment with our config file'''
loadPrcFile('main.prc')

class MusicApp(ShowBase):

    def __init__(self):
        ShowBase.__init__(self)
        base.musicManager.setConcurrentSoundLimit(1)
        self.mySound = None
        self.setupGUI()

    def setupGUI(self):
        background = Loader().loadSync(Filename('models/models/gui/entering-background'))
        backgroundNodePath = aspect2d.attachNewNode(background, 0)
        backgroundNodePath.setPos(0.0, 0.0, 0.0)
        backgroundNodePath.setScale(2.5)

        gui = loader.loadModel('models/models/gui/tt_m_gui_mat_mainGui')
        guiNextUp = gui.find('**/tt_t_gui_mat_nextUp')
        guiNextDown = gui.find('**/tt_t_gui_mat_nextDown')
        guiNextDisabled = gui.find('**/tt_t_gui_mat_nextDisabled')

        genericGUI = loader.loadModel('models/models/gui/ttr_m_gui_gen_buttons')
        self.scrubberBar = genericGUI.find('**/ttr_t_gui_gen_buttons_lineSkinny')
        self.scrubberButton = genericGUI.find('**/ttr_t_gui_gen_buttons_slider1')

        inventoryGUI = loader.loadModel('models/models/gui/ttr_m_gui_bat_inventoryGUI')
        browseButton = inventoryGUI.find('**/gagButton')
        browseButtonUp = browseButton.find('**/ttr_t_gui_bat_inventoryGUI_gagButton_base_up_card')
        browseButtonUpHighlight = browseButtonUp.find('**/ttr_t_gui_bat_inventoryGUI_gagButton_highlight_up_card')
        browseButtonUpHighlight.reparentTo(browseButtonUp)
        browseButtonUpHighlight.setColor(1, 1, 1)
        browseButtonDown = browseButton.find('**/ttr_t_gui_bat_inventoryGUI_gagButton_base_down_card')
        browseButtonDownHighlight = browseButtonDown.find('**/ttr_t_gui_bat_inventoryGUI_gagButton_highlight_down_card')
        browseButtonDownHighlight.reparentTo(browseButtonDown)
        browseButtonDownHighlight.setColor(1, 1, 1)
        browseButtonHover = browseButton.find('**/ttr_t_gui_bat_inventoryGUI_gagButton_base_hover_card')
        browseButtonHoverHighlight = browseButtonHover.find('**/ttr_t_gui_bat_inventoryGUI_gagButton_highlight_hover_card')
        browseButtonHoverHighlight.reparentTo(browseButtonHover)
        browseButtonHoverHighlight.setColor(1, 1, 1)


        self.playButton = DirectButton(relief=None, geom=((guiNextUp,
                                                           guiNextDown,
                                                           guiNextDisabled)), parent=aspect2d, state=DGG.DISABLED, scale=(1), pos=(0, 0, -0.7), command=self.setMusicStatus)
        self.browseButton = DirectButton(relief=None, geom=((browseButtonUp,
                                                            browseButtonDown,
                                                            browseButtonUp,
                                                            browseButtonHover)), parent=aspect2d, text='Browse', text_font=loader.loadFont('models/fonts/ImpressBT.ttf'), scale=(2, 4, 1), text_scale=(0.2, 0.4, 1), pos=(-1.7, 0, -0.7), text_pos=(0, -0.1, 0), geom_color=(0, 0.52, 0.86, 1), text_fg=(1, 1, 1, 1), command=self.selectFile)

        self.maxTime = OnscreenText(parent=aspect2d, text='', font=loader.loadFont('models/fonts/ImpressBT.ttf'), scale=0.25, pos=(1.75, -0.35), fg=(1, 1, 1, 1))
        self.currentTime = OnscreenText(parent=aspect2d, text='', font=loader.loadFont('models/fonts/ImpressBT.ttf'), scale=0.25, pos=(-1.75, -0.35), fg=(1, 1, 1, 1))

        self.scrubber = DirectSlider(range=(0,100), scale=(2, 1, 1), geom=self.scrubberBar, geom_scale=(0.5, 1, 1), relief=None, thumb_geom=self.scrubberButton, thumb_geom_scale=(0.25, 0.25, 0.25), thumb_frameSize=(-0.1, 0.1, -0.1, 0.1), thumb_relief=None, thumb_command=self.setTime, thumb_extraArgs=[True], value=0, pageSize=100, command=self.setTime, extraArgs=[False])
        self.scrubber.hide()

    def selectFile(self):
        if self.mySound:
            time = self.mySound.getTime()
            self.mySound.stop()
            self.mySound.setTime(time)
        app = QtWidgets.QApplication(sys.argv)
        filename, _ = QtWidgets.QFileDialog.getOpenFileName(None, 'Open File', r"", ("Audio Files (*.ogg *.mp3)"))
        if sys.platform == 'win32':
            if filename and not filename == '/':
                file = filename[0]
                file = filename.replace('%s:/' % (file), '/%s/' % (file.lower()))
                self.loadMusicFile(file)
                self.playButton['state'] = DGG.NORMAL
        if self.mySound:
            self.mySound.play()

    def pauseMusic(self):
        time = self.mySound.getTime()
        self.mySound.stop()
        self.mySound.setTime(time)

    def setMusicStatus(self):
        status = self.mySound.status()
        if status == self.mySound.PLAYING:
            self.pauseMusic()
        else:
            self.mySound.play()

    def calculateSoundLength(self):
        m, s = divmod(self.mySound.length(), 60)
        m = round(m)
        s = round(s)
        if s <= 9:
            self.maxTime['text'] = '%s:0%s' % (m, s)
        elif s == 60:
            m += 1
            self.maxTime['text'] = '%s:00' % (m)
        else:
            self.maxTime['text'] = '%s:%s' % (m, s)

    def calculateSoundTime(self, task):
        m, s = divmod(self.mySound.getTime(), 60)
        m = round(m)
        s = round(s)
        if s <= 9:
            self.currentTime['text'] = '%s:0%s' % (m, s)
        elif s == 60:
            m += 1
            self.currentTime['text'] = '%s:00' % (m)
        else:
            self.currentTime['text'] = '%s:%s' % (m, s)
        return Task.cont

    def setTime(self, status):
        if status:
            self.mySound.stop()
            self.mySound.setTime(self.scrubber['value'])
            self.mySound.play()

    def scrubberValueOverTime(self, task):
        self.scrubber['value'] = self.mySound.getTime()
        return Task.cont

    def loadMusicFile(self, filename):
        self.mySound = base.loader.loadMusic(filename)
        taskMgr.add(self.calculateSoundTime)
        self.calculateSoundLength()
        self.scrubber['range'] = (0,self.mySound.length())
        taskMgr.add(self.scrubberValueOverTime)
        self.scrubber.show()
        self.playMusic()

    def playMusic(self):
        self.mySound.setLoop(True)
        self.mySound.setVolume(1)
        self.mySound.play()

app = MusicApp()
try:
    app.run()
except SystemExit:
    exit()