import re
import os

from pymediainfo import MediaInfo
from series_details import get_episodes
from get_plot_test import extensions


def makenfo(dir_path, imdb_id=None, season=None, writing_app=None):
    """
    Creates an nfo template file by extracting the media info
    from video files. The resulting nfo file contains every
    episode from the season on one file.

    Example:
        makenfo(D:\\TV Shows\\Better Call Saul, imdb_id='tt3032476', season=1)

    Parameters
    ----------
    dir_path: str
        The directory of the show season.
    imdb_id: str, optional
        The IMDB id of the show (e.g. 'tt0903747')
    season: int, optional
        A single integer indicating the show
        season.
    writing_app: str, optional
        The program used to create the video file.
    """
    if writing_app is not None:
        writing_app = f"\tWriting application.......: {writing_app}\n"
    else:
        writing_app = ""
    plot_label = ""
    all_plots = [""]
    if imdb_id is not None:
        all_plots = get_plot(imdb_id, season=season)
        plot_label = "\n\tPlot Summary:\n\t-------------"
        if season is None:
            raise ValueError("Please enter the 'season' keyword to "
                             "specify the season number.")

    plot_index = 0
    for file in os.listdir(dir_path):
        if file.lower().endswith(tuple(extensions)):
            media_info = MediaInfo.parse(os.path.join(dir_path, file))

            for t in media_info.tracks:
                plot_summary = (
                    all_plots[0] if season is None else f"{all_plots[plot_index]}\n\n"
                )
                if t.track_type == "Video":
                    with open(os.path.join(dir_path, "Season.nfo"), "a") as nfo:
                        nfo.write(
                            (
                                "\n====== " + file + " =====\n\n"
                                "\tGeneral\n"
                                "\tTitle.....................: " + file + "\n"
                                f"\tBit rate..................: {t.bit_rate}\n"
                                "\tFirst aired...............: \n"
                                f"\tFormat....................: {t.format}\n"
                                f"\tFormat Version............: {t.format_version}\n"
                                f"\tFormat info...............: {t.format_info}\n"
                                "\tFile size.................:\n"
                                f"\tDuration..................: {_is_iterable(t.other_duration)} seconds\n"
                                f"\tBit rate..................: {t.bit_rate}\n"
                                f"\tEncoded date..............: {t.encoded_date}\n"
                                f"{writing_app}"
                                "\n"
                                "\tVideo\n"
                                f"\tID........................: {t.track_id}\n"
                                f"\tFormat....................: {_is_iterable(t.other_format)}\n"
                                f"\tCodec ID..................: {t.codec_id}\n"
                                f"\tCodec ID/Info.............: {t.codec_id_info}\n"
                                f"\tBit rate..................: {_is_iterable(t.other_bit_rate)}\n"
                                f"\tWidth.....................: {t.width}\n"
                                f"\tHeight....................: {t.height}\n"
                                f"\tDisplay aspect ratio......: {t.display_aspect_ratio}\n"
                                f"\tFrame rate mode...........: {t.frame_rate_mode}\n"
                                f"\tFrame rate................: {t.frame_rate}\n"
                                f"\tFrame count...............: {t.frame_count}\n"
                                f"\tChroma subsampling........: {t.chroma_subsampling}\n"
                                f"\tBit depth.................: {t.bit_depth}\n"
                            )
                        )
                elif t.track_type == "Audio":
                    with open(os.path.join(dir_path, "Season.nfo"), "a") as nfo:
                        nfo.write(
                            (
                                "\n"
                                "\tAudio\n"
                                f"\tID........................: {t.track_id}\n"
                                f"\tFormat....................: {t.format} {t.format_additionalfeatures}\n"
                                f"\tFormat/info...............: {t.format_info}\n"
                                f"\tCodec ID..................: {t.codec_id}\n"
                                f"\tBit rate mode.............: {t.bit_rate_mode}\n"
                                f"\tBit rate..................: {t.bit_rate}\n"
                                f"\tChannels..................: {t.channel_s}\n"
                                f"\tChannel layout............: {t.channel_layout}\n"
                                f"\tSampling rate.............: {t.sampling_rate}\n"
                                f"\tFrame rate................: {t.frame_rate}\n"
                                f"\tCompression mode..........: {t.compression_mode}\n"
                                f"\tTitle.....................: {t.title}\n"
                                f"\tLanguage..................: {t.language}\n"
                                f"\t{plot_label}\n"
                                f"\t{plot_summary}\n"
                            )
                        )
            plot_index += 1


def get_plot(imdb_id, season=None):
    """
    Fetches the plot summary of each episode from IMDB
    using BeautifulSoup4 and returns it in a list of str.

    Parameters
    ----------
    imdb_id: str
        The IMDB id of the show (e.g. 'tt0903747')
    season: int, optional
        A single integer indicating the show
        season.
    """
    all_plot_sums = []
    episode_details = get_episodes(imdb_id, start=season, end=season, from_nfo=True)
    for dump in episode_details:
        for eps in dump:
            descr = eps.find_all("div", class_="ipc-html-content-inner-div")
            plot_descr = re.search(r"<div.*?>(.*?)</div>", str(descr)).group(1)
            all_plot_sums.append(_format_plot(plot_descr))
    return all_plot_sums


def _format_plot(plot_str):
    """
    Helper function to insert line breaks in the
    plot description.
    """
    # Return sentences less than 90 characters
    # without formatting.
    if len(plot_str) <= 90:
        return plot_str

    plot_list = list(plot_str)
    nl = "\n\t"
    i = 90
    while i < len(plot_list):
        # Find the nearest space before or at the current position.
        while i < len(plot_list) and plot_list[i] != " ":
            i -= 1
        # Replace the space with a newline character.
        if i < len(plot_list):
            plot_list[i] = nl
        i += 91
    return "".join(plot_list)


def _is_iterable(value):
    """
    Make sure a Track value is an iterable before trying
    to index into it.
    """
    if hasattr(value, '__iter__'):
        return value[0]
    return value
