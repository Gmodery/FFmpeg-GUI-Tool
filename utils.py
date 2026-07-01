from File import File

def getFileFormatExt(file: File):
    """ Gets the file extension for a given file using ffprobe data, rather than relying on extensions """

    # Maps ffprobe format name string to the right extension
    ffprobe_to_extension_map = {
        # --- AUDIO: LOSSLESS / UNCOMPRESSED ---
        "wav": "wav",
        "flac": "flac",
        "alac": "alac",
        "ape": "ape",
        "aiff": "aif/aiff",
        "pcm_s16le": "pcm",  # Common raw PCM identifier
        "pcm_s24le": "pcm",

        # --- AUDIO: CONVERTABLE / LOSSY ---
        "mp3": "mp3",
        "aac": "aac/m4a",
        "mov,mp4,m4a,3gp,3g2,mj2": "aac/m4a",  # MP4 container holding audio
        "ogg": "ogg",
        "opus": "ogg",                     # Modern Ogg audio codec
        "asf": "wma",                          # WMA files use the Microsoft ASF container
        "ac3": "ac3/eac3",
        "eac3": "ac3/eac3",
        "dts": "dts",

        # --- VIDEO: MODERN ---
        "matroska,webm": "mkv",                # Handled via fallback condition
        "mov,mp4,m4a,3gp,3g2,mj2": "mp4",      # Handled via fallback condition

        # --- VIDEO: LEGACY/WEB ---
        "avi": "avi",
        "flv": "flv/f4v",

        # --- VIDEO: BROADCAST ---
        "mpegts": "ts/m2ts/mts",
        "mpeg": "mpg/mpeg/vob",
        "mxf": "mxf",

        # --- VIDEO: ANIMATED IMAGES ---
        "gif": "gif",
        "apng": "apng"
    }

    fmt = file.f_format_raw['format_name']

    # determine if format is mkv or webm by checking video codec
    if fmt == "matroska,webm":
        codec = None
        
        for stream in file.streams:
            if stream.codec_type == "video":
                codec = stream.codec_name
                break

        if codec in ['vp8', 'vp9', 'av1', 'opus', 'vorbis']:
            return "webm"
        
        else:
            return "mkv"

        
    # determine if "mov,mp4,..." is mp4 or m4a as ffprobe renders both the same way
    # Return mp4 if a video stream exists
    if fmt == "mov,mp4,m4a,3gp,3g2,mj2":
        return "mp4" if any([s.codec_type == "video" for s in file.streams]) else "aac/m4a"
    

    return ffprobe_to_extension_map[fmt]