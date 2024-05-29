import os
import re
from string import ascii_uppercase

import pandas as pd

extensions = ('.mp4', '.mkv', '.avi', 'ts', 'mov', '.wmv', '.flv', '.webm',
              '.m4v', '.mpg', '.3gp', '.3g2', '.ogv', '.vob', '.rm', '.rmvb',
              '.asf', '.m2ts', '.mxf', '.divx', '.xvid', '.f4v', '.mpe',
              '.mpe', '.drc', '.qt', '.svi', '.bik')


def sortmovies(dir_path, filepath=None, sorted_movies=None,
               sort_type='abc', output_type=None, strip=False):
    """
    Main sorting function. `abc` sort sorts every file in alphabetical
    order. `folder`sort` sorts every file by directory and keeps the
    directory structure intact. The output file is created in the
    current working directory by default.

    Example:
        sort_movies('D:\\Movies', sort_type='folder', output_type='csv', strip=True)

    Parameters
    ----------
    dir_path: str
        The root directory of the movie files.
    filepath: str, optional
        The output directory for the txt/csv file. Default is current
        working directory.
    sorted_movies: list, default None
        A list of every movie title found in the directory tree.
    sort_type: str, default `abc`
        The two types of sort algorithms, `abc` and `folder`.
        `abc` sort produces an alphabetically sorted dataframe
        of every movie in the folder hierarchy organized under
        a heading of each letter.
        `folder` sort iterates through each folder separately and
        produces a dataframe of movies organized by folder.
    output_type: str, default `txt`
        Choose the resulting filetype/output. Valid types are `txt`,
        `csv`, `console`.
    strip: bool, default False
        Call `_format_filename` with the `strip_all` kwarg
        to remove extraneous details from the file names.
    """
    if filepath is None:
        filepath = os.getcwd()
    if sorted_movies is None:
        sorted_movies = []
    if output_type is None:
        output_type = 'txt'

    if sort_type == 'abc':
        for root, dirs, files in os.walk(dir_path):
            sorted_movies.extend(_main_sort(root, strip=strip))
            del dirs[:]
        _create_abc_df(sorted_movies, filepath=filepath, output_type=output_type)

    elif sort_type == 'folder':
        uncategorized = []
        for root, dirs, files in os.walk(dir_path):
            if root == dir_path:
                # All movie files in root folder get appended
                # to `movie_list` without sorting.
                for i in range(len(files)):
                    files[i] = _format_filename(files[i], strip_all=strip)
                uncategorized = ('Uncategorized', files)
            else:
                # Send each movie folder to `make_list()` to be
                # put in their own separate list.
                sorted_movies.append((os.path.basename(root),
                                      _main_sort(root, strip=strip)))
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
        raise ValueError(f"{sort_type} is not a valid sort type. Valid keywords "
                         f"are 'abc' and 'folder'.")


def _main_sort(dir_path, movie_list=None, strip=False):
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
    files_and_dirs.sort(key=lambda x:
                        (not os.path.isdir(os.path.join(dir_path, x)), x))
    for item in files_and_dirs:
        item_path = os.path.join(dir_path, item)
        if os.path.isfile(item_path) and item.endswith(extensions):
            movie_list.append(_format_filename(item, strip_all=strip))
        elif os.path.isdir(item_path):
            _main_sort(item_path, movie_list, strip=strip)
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
    if filename.endswith(extensions):
        if strip_all:
            # Ignore files with year at the beginning of the filename.
            match = re.search(r'^\d{4}', filename)
            if not match:
                # Strip everything after the year.
                match = re.search(r'^(.*?[(\[]?\d{4}[)\]]?)(?:[.\s]|$)',
                                  filename)
                if match:
                    # Extract the part up to and including the year.
                    return match.group(1).replace('.', ' ')
        return os.path.splitext(filename)[0].replace('.', ' ')
    return filename


def _create_abc_df(data, filepath=None, output_type=None):
    """
    Creates a dataframe for an `abc` sort.

    Parameters
    ----------
    data: list of str
        A list of every movie title.
    filepath: str, optional
        The directory path for the output csv file.
        Defaults to current working directory.
    output_type: str, default `txt`
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
                    rows.append(('', ''))
                    rows.append((char, m))
                    first = False
                else:
                    rows.append(('', m))
    _save_to_file(pd.DataFrame(rows, columns=['A - Z', 'Movie']),
                  filepath=filepath, output_type=output_type)


def _create_folder_df(data, filepath=None, output_type=None, strip=False):
    """
    Creates a dataframe for a `folder` sort.

    Parameters
    ----------
    data: list of tuple
        A list of every movie title.
    filepath: str, optional
        The directory path for the output csv file.
        Defaults to current working directory.
    output_type: str, default `txt`
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
                rows.append(('', ''))
                rows.append((series, m))
                first = False
            else:
                rows.append(('', m))
    _save_to_file(pd.DataFrame(rows, columns=['Series', 'Movie']),
                  filepath=filepath, output_type=output_type)


def _save_to_file(df, filepath=None, output_type=None):
    """
    Helper function to save the resulting DataFrame to
    a file or to print to console.

    Parameters
    ----------
    df: DataFrame
        The resulting DataFrame of the movie database.
    filepath: str, optional
        The directory path for the output csv file.
        Defaults to current working directory.
    output_type: str, default `txt`
        Choose the resulting filetype/output. Valid types are `txt`,
        `csv`, `console`.
    """
    if output_type == 'txt':
        if filepath.endswith('.txt'):
            fpath = filepath
        else:
            fpath = os.path.join(filepath, 'Movie Database.txt')
        with open(fpath, 'w', encoding='utf-8') as txt:
            df.to_string(txt, index=False)
    elif output_type == 'csv':
        if filepath.endswith('.csv'):
            df.to_csv(filepath, index=False)
        else:
            df.to_csv(os.path.join(filepath, 'Movie Database.csv'), index=False)
    elif output_type == 'console':
        print(df.to_string())
    else:
        raise ValueError(f"{output_type} is not a valid output type. Valid "
                         f"keywords are 'txt', 'csv' or 'console'.")
