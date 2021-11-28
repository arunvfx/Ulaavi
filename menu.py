import nuke
from main import *
from nukescripts import panels


menu = nuke.menu('Nuke').addMenu('thEdge')
menu.addCommand('Ulaavi', 'main()')


def loadWidgetPanel(widgetPP):
    widgetPP.addToPane()

widgetPP = widgetPanel()
nuke.menu('Pane').addCommand("Ulaavi", "loadWidgetPanel(widgetPP)")


# from nukescripts import panels
# pane = nuke.getPaneFor('Properties.1')
#
# panels.registerWidgetAsPanel('Elements', 'Ulaavi', 'uk.co.thefoundry.Elements', True).addToPane(pane)