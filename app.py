import os, sys, utils
from File import File
from FFmpegWorker import FFmpegWorker, FFProbeWorker
from CoreWidgets import *
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QLabel, 
    QVBoxLayout, QHBoxLayout, QPushButton, QButtonGroup, QFileDialog, QDialog, 
    QMessageBox, QRadioButton, QFrame, QProgressBar
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont


class ConversionDialog(QDialog):
    def __init__(self, file: File, parent=None):
        super().__init__(parent)

        self.setStyleSheet("""
            QLabel {
                margin: 0px;
                padding: 4px 8px;
                qproperty-alignment: AlignCenter;
            }
                           
            QLabel[class="section-header"] {
                margin-bottom: 0px;
                padding: 0px 0px;
                qproperty-alignment: AlignCenter;
            }
        """)

        self.setWindowTitle("Convert Format")
        self.setFixedSize(700, 250)

        # VBox holding HBox holding Vboxes
        primary_layout = QVBoxLayout()

        # Holds labels and radio buttons
        h_layout = QHBoxLayout()
        primary_layout.addLayout(h_layout)

        # Shows current format and details
        # Frame for left border
        left_frame = QFrame()
        left_frame.setFrameStyle(QFrame.Shape.Box)
        left_frame.setLineWidth(2)

        # VBox layout who's parent is the frame
        left_frame_layout = QVBoxLayout(left_frame)

        # Outermost left layout containing > frame > frame layout
        left_vlayout = QVBoxLayout()
        left_vlayout.addWidget(left_frame)
        


        # Shows conversion options as radio buttons
        # Frame for right border
        right_frame = QFrame()
        right_frame.setFrameStyle(QFrame.Shape.Box)
        right_frame.setLineWidth(2)

        # VBox layout who's parent is the frame
        right_frame_layout = QVBoxLayout(right_frame)

        # Outermost right layout containing > frame > frame layout
        right_vlayout = QVBoxLayout()
        right_vlayout.addWidget(right_frame)



        center_layout = QHBoxLayout()
        to_label = QLabel("To")
        font = to_label.font()
        font.setPointSize(14)
        to_label.setFont(font)
        center_layout.addWidget(to_label)


        h_layout.addLayout(left_vlayout)
        h_layout.addLayout(center_layout)
        h_layout.addLayout(right_vlayout)


        # Get file extension based on ffprobe data
        file_ext = utils.getFileFormatExt(file)


        # Left elements
        name_label = QLabel(f"Converting:\n {file.name}\n\nFrom: {file.f_format_raw['format_long_name']} ({file_ext})")
        font = name_label.font()
        font.setPointSize(12)
        name_label.setFont(font)

        name_label.setWordWrap(True)

        left_frame_layout.addWidget(name_label)


        # Audio Formats
        audio_compressed_formats = ["mp3", "aac/m4a", "ogg", "wma", "ac3/eac3"]
        audio_lossless_formats = ["flac", "wav", "aif/aiff", "pcm"]
        audio_section_label_headers = [QLabel("<u>Compressed Formats</u>"), QLabel("<u>Lossless Formats</u>")]

        # Video Formats
        modern_containers_video = ["mp4", "mkv", "mov", "webm"]
        legacy_web_formats_video = ["avi", "wmv/asf", "flv/f4v"]
        broadcast_media_formats_video = ["ts/m2ts/mts", "mpg/mpeg/vob"]
        animated_image_formats_video = ["gif", "apng"]
        video_section_label_headers = [QLabel("<u>Modern Formats</u>"), QLabel("<u>Legacy Formats</u>"), QLabel("<u>Broadcast Formats</u>"), QLabel("<u>Animated image Formats</u>")]
        
        is_audio = file_ext in audio_compressed_formats + audio_lossless_formats

        # Set format list according to media type
        format_list = [audio_compressed_formats, audio_lossless_formats] if is_audio else [modern_containers_video, legacy_web_formats_video, broadcast_media_formats_video, animated_image_formats_video]

        # Set headers according to media type
        section_label_headers = audio_section_label_headers if is_audio else video_section_label_headers

        # Right layout (radio buttons)
        self.button_group = QButtonGroup()
        
        for i, formats in enumerate(format_list):
            header_layout = QHBoxLayout()
            header_layout.addWidget(section_label_headers[i])
            right_frame_layout.addLayout(header_layout)
            
            for j, f_format in enumerate(formats):
                # Add HBox layouts of 3 columns for each set
                if j % 3 == 0:
                    if j > 0:
                        right_frame_layout.addLayout(temp_layout)

                    temp_layout = QHBoxLayout()
                    temp_layout.setAlignment(Qt.AlignmentFlag.AlignCenter) 

                # Create button and add it to group
                radio_button = QRadioButton(f_format)
                self.button_group.addButton(radio_button)

                # Set enabled, unless this is already its file type
                if f_format == file_ext:
                    radio_button.setEnabled(False)

                # Add the widget
                temp_layout.addWidget(radio_button)

            # Add last row in if it didn't complete
            if j % 3 != 0:
                right_frame_layout.addLayout(temp_layout)
                

        # Add cancel/ok bottom of primary layout
        button_layout = QHBoxLayout()
        btn_ok = QPushButton("OK")
        btn_ok.clicked.connect(self.submit)

        btn_cancel = QPushButton("Cancel")
        btn_cancel.clicked.connect(self.reject)

        button_layout.addWidget(btn_cancel)
        button_layout.addWidget(btn_ok)
        
        primary_layout.addLayout(button_layout)


        
        self.setLayout(primary_layout)


    def submit(self):
        """ Get the selected button, set that as the class variable, then call the dialog's 
         self.accept function to return to MainWindow convertFile """

        selected = self.button_group.checkedButton()

        if selected:
            self.selected_ext = selected.text().split("/")[0]

        self.accept()



class ProgressDialog(QDialog):
    """ Creates and shows progress of running FFmpeg worker """

    def __init__(self, parent, file, cmd):
        super().__init__(parent)

        self.file = file
        self.cmd = cmd

        self.setWindowTitle("Convert Format")
        self.setFixedSize(500, 200)

        primary_layout = QVBoxLayout()

        progress_bar = QProgressBar()
        progress_bar.setRange(0,100)

        primary_layout.addWidget(progress_bar)

        self.btn_done = QPushButton("OK")
        self.btn_done.clicked.connect(self.accept)
        self.btn_done.setEnabled(False) # Off by default

        primary_layout.addWidget(self.btn_done)
        

        self.setLayout(primary_layout)



        self.worker = FFmpegWorker(cmd=cmd, file=file)

        self.worker.progress.connect(progress_bar.setValue)
        # self.worker.log_line.connect(log_output.append)
        self.worker.finished.connect(self.onFinished)
        self.worker.error.connect(self.onError)

        self.worker.start()

        


    def onFinished(self):
        QMessageBox.information(self, "Success", f"File saved to: \n\n {self.cmd[-1]}")
        self.close()
        

    def onError(self, msg):
        QMessageBox.critical(self, "Error", msg)
        self.close()



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

        self.convert_action = edit_menu.addAction("Convert to...")
        self.convert_action.triggered.connect(lambda: self.convert_file(self.central_widget.file_selector_widget.getSelectedFile()))
        self.convert_action.setEnabled(False) # False by default. Enables when a file is uploaded


        # View
        view_menu = menu.addMenu("View")

        # Status bar (at the bottom)
        self.statusBar().showMessage("Ready")





    def convert_file(self, file: File):
        """ Opens dialogue to get desired file format, then kicks off FFmpeg to do the job """

        dialog = ConversionDialog(parent=self, file=file)
        

        if dialog.exec() == QDialog.DialogCode.Accepted:
            # Strip the old extension and add the new one
            newpath = f"{os.path.splitext(file.path)[0]}.{dialog.selected_ext}"

            # Create the command
            cmd = [
                "ffmpeg", "-i", file.path,
                 "-y", newpath
            ]

            # Pass the command to the progress dialog
            dialog = ProgressDialog(parent=self, file=file, cmd=cmd)

            if dialog.exec() == QDialog.DialogCode.Accepted:
                return




    

    def ffprobe_update(self, info):
        """ Receives the result signal (file info) emitted by the ffprobe thread, updates file accordingly, and adds the button for it """
        
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
            self.files = [(
                File (
                    name=os.path.basename(file_path),
                    path=file_path
                )
            )]
            self.n_files = 1

            self.convert_action.setEnabled(True)

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