from pandasqt.compat import QtCore, QtGui, QtWidgets, Qt, Slot, Signal

from pandasqt.models.DataFrameModel import DataFrameModel
from pandasqt.views.EditDialogs import AddAttributesDialog, RemoveAttributesDialog

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

class DataTableWidget(QtWidgets.QWidget):
    """A Custom widget with a TableView and a toolbar.

    This widget shall display all `DataFrameModels` and
    enable the editing of this (edit data, adding/removing,
    rows/columns).

    """
    def __init__(self, parent=None):
        """Constructs the object with the given parent.

        Args:
            parent (QObject, optional): Causes the objected to be owned
                by `parent` instead of Qt. Defaults to `None`.

        """
        super(DataTableWidget, self).__init__(parent)
        self.initUi()


    def initUi(self):
        """Initalizes the Uuser Interface with all sub widgets.

        """
        self.gridLayout = QtWidgets.QGridLayout(self)

        self.buttonFrame = QtWidgets.QFrame(self)
        self.buttonFrame.setMinimumSize(QtCore.QSize(250, 50))
        self.buttonFrame.setMaximumSize(QtCore.QSize(250, 50))
        self.buttonFrame.setFrameShape(QtWidgets.QFrame.NoFrame)

        self.buttonFrameLayout = QtWidgets.QGridLayout(self.buttonFrame)
        self.buttonFrameLayout.setContentsMargins(0, 6, 0, 6)

        self.editButton = QtWidgets.QToolButton(self.buttonFrame)
        self.editButton.setObjectName('editbutton')
        icon = QtGui.QIcon(QtGui.QPixmap(_fromUtf8(':/icons/document-edit.png')))

        self.editButton.setIcon(icon)

        self.addColumnButton = QtWidgets.QToolButton(self.buttonFrame)
        self.addColumnButton.setObjectName('addcolumnbutton')
        icon = QtGui.QIcon(QtGui.QPixmap(_fromUtf8(':/icons/edit-table-insert-column-right.png')))

        self.addColumnButton.setIcon(icon)

        self.addRowButton = QtWidgets.QToolButton(self.buttonFrame)
        self.addRowButton.setObjectName('addrowbutton')
        icon = QtGui.QIcon(QtGui.QPixmap(_fromUtf8(':/icons/edit-table-insert-row-below.png')))

        self.addRowButton.setIcon(icon)

        self.removeColumnButton = QtWidgets.QToolButton(self.buttonFrame)
        self.removeColumnButton.setObjectName('removecolumnbutton')
        icon = QtGui.QIcon(QtGui.QPixmap(_fromUtf8(':/icons/edit-table-delete-column.png')))

        self.removeColumnButton.setIcon(icon)

        self.removeRowButton = QtWidgets.QToolButton(self.buttonFrame)
        self.removeRowButton.setObjectName('removerowbutton')
        icon = QtGui.QIcon(QtGui.QPixmap(_fromUtf8(':/icons/edit-table-delete-row.png')))

        self.removeRowButton.setIcon(icon)

        self.buttons = [self.editButton, self.addColumnButton, self.addRowButton, self.removeColumnButton, self.removeRowButton]

        for index, button in enumerate(self.buttons):
            button.setMinimumSize(QtCore.QSize(36, 36))
            button.setMaximumSize(QtCore.QSize(36, 36))
            button.setIconSize(QtCore.QSize(36, 36))
            button.setCheckable(True)
            self.buttonFrameLayout.addWidget(button, 0, index, 1, 1)

        for button in self.buttons[1:]:
            button.setEnabled(False)

        self.tableView = QtWidgets.QTableView(self)
        self.tableView.setAlternatingRowColors(True)
        self.tableView.setSortingEnabled(True)

        self.gridLayout.addWidget(self.buttonFrame, 0, 0, 1, 1)
        self.gridLayout.addWidget(self.tableView, 1, 0, 1, 1)

        self.editButton.toggled.connect(self.enableEditing)
        self.addColumnButton.toggled.connect(self.showAddColumnDialog)
        self.addRowButton.toggled.connect(self.addRow)
        self.removeRowButton.toggled.connect(self.removeRow)
        self.removeColumnButton.toggled.connect(self.showRemoveColumnDialog)

    @Slot(bool)
    def enableEditing(self, enabled):
        """Enable the editing buttons to add/remove rows/columns and to edit the data.

        This method is also a slot.
        In addition, the data of model will be made editable,
        if the `enabled` parameter is true.

        Args:
            enabled (bool): This flag indicates, if the buttons
                shall be activated.

        """
        for button in self.buttons[1:]:
            button.setEnabled(enabled)
            if button.isChecked():
                button.setChecked(False)

        model = self.tableView.model()

        if model is not None:
            model.enableEditing(enabled)

    @Slot()
    def uncheckButton(self):
        """Removes the checked stated of all buttons in this widget.

        This method is also a slot.

        """
        for button in self.buttons[1:]:
            if button.isChecked:
                button.setChecked(False)

    @Slot(str, object, object)
    def addColumn(self, columnName, dtype, defaultValue):
        """Adds a column with the given parameters to the underlying model

        This method is also a slot.
        If no model is set, nothing happens.

        Args:
            columnName (str): The name of the new column.
            dtype (numpy.dtype): The datatype of the new column.
            defaultValue (object): Fill the column with this value.

        """
        model = self.tableView.model()

        if model is not None:
            model.addDataFrameColumn(columnName, dtype, defaultValue)

        self.addColumnButton.setChecked(False)

    @Slot(bool)
    def showAddColumnDialog(self, triggered):
        """Display the dialog to add a column to the model.

        This method is also a slot.

        Args:
            triggered (bool): If the corresponding button was
                activated, the dialog will be created and shown.

        """
        if triggered:
            dialog = AddAttributesDialog(self)
            dialog.accepted.connect(self.addColumn)
            dialog.rejected.connect(self.uncheckButton)
            dialog.show()

    @Slot(bool)
    def addRow(self, triggered):
        """Adds a row to the model.

        This method is also a slot.

        Args:
            triggered (bool): If the corresponding button was
                activated, the row will be appended to the end.

        """
        if triggered:
            model = self.tableView.model()
            model.addDataFrameRows()
            self.sender().setChecked(False)


    @Slot(bool)
    def removeRow(self, triggered):
        """Removes a row to the model.

        This method is also a slot.

        Args:
            triggered (bool): If the corresponding button was
                activated, the selected row will be removed
                from the model.

        """
        if triggered:
            model = self.tableView.model()
            selection = self.tableView.selectedIndexes()

            rows = [index.row() for index in selection]
            model.removeDataFrameRows(set(rows))
            self.sender().setChecked(False)

    @Slot(list)
    def removeColumns(self, columnNames):
        """Removes one or multiple columns from the model.

        This method is also a slot.

        Args:
            columnNames (list): A list of columns, which shall
                be removed from the model.

        """
        model = self.tableView.model()

        if model is not None:
            model.removeDataFrameColumns(columnNames)

        self.removeColumnButton.setChecked(False)

    @Slot(bool)
    def showRemoveColumnDialog(self, triggered):
        """Display the dialog to remove column(s) from the model.

        This method is also a slot.

        Args:
            triggered (bool): If the corresponding button was
                activated, the dialog will be created and shown.

        """
        if triggered:
            model = self.tableView.model()
            if model is not None:
                columns = model.dataFrameColumns()
                dialog = RemoveAttributesDialog(columns, self)
                dialog.accepted.connect(self.removeColumns)
                dialog.rejected.connect(self.uncheckButton)
                dialog.show()

    def setViewModel(self, model):
        """Sets the model for the enclosed TableView in this widget.

        Args:
            model (DataFrameModel): The model to be displayed by
                the Table View.

        """
        if isinstance(model, DataFrameModel):
            selectionModel = self.tableView.selectionModel()
            self.tableView.setModel(model)
            del selectionModel

    def view(self):
        """Gets the enclosed TableView

        Returns:
            QtGui.QTableView: A Qt TableView object.

        """
        return self.tableView


