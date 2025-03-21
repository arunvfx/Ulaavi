"""
Summary:

This module provides utility functions for generating ffmpeg and ffprobe commands to handle various media processing
tasks, such as video conversion, image sequence conversion, image conversion, and frame extraction.
"""


def convert_video(source_file: str,
                  output_file: str,
                  resolutionX: int,
                  resolutionY: int,
                  fps: float = 24) -> list:
    """
    Generates a ffmpeg command to convert a video file to `.mov` format.

    :param source_file: The path to the source video file.
    :type source_file: str
    :param output_file: The path to the output `.mov` file.
    :type output_file: str
    :param resolutionX: The target width of the output video.
    :type resolutionX: int
    :param resolutionY: The target height of the output video.
    :type resolutionY: int
    :param fps: The target frames per second (FPS) of the output video. Defaults to 24.
    :type fps: float

    :return: A list of ffmpeg command arguments.
    :rtype: list[str]
    """
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
                           fps: float = 24) -> list:
    """
    Generates a ffmpeg command to convert an image sequence to `.mov` format.

    :param source_file: The path to the source image sequence (e.g., `file_0001-0100`).
    :type source_file: str
    :param output_file: The path to the output `.mov` file.
    :type output_file: str
    :param resolutionX: The target width of the output video.
    :type resolutionX: int
    :param resolutionY: The target height of the output video.
    :type resolutionY: int
    :param start_frame: The starting frame number of the image sequence.
    :type start_frame: int
    :param fps: The target frames per second (FPS) of the output video. Defaults to 24.
    :type fps: float

    :return: A list of ffmpeg command arguments.
    :rtype: list[str]
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


def convert_image(source_file: str, output_file: str, resolutionX: int, resolutionY: int) -> list:
    """
    Generates a ffmpeg command to convert an image file to `.png` format.

    :param source_file: The path to the source image file.
    :type source_file: str
    :param output_file: The path to the output `.png` file.
    :type output_file: str
    :param resolutionX: The target width of the output image.
    :type resolutionX: int
    :param resolutionY: The target height of the output image.
    :type resolutionY: int

    :return: A list of ffmpeg command arguments.
    :rtype: list[str]
    """
    return ["ffmpeg",
            "-i",
            source_file,
            "-vf",
            f"scale={resolutionX}:{resolutionY}:force_original_aspect_ratio=decrease",
            output_file,
            "-hide_banner"]


def extract_video_thumbnail_frame(source_file: str) -> list:
    """
    Generates a ffprobe command to extract metadata for the middle frame of a video.

    :param source_file: The path to the source video file.
    :type source_file: str

    :return: A list of ffprobe command arguments.
    :rtype: list[str]
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
    """
    Generates a ffmpeg command to extract a single frame from a video as an image.

    :param source_file: The path to the source video file.
    :type source_file: str
    :param output_file: The path to the output image file.
    :type output_file: str
    :param resolutionX: The target width of the output image.
    :type resolutionX: int
    :param resolutionY: The target height of the output image.
    :type resolutionY: int
    :param time: The timestamp (in seconds) of the frame to extract.
    :type time: float

    :return: A list of ffmpeg command arguments.
    :rtype: list[str]
    """
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
