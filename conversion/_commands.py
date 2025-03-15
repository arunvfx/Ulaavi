def convert_video(source_file: str,
                  output_file: str,
                  resolutionX: int,
                  resolutionY: int,
                  fps: float = 24):
    """
    Convert video file to mov conversion command.
    """
    return ["ffmpeg",
            "-i",
            source_file,
            "-vf",
            f"scale={resolutionX}:{resolutionY}:force_original_aspect_ratio=decrease",
            "-r",
            f"{fps}",
            output_file,
            "-hide_banner"]


def convert_image_sequence(source_file: str,
                           output_file: str,
                           resolutionX: int,
                           resolutionY: int,
                           start_frame: int,
                           fps: float = 24):
    """
    image sequence to mov conversion command.
    """
    _input = source_file.rsplit(' ', 1)[0]

    return ["ffmpeg",
            "-start_number",
            start_frame,
            "-i",
            _input,
            "-vf",
            f"scale={resolutionX}:{resolutionY}:force_original_aspect_ratio=decrease",
            "-r",
            f"{fps}",
            output_file,
            "-hide_banner"]


def convert_image(source_file: str, output_file: str, resolution: tuple):
    """
    image with any format to png conversion.
    """
    return ["ffmpeg",
            "-i",
            source_file,
            "-vf",
            f"scale={resolution[0]}:{resolution[1]}",
            output_file,
            "-hide_banner"]


def extract_video_thumbnail_frame(source_file: str):
    """
    Command to extract middle frame from video
    """
    return ["ffprobe",
            "-loglevel",
            "0",
            "-print_format",
            "json",
            "-show_format",
            "-show_streams",
            "-i",
            source_file,
            "-hide_banner"]


def extract_image_from_video(source_file: str, output_file: str, resolution: tuple, time: float) -> list:
    return ["ffmpeg",
            "-ss",
            f"{round(time)}",
            "-i",
            source_file,
            "-pix_fmt",
            "rgb24",
            "-frames",
            "1",
            "-vf",
            f"scale={resolution[0]}:{resolution[1]}:force_original_aspect_ratio=decrease",
            output_file,
            "-hide_banner"]
