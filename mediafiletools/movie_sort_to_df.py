import os
import re
from string import ascii_uppercase

import pandas as pd
from .common import save_to_file, EXTENSIONS, _print_file_loc


def make_moviedb(dir_path, filepath=None, sort_type="abc",
                 output_type="csv", strip=False):
    """
    Create movie database from every movie file in the directory.

    `abc` sort sorts every file in alphabetical order.
    `folder`sort` sorts every file by directory and keeps the
    directory structure intact. The output file is created in the
    Home directory by default.

    Example:
        make_moviedb('/home/user/movies', sort_type='folder',
                     output_type='csv', strip=True)

    Parameters
    ----------
    dir_path: str
        The root directory of the movie files.
    filepath: str, optional
        The output directory for the txt/csv file. Default is
        /home/user.
    sort_type: str, default `abc`
        The two types of sort algorithms, `abc` and `folder`.
        `abc` sort produces an alphabetically sorted dataframe
        of every movie in the folder hierarchy organized under
        a heading of each letter.
        `folder` sort iterates through each folder separately and
        produces a dataframe of movies organized by folder.
    output_type: str, default `csv`
        Choose the resulting filetype/output. Valid types are `txt`,
        `csv`, `console`.
    strip: bool, default False
        Call `_format_filename()` with the `strip_all` kwarg
        to remove extraneous details from the file names.
    """
    if filepath is None:
        filepath = os.path.expanduser('~')
    sorted_movies = []

    if sort_type == "abc":
        for root, dirs, files in os.walk(dir_path):
            sorted_movies.extend(recursive_sort(root, strip=strip))
            del dirs[:]
        _create_abc_df(sorted_movies, filepath=filepath, output_type=output_type)

    elif sort_type == "folder":
        uncategorized = []
        for root, dirs, files in os.walk(dir_path):
            if root == dir_path:
                # All movie files in root folder get appended
                # to `movie_list` without sorting.
                for i in range(len(files)):
                    files[i] = _format_filename(files[i], strip_all=strip)
                uncategorized = ("Uncategorized", files)
            else:
                # Send each movie folder to `recursive_sort()` to be
                # put in their own separate list.
                sorted_movies.append(
                    (os.path.basename(root), recursive_sort(root, strip=strip))
                )
                del dirs[:]
        # Sort list of tuples ignoring case and append the
        # `Uncategorized` list at the end.
        sorted_movies.sort(key=lambda x: x[0].lower())
        sorted_movies.append(uncategorized)
        # A single movie in a folder is not a series; it will
        # be appended to the root folder list.
        for i in range(len(sorted_movies) - 1):
            # If the folder only has one movie,
            # Add it to the `Uncategorized` folder.
            if len(sorted_movies[i][1]) == 1:
                sorted_movies[-1][1].extend(sorted_movies[i][1])
        # Filter out the single movie folders from the final list.
        final_list = [i for i in sorted_movies if len(i[1]) >= 2]
        _create_folder_df(final_list, filepath=filepath, output_type=output_type)

    else:
        raise ValueError(
            f"{sort_type} is not a valid sort type. Valid keywords "
            f"are 'abc' and 'folder'."
        )


def recursive_sort(dir_path, movie_list=None, strip=False):
    """
    Recursively sorts every file in the `dir_path` tree.

    Parameters
    ----------
    dir_path: str
        The root directory of the movie files.
    movie_list: list, default None
        A list containing the sorted movie titles.
    strip: bool, default False
        Call `_format_filename` with the `strip_all` kwarg
        to remove extraneous details from the file names.
    """
    if movie_list is None:
        movie_list = []
    files_and_dirs = os.listdir(dir_path)
    files_and_dirs.sort(key=lambda x: (not os.path.isdir(os.path.join(dir_path, x)), x))
    for item in files_and_dirs:
        item_path = os.path.join(dir_path, item)
        if os.path.isfile(item_path) and item.lower().endswith(EXTENSIONS):
            movie_list.append(_format_filename(item, strip_all=strip))
        elif os.path.isdir(item_path):
            recursive_sort(item_path, movie_list, strip=strip)
    return movie_list


def _format_filename(filename, strip_all=False):
    """
    Helper function to clean up filenames.

    Parameters
    ----------
    filename: str
        The name of the movie file.
    strip_all: bool, default False
        Removes extraneous details from the file names.
    """
    if filename[0].islower():
        filename = filename.capitalize()
    if filename.lower().endswith(EXTENSIONS):
        if strip_all:
            # Ignore files with year at the beginning of the filename.
            match = re.search(r"^\d{4}", filename)
            if not match:
                # Strip everything after the year.
                match = re.search(r"^(.*?[(\[]?\d{4}[)\]]?)(?:[.\s]|$)", filename)
                if match:
                    # Extract the part up to and including the year.
                    return match.group(1).replace(".", " ")
        return os.path.splitext(filename)[0].replace(".", " ")
    return filename


def _create_abc_df(data, filepath=None, output_type=None):
    """
    Creates a dataframe for an `abc` sort.

    Parameters
    ----------
    data: list
        A list of every movie title.
    filepath: str, optional
        The directory path for the output csv file.
        Default is /home/user.
    output_type: str, default `csv`
        Choose the resulting filetype/output. Valid types are `txt`,
        `csv`, `console`.
    """
    rows = []
    alphanum = list(map(str, range(1, 10))) + list(ascii_uppercase)
    for char in alphanum:
        first = True
        for m in sorted(data):
            if m.startswith(char):
                data.remove(m)
                if first:
                    rows.append(("", ""))
                    rows.append((char, m))
                    first = False
                else:
                    rows.append(("", m))

    f_name = "Movie Database A - Z"
    # Output file location to console.
    _print_file_loc(output_type, filepath, f_name)

    save_to_file(
        pd.DataFrame(rows, columns=["A - Z", "Movie"]),
        filepath=filepath,
        output_type=output_type,
        fname=f_name,
    )


def _create_folder_df(data, filepath=None, output_type=None, strip=False):
    """
    Creates a dataframe for a `folder` sort.

    Parameters
    ----------
    data: list of tuple
        A list of every movie title.
    filepath: str, optional
        The directory path for the output csv file.
        Default is /home/user.
    output_type: str, default `scv`
        Choose the resulting filetype/output. Valid types are `txt`,
        `csv`, `console`.
    strip: bool, default False
        Call `_format_filename` with the `strip_all` kwarg
        to removes extraneous details from the file names.
    """
    rows = []
    for series, movies in data:
        series = _format_filename(series, strip_all=strip)
        first = True
        for m in sorted(movies, key=str.casefold):
            if first:
                rows.append(("", ""))
                rows.append((series, m))
                first = False
            else:
                rows.append(("", m))

    f_name = "Movie Database"
    # Output file location to console.
    _print_file_loc(output_type, filepath, f_name)

    save_to_file(
        pd.DataFrame(rows, columns=["Series", "Movie"]),
        filepath=filepath,
        output_type=output_type,
        fname=f_name,
    )
