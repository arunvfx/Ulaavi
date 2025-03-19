def convert_video(source_file: str,
                  output_file: str,
                  resolutionX: int,
                  resolutionY: int,
                  fps: float = 24):
    """
    Convert video file to mov conversion command.
    """
    # output_file = output_file.replace('.mov', '.mp4')
    return ["ffmpeg",
            "-i",
            source_file,
            "-vcodec",
            "libx264",
            "-movflags",
            "faststart",
            "-pix_fmt",
            "yuv422p",
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
            "-vcodec",
            "libx264",
            "-pix_fmt",
            "yuv420p",
            "-vf",
            f"scale={resolutionX}:{resolutionY}:force_original_aspect_ratio=decrease",
            "-r",
            f"{fps}",
            output_file,
            "-hide_banner"]


def convert_image(source_file: str, output_file: str, resolutionX: int, resolutionY: int):
    """
    image with any format to png conversion.
    """
    return ["ffmpeg",
            "-i",
            source_file,
            "-vf",
            f"scale={resolutionX}:{resolutionY}:force_original_aspect_ratio=decrease",
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


def extract_image_from_video(source_file: str,
                             output_file: str,
                             resolutionX: int,
                             resolutionY: int,
                             time: float) -> list:
    return ["ffmpeg",
            "-ss",
            f"{time}",
            "-i",
            source_file,
            "-pix_fmt",
            "yuvj420p",
            "-frames",
            "1",
            "-vf",
            f"scale={resolutionX}:{resolutionY}:force_original_aspect_ratio=decrease",
            output_file,
            "-hide_banner"]
