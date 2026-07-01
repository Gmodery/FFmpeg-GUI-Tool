import os, subprocess, json, re
from File import File
from PyQt6.QtCore import QThread, pyqtSignal

class FFmpegWorker(QThread):
    """ Calls FFMpeg subprocess """
    progress = pyqtSignal(int) # 0 - 100
    log_line = pyqtSignal(str)
    finished = pyqtSignal()
    error = pyqtSignal(str)


    def __init__(self, cmd, file: File):
        super().__init__()
        self.cmd = cmd
        self._cancelled = False
        self.file = file


    def run(self):
        print(self.cmd)
        try:
            file_duration = float(self.file.f_format_raw["duration"])

            process = subprocess.Popen(
                self.cmd,
                stderr=subprocess.PIPE,
                stdout=subprocess.DEVNULL,
                text=True
            )

            for line in process.stderr:
                if self._cancelled:
                    process.kill()
                    return
                
                # Send to UI
                self.log_line.emit(line.strip())

                match = re.search(r"time=(\d+):(\d+):(\d+)", line)
                if match:
                    h, m, s = map(int, match.groups())
                    elapsed = h * 3600 + m * 60 + s
                    pct_complete = int(elapsed / file_duration * 100)
  
                    self.progress.emit(min(pct_complete, 100))

            process.wait()

            if process.returncode == 0:
                self.progress.emit(100)
                self.finished.emit()
            else:
                self.error.emit(f"FFmpeg exited with code {process.returncode}")



        except Exception as ex:
            print(str(ex))
            self.error.emit(str(ex))


    def cancel(self):
        self._cancelled = True



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

        self.result.emit(info)