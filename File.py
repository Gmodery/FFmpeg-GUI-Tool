class File():
    def __init__(self, name, path, streams=None, f_format=None):
        self.name = name
        self.path = path

        if streams:
            self.load_streams(streams)

        if f_format:
            self.load_format(f_format)
        

        self.button_format_name =  self.buttonFormatName()
        

    def load_streams(self, streams):
        # Raw list of dicts from ffprobe
        self.streams_raw = streams

        # Stream objects
        self.streams = [Stream(s) for s in streams]

    
    def load_format(self, f_format):
        self.f_format_raw = f_format


    def display_format_data(self):
        """ Returns format data, formatted """

        format_output = "==================== Format ====================\n"

        for key, val in self.f_format_raw.items():
            format_output += f"{key.replace('_', ' ').title():<20}: {val}\n"
        
        format_output += '\n'

        return format_output
    

    def display_stream_data(self):
        """ Returns all stream data concatenated """

        stream_output = ""

        for stream in self.streams:
            stream_output += stream.display_stream_data()

        return stream_output
    

    def display_full_data(self):
        """ Displays format and Stream data """

        return self.display_format_data() + self.display_stream_data()


    def buttonFormatName(self):
        return f"{self.name[:14]}...{self.name[-14:]}" if len(self.name) >= 28 else self.name
    



class Stream():
    def __init__(self, stream_item: dict):
        self.stream_item = stream_item

        self.index = stream_item["index"]
        self.codec_name = stream_item["codec_name"]
        self.codec_long_name = stream_item["codec_long_name"]
        self.codec_type = stream_item["codec_type"]

        self.disposition = stream_item["disposition"]
        self.tags = stream_item["tags"]


    def display_stream_data(self):
        """ Displays Stream data """

        s = f"==================== Stream {self.index} ====================\n\n"

        for key, val in self.stream_item.items():
            if key == "disposition" or key == "tags":
                continue

            s += f"{key.replace('_', ' ').title():<35}: {val}\n"

        s += "\nDisposition:\n"

        for key, val in self.disposition.items():
            s += f"\t{key.replace('_', ' ').title():<27}: {'Yes' if val == 1 else 'No'}\n"

        s += "\tTags:\n"

        for key, val in self.tags.items():
            s += f"\t{key.replace('_', ' ').title():<27}: {val}\n"

        s += "\n"

        return s
