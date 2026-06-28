import os, subprocess, json
from PyQt6.QtCore import QThread, pyqtSignal

class FFmpegWorker(QThread):
    """ Takes a file or list of files to perform operations on
        e.g.

        worker = FFmpegWorker(file_path)

        worker
      
        """

    def __init__(self, f_input):
        """ 
        f_input can be either str or list 
        """
        super().__init__()

        self.input = f_input



    def convert_codec(self):
        """ Single input single output 


        """

        pass

    def run(self):
        pass





class FFProbeWorker(QThread):
    # Signals expose results from this worker to the main UI
    result = pyqtSignal(dict)
    error = pyqtSignal(str)
    
    def __init__(self, f_input):
        super().__init__()
        self.f_input = f_input

    def run(self):
        cmd = [
            "ffprobe", "-v", "error",
            "-print_format", "json",
            "-show_streams", "-show_format",
            self.f_input
        ]

        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode != 0:
            self.error.emit(result.stderr)
            return
        
        info = json.loads(result.stdout)

        with open('file.json', 'w') as f:
            json.dump(info, f)

        self.result.emit(info)