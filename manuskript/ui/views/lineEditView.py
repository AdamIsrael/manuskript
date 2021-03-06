#!/usr/bin/env python
# --!-- coding: utf8 --!--
from PyQt5.QtCore import QMutex
from PyQt5.QtWidgets import QLineEdit

from manuskript.enums import Outline
from manuskript.functions import toString


class lineEditView(QLineEdit):
    def __init__(self, parent=None):
        QLineEdit.__init__(self, parent)
        self._column = Outline.title
        self._indexes = None
        self._index = None
        self._placeholderText = None
        self._updating = QMutex()

    def setModel(self, model):
        self._model = model
        self._model.dataChanged.connect(self.update)

    def setColumn(self, col):
        self._column = col

    def setCurrentModelIndex(self, index):
        self._indexes = None
        if index.isValid():
            if index.column() != self._column:
                index = index.sibling(index.row(), self._column)
            self._index = index
            self._model = index.model()
            # self.item = index.internalPointer()
            if self._placeholderText is not None:
                self.setPlaceholderText(self._placeholderText)
            self.textEdited.connect(self.submit)
            self.updateText()

    def setCurrentModelIndexes(self, indexes):
        self._indexes = []
        self._index = None

        for i in indexes:
            if i.isValid():
                if i.column() != self._column:
                    i = i.sibling(i.row(), self._column)
                self._indexes.append(i)

        self.textEdited.connect(self.submit)
        self.updateText()

    def submit(self):
        self._updating.lock()
        text = self.text()
        self._updating.unlock()

        if self._index:
            # item = self._index.internalPointer()
            if text != self._model.data(self._index):
                self._model.setData(self._index, text)

        elif self._indexes:
            for i in self._indexes:
                # item = i.internalPointer()
                if text != self._model.data(i):
                    self._model.setData(i, text)

    def update(self, topLeft, bottomRight):
        update = False

        if self._index:
            if topLeft.row() <= self._index.row() <= bottomRight.row():
                update = True

        elif self._indexes:
            for i in self._indexes:
                if topLeft.row() <= i.row() <= bottomRight.row():
                    update = True

        if update:
            self.updateText()

    def updateText(self):
        self._updating.lock()

        if self._index:
            # item = self._index.internalPointer()
            # txt = toString(item.data(self._column))
            txt = toString(self._model.data(self._index))
            if self.text() != txt:
                self.setText(txt)

        elif self._indexes:
            t = []
            same = True
            for i in self._indexes:
                # item = i.internalPointer()
                # t.append(toString(item.data(self._column)))
                t.append(toString(self._model.data(i)))

            for t2 in t[1:]:
                if t2 != t[0]:
                    same = False
                    break

            if same:
                self.setText(t[0])
            else:
                self.setText("")

                if not self._placeholderText:
                    self._placeholderText = self.placeholderText()

                self.setPlaceholderText(self.tr("Various"))

        self._updating.unlock()

