# -*- coding: utf-8 -*-

import sys
sys.path.append("..")

import sip
sip.setapi('QString', 2)
sip.setapi('QVariant', 2)

from pandasqt.compat import QtCore, QtGui, QtWidgets, Qt, Slot, Signal

import sys
import pandas
import numpy


from pandasqt.models.DataFrameModel import DataFrameModel
from pandasqt.models.DataSearch import DataSearch
from pandasqt.views.CSVDialogs import CSVImportDialog, CSVExportDialog
from pandasqt.views._ui import icons_rc
from pandasqt.views.DataTableView import DataTableWidget
from pandasqt.views.CustomDelegates import createDelegate, DtypeComboDelegate
from util import getCsvData, getRandomData

class TestWidget(QtWidgets.QWidget):

    def __init__(self, parent=None):
        super(TestWidget, self).__init__(parent)
        self.resize(1680, 756)
        self.move(0, 0)


        self.df = pandas.DataFrame()
        #  init the data view's
        self.dataTableView = DataTableWidget(self)
        # self.dataTableView.setSortingEnabled(True)
        # self.dataTableView.setAlternatingRowColors(True)

        self.dataListView = QtWidgets.QListView(self)
        self.dataListView.setAlternatingRowColors(True)

        self.dataComboBox = QtWidgets.QComboBox(self)

        # make combobox to choose the model column for dataComboBox and dataListView
        self.chooseColumnComboBox = QtWidgets.QComboBox(self)

        self.buttonCsvData = QtWidgets.QPushButton("load csv data")
        self.buttonRandomData = QtWidgets.QPushButton("load random data")
        importDialog = CSVImportDialog(self)
        importDialog.load.connect(self.updateModel)
        self.buttonCsvData.clicked.connect(lambda: importDialog.show())
        self.buttonRandomData.clicked.connect(lambda: self.setDataFrame( getRandomData(rows=100, columns=100) ))

        self.exportDialog = CSVExportDialog(self)

        self.buttonCSVExport = QtWidgets.QPushButton("export to csv")
        self.buttonCSVExport.clicked.connect(self._exportModel)
        self.buttonLayout = QtWidgets.QHBoxLayout()
        self.buttonLayout.addWidget(self.buttonCsvData)
        self.buttonLayout.addWidget(self.buttonCSVExport)
        self.buttonLayout.addWidget(self.buttonRandomData)

        self.mainLayout = QtWidgets.QVBoxLayout()
        self.setLayout(self.mainLayout)
        self.mainLayout.addLayout(self.buttonLayout)

        self.mainLayout.addWidget(self.dataTableView)

        self.spinbox = QtWidgets.QSpinBox()
        self.mainLayout.addWidget(self.spinbox)
        self.spinbox.setMaximum(99999999999)
        self.spinbox.setValue(99999999999)

        self.rightLayout = QtWidgets.QVBoxLayout()
        self.chooseColumLayout = QtWidgets.QHBoxLayout()
        self.mainLayout.addLayout(self.rightLayout)
        self.rightLayout.addLayout(self.chooseColumLayout)
        self.chooseColumLayout.addWidget(QtWidgets.QLabel("Choose column:"))
        self.chooseColumLayout.addWidget(self.chooseColumnComboBox)
        self.rightLayout.addWidget(self.dataListView)
        self.rightLayout.addWidget(self.dataComboBox)

        self.tableViewColumnDtypes = QtWidgets.QTableView(self)
        self.rightLayout.addWidget(QtWidgets.QLabel('dtypes'))
        self.rightLayout.addWidget(self.tableViewColumnDtypes)
        self.buttonGoToColumn = QtWidgets.QPushButton("go to column")
        self.rightLayout.addWidget(self.buttonGoToColumn)
        self.buttonGoToColumn.clicked.connect(self.goToColumn)

        self.buttonSetFilter = QtWidgets.QPushButton("set filter")
        self.rightLayout.addWidget(self.buttonSetFilter)
        self.buttonSetFilter.clicked.connect(self.setFilter)
        self.buttonClearFilter = QtWidgets.QPushButton("clear filter")
        self.rightLayout.addWidget(self.buttonClearFilter)
        self.buttonClearFilter.clicked.connect(self.clearFilter)
        self.lineEditFilterCondition = QtWidgets.QLineEdit("freeSearch('am')")
        self.rightLayout.addWidget(self.lineEditFilterCondition)

        self.chooseColumnComboBox.currentIndexChanged.connect(self.setModelColumn)

        self.dataListView.mouseReleaseEvent = self.mouseReleaseEvent


    def setDataFrame(self, dataFrame):
        self.df = dataFrame
        dataModel = DataFrameModel()
        dataModel.setDataFrame(self.df)
        self.dataListView.setModel(dataModel)
        self.dataTableView.setViewModel(dataModel)
        self.dataComboBox.setModel(dataModel)

        for index, column in enumerate(dataModel.dataFrame().columns):
            dtype = dataModel.dataFrame()[column].dtype
            self.updateDelegates(index, dtype)
        #self.updateDelegates()

        # self.dataTableView.resizeColumnsToContents()

        # create a simple item model for our choosing combobox
        columnModel = QtGui.QStandardItemModel()
        for column in self.df.columns:
            columnModel.appendRow(QtGui.QStandardItem(column))
        self.chooseColumnComboBox.setModel(columnModel)

        self.tableViewColumnDtypes.setModel(dataModel.columnDtypeModel())
        self.tableViewColumnDtypes.horizontalHeader().setDefaultSectionSize(200)
        self.tableViewColumnDtypes.setItemDelegateForColumn(1, DtypeComboDelegate(self.tableViewColumnDtypes))
        dataModel.dtypeChanged.connect(self.updateDelegates)
        dataModel.changingDtypeFailed.connect(self.changeColumnValue)

    @Slot()
    def _exportModel(self):
        model = self.dataTableView.view().model()
        self.exportDialog.setExportModel(model)
        self.exportDialog.show()

    @Slot('QAbstractItemModel')
    def updateModel(self, model):
        self.dataListView.setModel(model)
        self.dataTableView.setViewModel(model)
        self.dataComboBox.setModel(model)

        self.tableViewColumnDtypes.setModel(model.columnDtypeModel())

    def setModelColumn(self, index):
        self.dataListView.setModelColumn(index)
        self.dataComboBox.setModelColumn(index)

    @Slot(int, object)
    def updateDelegates(self, column, dtype):
        print "update delegate for column", column, dtype
        # as documented in the setDelegatesFromDtype function
        # we need to store all delegates, so going from
        # type A -> type B -> type A
        # would cause a segfault if not stored.
        view = self.dataTableView.tableView
        createDelegate(dtype, column, view)
        # dlg = self.delegates or {}
        # self.delegates = setDelegatesFromDtype(self.dataTableView.tableView, dlg)
        # print dlg

    def goToColumn(self):
        print "go to column 7"
        index = self.dataTableView.view().model().index(7, 0)
        self.dataTableView.view().setCurrentIndex(index)

    def changeColumnValue(self, columnName, index, dtype):
        print "failed to change", columnName, "to", dtype
        print index.data(), index.isValid()
        self.dataTableView.view().setCurrentIndex(index)

    def setFilter(self):
        #filterIndex = eval(self.lineEditFilterCondition.text())
        search = DataSearch("Test", self.lineEditFilterCondition.text())
        self.dataTableView.view().model().setFilter(search)
        #raise NotImplementedError

    def clearFilter(self):
        self.dataTableView.view().model().clearFilter()

if __name__ == '__main__':

    app = QtWidgets.QApplication(sys.argv)
    widget = TestWidget()
    widget.show()

    widget.setDataFrame( getCsvData() )

    #widget.setDataFrame( getRandomData(2, 2) )

    app.exec_()