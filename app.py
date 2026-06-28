import os, sys
from File import File
from FFmpegWorker import FFmpegWorker, FFProbeWorker
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QLabel, QWidget, 
    QVBoxLayout, QHBoxLayout, QPushButton, QButtonGroup, 
    QSplitter, QFileDialog, QScrollArea, QDialog, 
    QDialogButtonBox, QRadioButton
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

# Widgets are UI elements (windows, dialogs, controls)
# Layouts position widgets
# Signals/slots are events/functions (e.g. button.clicked.connect(function) is a slot assigned to a signal (clicked)). Always use signals, don't call functions directly
# Threading: Classes can be extended with QThread to run separate from the UI
# QSS is CSS but specifically for PyQt6

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



class ConversionDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Convert Format")

        # VBox holding HBox holding Vboxes
        primary_layout = QVBoxLayout()

        # Holds labels and radio buttons
        layout = QHBoxLayout()
        primary_layout.addLayout(layout)

        layout.addWidget(QLabel("Example Text"))


        # Add to bottom of primary layout
        buttons = QDialogButtonBox.StandardButton.Cancel | QDialogButtonBox.StandardButton.Ok
        self.button_box = QDialogButtonBox(buttons)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)

        primary_layout.addWidget(self.button_box)


        
        self.setLayout(primary_layout)



class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.files = []
        self.n_files = 0

        self.setWindowTitle("Audio Editor Tool")
        self.setMinimumSize(800, 600)

        self.central_widget = CentralWidget()

        self.setCentralWidget(self.central_widget)
        

        # Menu Bar
        menu = self.menuBar()
        
        # File
        file_menu = menu.addMenu("File")

        open_single_action = file_menu.addAction("Load File")
        open_single_action.triggered.connect(self.load_single)

        open_many_action = file_menu.addAction("Load Multiple Files")
        open_many_action.triggered.connect(self.load_many)
        open_many_action.setEnabled(False) # Turn off for now
        

        # Edit
        edit_menu = menu.addMenu("Edit")

        convert_action = edit_menu.addAction("Convert to...")
        convert_action.triggered.connect(self.convert_file)


        # View
        view_menu = menu.addMenu("View")

        # Status bar (at the bottom)
        self.statusBar().showMessage("Ready")





    def convert_file(self):
        dialog = ConversionDialog(self)

        if dialog.exec() == QDialog.DialogCode.Accepted:
            print("Submitted")




    

    def ffprobe_update(self, info):
        """ Recieves the result signal (file info) emitted by the ffprobe thread, updates file accordingly, and adds the button for it """
        
        # Select the first file (should be the only one here at this point (this will change when multiple are uploaded))
        file = self.files[0]
        print("loading streams")
        try:
            file.load_streams(info['streams'])
        except KeyError:
            file.load_streams({"error": "No streams read"})

        print("loading format")
        try:
            file.load_format(info['format'])
        except KeyError:
            file.load_format({"error": "No streams read"})


        self.central_widget.file_selector_widget.removeAllButtons()
        self.central_widget.file_selector_widget.addButton(self.files[0], True)

        self.statusBar().showMessage(f"Loaded {file.path}")



    def load_single(self):
        """ Loads a single file specified by a path, then creates a file object and adds it to self.files.
            Also kicks off the FFProbeWorker to get the file data then updates it when finished. """

        file_filter = (
            "All Media (*.mp3 *.wav *.ogg *.flac *.m4a *.mp4 *.mkv *.avi *.mov *.wmv);;"
            "Audio Files (*.mp3 *.wav *.ogg *.flac *.m4a);;"
            "Video Files (*.mp4 *.mkv *.avi *.mov *.wmv)"
        )

        file_path = QFileDialog.getOpenFileName(
            self,
            "Select File",
            "",
            file_filter
        )[0]

        if file_path:

            # Set initial file data
            self.files.append(
                File (
                    name=os.path.basename(file_path),
                    path=file_path
                )
            )
            self.n_files = 1

            # Kick off ffprobe thread
            self.probe = FFProbeWorker(file_path)

            # Send result to ffprobe_update function
            self.probe.result.connect(self.ffprobe_update)
            self.probe.error.connect(lambda x: print(x))
            self.probe.start()

            

        else:
            self.statusBar().showMessage(f"No File Selected")
            

    def load_many(self):
        pass





app = QApplication(sys.argv)

app.setStyleSheet("""
    QMainWindow { background-color: #1e1e2e; }
    

""")


window = MainWindow()
window.show()

sys.exit(app.exec())