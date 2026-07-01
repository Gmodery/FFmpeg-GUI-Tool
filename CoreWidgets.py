from PyQt6.QtWidgets import (
    QLabel, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
    QButtonGroup, QSplitter, QScrollArea
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from File import File

class FileSelectorWidget(QWidget):
    """Left pane for selecting loaded files and signaling update of info to infowidget"""

    def __init__(self, info_widget):
        super().__init__()

        self.info_widget = info_widget

        self.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                margin: 0px;
                padding: 4px 8px;
                border: 1px solid #555;
                border-radius: 6px;
                text-align: left;
            }
                        
            QPushButton:checked {
                background-color: #6d28d9;
                margin: 0px;
                padding: 4px 8px;
                border: 1px solid #555;
                border-radius: 6px;
                text-align: left;
            }
                        
            QPushButton:hover { background-color: #6d28d9; }
        """)

        self.layout = QVBoxLayout()

        self.layout.setSpacing(0)
        self.layout.setContentsMargins(4,0,0,0)
        self.layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # Maps buttons to file objects
        self.button_file_map = {}

        self.button_group = QButtonGroup(self)
        self.button_group.setExclusive(True)

        # When button is clicked, send updateInfo the associated file object to update its text
        self.button_group.buttonClicked.connect(lambda btn: self.updateInfo(self.button_file_map[btn]))


        self.setLayout(self.layout)


    def updateInfo(self, file: File):
        """ Updates the info widget's info label's text accordingly """

        self.info_widget.info_label.setText(file.display_full_data())


    def getSelectedFile(self):
        for button in self.button_group.buttons():
            if button.isChecked():
                return self.button_file_map[button] 
            
        return None


    def removeAllButtons(self):
        for button in self.button_group.buttons().copy():
            self.button_group.removeButton(button)
            button.deleteLater()


    def addButton(self, file: File, selected=False):
        btn = QPushButton(file.button_format_name)
        
        btn.setCheckable(True)
        
        self.button_file_map[btn] = file

        # If preselected, set checked and call function to update info window
        if selected:
            btn.setChecked(True)

            self.updateInfo(file)


        self.button_group.addButton(btn)

        self.layout.addWidget(btn)



class InfoWidget(QWidget):
    """ Takes FileSelectorWidget in initialization so it can listen to changes in selections """

    def __init__(self):
        super().__init__()

        self.setStyleSheet("""
            QLabel {
                margin: 0px;
                padding: 4px 8px;
                border: 1px solid #555;
                qproperty-alignment: AlignLeft;
            }

            QLabel#file_data_label {
                margin: 0px;
                padding: 4px 8px;
                border: 0px;
                qproperty-alignment: AlignCenter;
            }               
            
            QPushButton:hover { background-color: #6d28d9; }
        """)

        # Simple VBox layout to display text
        layout = QVBoxLayout()

        file_data_label = QLabel("File Data")
        file_data_label.setObjectName("file_data_label")

        layout.addWidget(file_data_label)

        # Scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)

        # Make label class item so it can be modified
        self.info_label = QLabel()
        self.info_label.setWordWrap(True)
        self.info_label.setFont((QFont("Courier New", 10)))
        self.info_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)

        # Add the scroll widget to layout
        scroll.setWidget(self.info_label)
        layout.addWidget(scroll)

        layout.setSpacing(12)
        layout.setContentsMargins(0,0,0,12)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)


        # Now finally set this class' layout as the one just constructed
        self.setLayout(layout)



class CentralWidget(QWidget):
    def __init__(self):
        super().__init__()

        splitter = QSplitter(Qt.Orientation.Horizontal)

        self.info_widget = InfoWidget()
        self.file_selector_widget = FileSelectorWidget(info_widget=self.info_widget)

        splitter.addWidget(self.file_selector_widget)
        splitter.addWidget(self.info_widget)

        splitter.setSizes([200,600])

        layout = QHBoxLayout()

        layout.setSpacing(0)
        layout.setContentsMargins(0,0,0,0)
        
        layout.addWidget(splitter)

        self.setLayout(layout)