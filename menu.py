# -------------------------------- built-in Modules ----------------------------------

# ------------------------------- ThirdParty Modules ---------------------------------
import nuke
import nukescripts

# -------------------------------- Custom Modules ------------------------------------
from main import *

menu = nuke.menu('Nuke').addMenu('thEdge')
menu.addCommand('Ulaavi', 'main()')


class UlaaviPanel(nukescripts.PythonPanel):
    def __init__(self):
        super(UlaaviPanel, self).__init__(title="Ulaavi", id="uk.co.thefoundry.UlaaviPanel")
        self.pyKnob = nuke.PyCustom_Knob("", "", "UlaaviKnob()")
        self.addKnob(self.pyKnob)


class UlaaviKnob:

    def makeUI(self):
        self.ulaavi = Ulaavi()
        return self.ulaavi


ulaavi_wid = UlaaviPanel()
nuke.menu('Pane').addCommand("Ulaavi", "ulaavi_wid.addToPane()")
