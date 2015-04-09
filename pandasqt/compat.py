import logging
log = logging.getLogger(__name__)

import sip
try:
    sip.setapi('QString', 2)
    sip.setapi('QVariant', 2)
except ValueError, e:
    log.error(e)

QT_WRAPPER = None

try:
    from PyQt5 import QtCore as QtCore_
    from PyQt5 import QtGui as QtGui_
    from PyQt5 import QtWidgets as QtWidgets_
    from PyQt5.QtCore import pyqtSlot as Slot, pyqtSignal as Signal
    QT_WRAPPER = 'PyQt5'
except ImportError, e:
    try:
        from PyQt4 import QtCore as QtCore_
        from PyQt4 import QtGui as QtGui_
        from PyQt4 import QtGui as QtWidgets_
        from PyQt4.QtCore import pyqtSlot as Slot, pyqtSignal as Signal
        QT_WRAPPER = 'PyQt4'
    except ImportError, e:
        from PySide import QtCore as QtCore_
        from PySide import QtGui as QtGui_
        from PySide import QtGui as QtWidgets_
        from PySide.QtCore import Slot, Signal
        QT_WRAPPER = 'PySide'


QtCore = QtCore_
QtGui = QtGui_
QtWidgets = QtWidgets_
Qt = QtCore_.Qt

__all__ = ['QtCore', 'QtGui', 'Qt', 'Signal', 'Slot', 'QtWidgets']


