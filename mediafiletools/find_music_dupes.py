import os

import pandas as pd
from tinytag import TinyTag
from .common import MUSIC_FORMAT, save_to_file, normalize_ld


class Song:
    def __init__(self, song_path):
        self.tag = TinyTag.get(song_path)
        self.format = os.path.splitext(song_path)[1][1:]
        self.matched = False
        self.identical = False
        self.score = 0

    def __str__(self):
        if self.tag.title.strip():
            return f"{self.tag.title} - {self.tag.artist}"
        return os.path.basename(self.tag._filename)


def get_songs(dir_path, music_list=None):
    """
    Recursively finds every audio file in the `dir_path` tree
    and sorts them into a list.
    Will raise a `tinytag` exception if tinytag can't parse
    the audio file.

    Parameters
    ----------
    dir_path: str
        The root directory of the audio files.
    music_list: list, default None
        A list containing the sorted audio titles.
        """
    if music_list is None:
        music_list = []
    files_and_dirs = os.listdir(dir_path)
    for item in files_and_dirs:
        item_path = os.path.join(dir_path, item)
        if os.path.isfile(item_path) and item.lower().endswith(MUSIC_FORMAT):
            try:
                music_list.append(Song(item_path))
            except Exception as e:
                print(f"{type(e).__name__} - {e} --> {item}")
        elif os.path.isdir(item_path):
            get_songs(item_path, music_list)
    return music_list


TITLE_POINTS = 10
ARTIST_POINTS = 6
LENGTH_POINTS = 3
FILE_SIZE_POINTS = 3
BITRATE_POINTS = 2
FORMAT_POINTS = 2
THRESHOLD = 16


def find_music_dupes(dir_path, filter=None, filepath=None,
                     output_type='csv', distance=None):
    """
    Compares every file in the list returned from `get_songs()`
    and finds duplicate audio files. Matches are calculated by
    the `_calculate_score` function which uses the file's
    metadata to find matches. The data is then output to
    either a csv file (default), text file or the console.

    The output file is created in the Home directory by default.

    Examples:
        find_music_dupes("C:/Users/user/Music")
        find_music_dupes("C:/Users/user/Music", filter="flac")

    Parameters
    ----------
    dir_path: str
        The root directory of the audio files.
    filter: str, optional
        Control the types of matches to view. Valid keywords
        are `identical`, 'wav', 'flac', 'ALAC', 'AIFF', 'ogg',
        'mp3', 'wma', 'm4a', 'AAC'
    filepath: str, optional
        The directory path for the output file.
        Default is /home/user.
    output_type: str, default `csv`
        Choose the resulting filetype/output. Valid types are `txt`,
        `csv`, `console`.
    distance: float, optional
        The strictness of the levenshtein function to find matches
        in song or artist names. A higher distance allows more leeway
        for differences in spelling and grammar and would match more files.
    """
    if filepath is None:
        filepath = os.path.expanduser('~')
    if distance is None:
        distance = 0.08

    matched = False
    music_list = get_songs(dir_path)
    matched_songs = []
    group = []

    # loop through each song
    for current_song in range(len(music_list)):
        for next_song in range(current_song + 1, len(music_list)):
            cur_song = music_list[current_song]
            nxt_song = music_list[next_song]

            # Compare song's tags to find a match.
            _calculate_score(cur_song, nxt_song, distance=distance)

            # If songs score reach a threshold, the songs match.
            if cur_song.score >= THRESHOLD:
                matched = True
                _mark_matched_songs(cur_song, nxt_song, group)
            else:
                music_list[current_song].score = 0

        # At the end of the loop, add the
        # current song if it matched anything.
        if matched:
            group.append(music_list[current_song])
            matched_songs.append(group)
        matched = False
        group = []

    _create_dataframe(matched_songs,
                      filter,
                      filepath=filepath,
                      output_type=output_type)


def _calculate_score(cur_song, nxt_song, distance=None):
    """
    The method by which matches are calculated. Song titles
    and artists are given the highest scores followed by
    track length and filesize.
    """
    tags = (cur_song.tag.title,
            nxt_song.tag.title,
            cur_song.tag.artist,
            nxt_song.tag.artist)

    # If tags exist in the file
    if not any(tag is None or tag.strip() == '' for tag in tags):
        if not cur_song.matched:
            if _check_name_match(cur_song.tag.title,
                                 nxt_song.tag.title,
                                 distance=distance):
                cur_song.score += TITLE_POINTS

            if _check_artist_match(cur_song.tag.artist,
                                   nxt_song.tag.artist,
                                   distance=distance):
                cur_song.score += ARTIST_POINTS

            if cur_song.format == nxt_song.format:
                cur_song.score += FORMAT_POINTS
            if cur_song.tag.bitrate == nxt_song.tag.bitrate:
                cur_song.score += BITRATE_POINTS
            if cur_song.tag.duration == nxt_song.tag.duration:
                cur_song.score += LENGTH_POINTS
            if cur_song.tag.filesize == nxt_song.tag.filesize:
                cur_song.score += FILE_SIZE_POINTS

    # If file has no tags, fallback on filename matches.
    else:
        cur_filename = os.path.basename(cur_song.tag._filename)
        nxt_filename = os.path.basename(nxt_song.tag._filename)
        if not cur_song.matched:
            if os.path.splitext(cur_filename)[0] in os.path.splitext(nxt_filename)[0]:
                cur_song.score += THRESHOLD
            if os.path.splitext(nxt_filename)[0] in os.path.splitext(cur_filename)[0]:
                cur_song.score += THRESHOLD


def _mark_matched_songs(song1, song2, group):
    # Mark song as matched, so it never gets compared again.
    song2.matched = True
    if song1.score >= 26:
        song1.identical = True
        song2.identical = True
    group.append(song2)
    song1.score = 0


def _check_name_match(name1, name2, distance=None):
    # Use levenshtein function if distance is set higher than 0
    # to account for minor misspellings of artist and song names.
    if distance > 0.0:
        if normalize_ld(name1, name2) <= distance:
            return True
    else:
        if name1 == name2:
            return True
    return False


def _check_artist_match(artist1, artist2, distance=None):
    # TODO add score based on multiple artist matches.
    # Split both artist strings into lists of individual artist names
    artists_list1 = artist1.split('/')
    artists_list2 = artist2.split('/')
    # Check if any artist in list 1 is in list 2 or vice versa
    for a1 in artists_list1:
        for a2 in artists_list2:
            return _check_name_match(a1, a2, distance=distance)


def _create_dataframe(data, filter=None, filepath=None, output_type=None):
    """
    Creates a dataframe out of all the resulting
    data.

    Parameters
    ----------
    data: list of list
        A list of every group of matched songs.
    filter: str, optional
        Control the types of matches to view. Valid keywords
        are `identical`, 'wav', 'flac', 'ALAC', 'AIFF', 'ogg',
        'mp3', 'wma', 'm4a', 'AAC'.
    filepath: str, optional
        The directory path for the output file.
        Default is /home/user.
    output_type: str, default `csv`
        Choose the resulting filetype/output. Valid types are
        `txt`, `csv`, `console`.
        """
    rows = []
    # Show all matches.
    if filter is None:
        for grp in data:
            rows.append(("", ""))
            for song in grp:
                _fill_df(song, rows)
        f_name = "All Music Dupes"
    # Only show identical matches.
    elif filter == 'identical':
        for grp in data:
            rows.append(("", ""))
            [_fill_df(song, rows) for song in grp if song.identical]
        f_name = "Identical Music Dupes"
    else:
        # Filter for different filetypes.
        for grp in data:
            if filter.lower() in MUSIC_FORMAT:
                matches = \
                    [song for song in grp if song.format == filter.lower()]
            else:
                raise ValueError(f"Supported keywords are "
                                 f"'identical', {MUSIC_FORMAT}")
            if len(matches) >= 2:
                rows.append(("", ""))
                [_fill_df(song, rows) for song in matches]

        f_name = f"{filter} Dupes"
    if output_type != 'console':
        print(f"\n{output_type} file located in: "
              f"{os.path.join(filepath, f_name)}.{output_type}")

    save_to_file(
        pd.DataFrame(rows, columns=["Song", "File Location"]),
        filepath=filepath,
        output_type=output_type,
        fname=f_name,
    )


def _fill_df(song, rows):
    file_path = os.path.dirname(song.tag._filename)
    filename = os.path.basename(song.tag._filename)
    rows.append((filename, file_path))
