import pandas as pd
import os
import pytest
import shutil
from mediafiletools.series_details import make_seriesdb, rename_episodes
from mediafiletools.movie_sort_to_df import make_moviedb
from mediafiletools.find_music_dupes import find_music_dupes


@pytest.fixture
def expected_files_dir(tmp_path):
    # Create temporary directory for expected files
    expected_files_dir = tmp_path / 'expected_files'
    expected_files_dir.mkdir()

    # Copy expected files to temporary directory
    expected_files = [
        'blank_episode_names.csv',
        'expected_abc_strip.csv',
        'expected_abc_strip.txt',
        'expected_abcsort.csv',
        'expected_abcsort.txt',
        'expected_folder_sort.csv',
        'expected_folder_sort.txt',
        'expected_folder_strip.csv',
        'expected_folder_strip.txt',
        'expected_ge_default.csv',
        'expected_ge_default.txt',
        'expected_ge_start_end.csv',
        'expected_ge_start_end.txt',
        'expected_list_default.txt',
        'expected_list_with_info.txt'
    ]

    for fname in expected_files:
        shutil.copy(os.path.join('tests', 'expected_files', fname),
                    expected_files_dir / fname)
    return expected_files_dir


def normalize_newlines(filepath):
    with open(filepath, 'r') as file:
        content = file.read()
    return content.replace('\r\n', '\n')


def compare_and_test_all(actual_ge_default_csv,
                         expected_csv_path,
                         expected_csv_name,
                         actual_txt,
                         expected_txt):
    """
    Testing utility to compare results.
    """
    # Compare csv files.
    df1 = pd.read_csv(actual_ge_default_csv)
    df2 = pd.read_csv(os.path.join(expected_csv_path, expected_csv_name))

    # Normalize newlines
    actual_txt_content = normalize_newlines(actual_txt)
    expected_txt_content = normalize_newlines(expected_txt)

    assert df1.to_dict() == df2.to_dict()
    assert actual_txt_content == expected_txt_content


def test_get_episode_df(request, expected_files_dir):
    """
    Test `get_episodes(imdb_id, filepath, output type='csv')`
    and `get_episodes(imdb_id, start=1, end=2, filepath, output type='txt')`
    There should be no diff in the output csv file.
    """
    # Get the path to the current test module
    test_dir = os.path.dirname(request.module.__file__)
    actual_files_dir = os.path.join(test_dir, 'actual_files')

    # Ensure the 'actual_files' directory exists
    os.makedirs(actual_files_dir, exist_ok=True)

    actual_ge_default_csv = os.path.join(actual_files_dir,
                                         "actual_ge_default.csv")
    actual_ge_default_txt = os.path.join(actual_files_dir,
                                         "actual_ge_default.txt")
    expected_ge_default_txt = expected_files_dir / "expected_ge_default.txt"

    # Create csv file to test.
    make_seriesdb("tt1220617",
                  filepath=str(actual_ge_default_csv))
    # Create txt file to test.
    make_seriesdb("tt1220617",
                  filepath=str(actual_ge_default_txt),
                  output_type="txt")

    compare_and_test_all(actual_ge_default_csv,
                         expected_files_dir,
                         "expected_ge_default.csv",
                         actual_ge_default_txt,
                         expected_ge_default_txt)


def test_get_episode_df_section(request, expected_files_dir):
    """
    Test `get_episodes(imdb_id, start=1, end=2, filepath, output type='csv')`
    and `get_episodes(imdb_id, start=1, end=2, filepath, output type='txt')`
    There should be no diff in the output csv file.
    """
    # Get the path to the current test module
    test_dir = os.path.dirname(request.module.__file__)
    actual_files_dir = os.path.join(test_dir, 'actual_files')

    # Ensure the 'actual_files' directory exists
    os.makedirs(actual_files_dir, exist_ok=True)

    actual_ge_start_end_csv = os.path.join(actual_files_dir,
                                           "actual_ge_start_end.csv")
    actual_ge_start_end_txt = os.path.join(actual_files_dir,
                                           "actual_ge_start_end.txt")
    expected_ge_start_end_txt = expected_files_dir / "expected_ge_start_end.txt"

    # Create csv file to test.
    make_seriesdb("tt1220617",
                  start=1,
                  end=2,
                  filepath=str(actual_ge_start_end_csv))
    # Create txt file to test.
    make_seriesdb("tt1220617",
                  start=1,
                  end=2,
                  filepath=str(actual_ge_start_end_txt),
                  output_type="txt")

    compare_and_test_all(actual_ge_start_end_csv,
                         expected_files_dir,
                         "expected_ge_start_end.csv",
                         actual_ge_start_end_txt,
                         expected_ge_start_end_txt)


def path_to_test_module(request, actual_files_dir, mediadir):
    # Get the path to the current test module
    test_dir = os.path.dirname(request.module.__file__)
    actual_files_dir = os.path.join(test_dir, actual_files_dir)
    media_dir = os.path.join(test_dir, mediadir)

    # Ensure the 'actual_files' directory exists
    os.makedirs(actual_files_dir, exist_ok=True)
    os.makedirs(media_dir, exist_ok=True)
    return actual_files_dir, media_dir


def test_write_episode_names(request, expected_files_dir):
    actual_files_dir, episodes_dir = path_to_test_module(request,
                                                         'actual_files',
                                                         'dummy_episodes')

    # The names to write to the episodes.
    csv_filepath = os.path.join(expected_files_dir, "expected_ge_default.csv")

    with open(os.path.join(expected_files_dir,
                           "expected_list_default.txt"), 'r') as file:
        lines = file.read().splitlines()

    expected_names = []
    season = []
    for line in lines:
        if line.strip() == "":
            if season:
                expected_names.append(season)
                season = []
        else:
            season.append(line.strip())
    if season:
        expected_names.append(season)  # Append the last season if not empty

    # Change file names to
    rename_episodes(episodes_dir, csv_path=csv_filepath)

    # Compare filenames
    for index, directory in enumerate(os.listdir(episodes_dir)):
        dir_path = os.path.join(episodes_dir, directory)
        actual_filenames = os.listdir(dir_path)
        assert sorted(actual_filenames) == sorted(expected_names)[index]

    # Reset the filenames.
    blank_csv_file_path = os.path.join(expected_files_dir,
                                       "blank_episode_names.csv")
    rename_episodes(episodes_dir, csv_path=blank_csv_file_path)


def test_write_episode_names_from_imdb(request, expected_files_dir):
    actual_files_dir, episodes_dir = path_to_test_module(request,
                                                         'actual_files',
                                                         'dummy_episodes')

    with open(os.path.join(expected_files_dir,
                           "expected_list_with_info.txt"), 'r') as file:
        lines = file.read().splitlines()

    expected_names = []
    season = []
    for line in lines:
        if line.strip() == "":
            if season:
                expected_names.append(season)
                season = []
        else:
            season.append(line.strip())
    if season:
        expected_names.append(season)  # Append the last season if not empty

    # Change file names to
    rename_episodes(episodes_dir, imdb_id="tt1220617", info="some info")

    # Compare filenames
    for index, directory in enumerate(os.listdir(episodes_dir)):
        dir_path = os.path.join(episodes_dir, directory)
        actual_filenames = os.listdir(dir_path)
        assert sorted(actual_filenames) == sorted(expected_names)[index]

    # Reset the filenames.
    blank_csv_file_path = os.path.join(expected_files_dir,
                                       "blank_episode_names.csv")
    rename_episodes(episodes_dir, csv_path=blank_csv_file_path)


def test_movies_dataframe_default(request, expected_files_dir):
    actual_files_dir, movies_dir = path_to_test_module(request,
                                                       'actual_files',
                                                       'dummy_movies')

    actual_abc_sort_csv = os.path.join(actual_files_dir, "actual_abcsort.csv")
    actual_abc_sort_txt = os.path.join(actual_files_dir, "actual_abcsort.txt")
    expected_abc_sort_txt = expected_files_dir / "expected_abcsort.txt"

    make_moviedb(movies_dir,
                 filepath=str(actual_abc_sort_csv),
                 output_type='csv')
    make_moviedb(movies_dir,
                 filepath=str(actual_abc_sort_txt),
                 output_type='txt')

    compare_and_test_all(actual_abc_sort_csv,
                         expected_files_dir,
                         "expected_abcsort.csv",
                         actual_abc_sort_txt,
                         expected_abc_sort_txt)


def test_movies_dataframe_folder(request, expected_files_dir):
    actual_files_dir, movies_dir = path_to_test_module(request,
                                                       'actual_files',
                                                       'dummy_movies')

    actual_folder_sort_csv = os.path.join(actual_files_dir,
                                          "actual_folder_sort.csv")
    actual_folder_sort_txt = os.path.join(actual_files_dir,
                                          "actual_folder_sort.txt")
    expected_folder_sort_txt = expected_files_dir / "expected_folder_sort.txt"

    make_moviedb(movies_dir,
                 sort_type='folder',
                 filepath=str(actual_folder_sort_csv),
                 output_type='csv')
    make_moviedb(movies_dir,
                 sort_type='folder',
                 filepath=str(actual_folder_sort_txt),
                 output_type='txt')

    compare_and_test_all(actual_folder_sort_csv,
                         expected_files_dir,
                         "expected_folder_sort.csv",
                         actual_folder_sort_txt,
                         expected_folder_sort_txt)


def test_movies_dataframe_strip(request, expected_files_dir):
    actual_files_dir, movies_dir = path_to_test_module(request,
                                                       'actual_files',
                                                       'dummy_movies')

    actual_abc_strip_csv = os.path.join(actual_files_dir,
                                        "actual_abc_strip.csv")
    actual_abc_strip_txt = os.path.join(actual_files_dir,
                                        "actual_abc_strip.txt")
    actual_folder_strip_csv = os.path.join(actual_files_dir,
                                           "actual_folder_strip.csv")
    actual_folder_strip_txt = os.path.join(actual_files_dir,
                                           "actual_folder_strip.txt")
    expected_abc_strip_txt = expected_files_dir / "expected_abc_strip.txt"
    expected_folder_strip_txt = \
        expected_files_dir / "expected_folder_strip.txt"

    make_moviedb(movies_dir,
                 filepath=str(actual_abc_strip_csv),
                 sort_type='abc',
                 output_type='csv',
                 strip=True)
    make_moviedb(movies_dir,
                 filepath=str(actual_abc_strip_txt),
                 sort_type='abc',
                 output_type='txt',
                 strip=True)
    make_moviedb(movies_dir,
                 filepath=str(actual_folder_strip_csv),
                 sort_type='folder',
                 output_type='csv',
                 strip=True)
    make_moviedb(movies_dir,
                 filepath=str(actual_folder_strip_txt),
                 sort_type='folder',
                 output_type='txt',
                 strip=True)

    # Compare csv files.
    df1 = pd.read_csv(actual_abc_strip_csv)
    df2 = pd.read_csv(os.path.join(expected_files_dir,
                                   "expected_abc_strip.csv"))
    df3 = pd.read_csv(actual_folder_strip_csv)
    df4 = pd.read_csv(os.path.join(expected_files_dir,
                                   "expected_folder_strip.csv"))

    # Normalize newlines
    actual_abc_txt_content = normalize_newlines(actual_abc_strip_txt)
    expected_abc_txt_content = normalize_newlines(expected_abc_strip_txt)
    actual_folder_txt_content = normalize_newlines(actual_folder_strip_txt)
    expected_folder_txt_content = normalize_newlines(expected_folder_strip_txt)

    assert df1.to_dict() == df2.to_dict()
    assert df3.to_dict() == df4.to_dict()
    assert actual_abc_txt_content == expected_abc_txt_content
    assert actual_folder_txt_content == expected_folder_txt_content


@pytest.fixture
def expected_dupe_files_dir(tmp_path):
    # Create temporary directory for expected files
    expected_dupe_files_dir = tmp_path / 'expected_dupe_files'
    expected_dupe_files_dir.mkdir()

    # Copy expected files to temporary directory
    expected_dupe_files = [
        'expected_default.csv',
        'expected_default.txt',
        'expected_flac.txt',
        'expected_flac.csv',
        'expected_mp3.txt',
        'expected_mp3.csv',
        'expected_wav.txt',
        'expected_wav.csv',
    ]

    for fname in expected_dupe_files:
        shutil.copy(os.path.join('tests', 'expected_dupe_files',
                                 fname), expected_dupe_files_dir / fname)
    return expected_dupe_files_dir


def test_music_dupe_default(request, expected_dupe_files_dir):
    actual_dupe_dir, musicdir = path_to_test_module(request,
                                                    'actual_dupe_files',
                                                    'dummy_music')

    actual_default_csv = os.path.join(actual_dupe_dir, "actual_default.csv")
    actual_default_txt = os.path.join(actual_dupe_dir, "actual_default.txt")
    expected_default_txt = expected_dupe_files_dir / "expected_default.txt"

    find_music_dupes(musicdir,
                     filepath=str(actual_default_csv),
                     output_type='csv')
    find_music_dupes(musicdir,
                     filepath=str(actual_default_txt),
                     output_type='txt')

    compare_and_test_all(actual_default_csv,
                         expected_dupe_files_dir,
                         "expected_default.csv",
                         actual_default_txt,
                         expected_default_txt)

    compare_and_test_all(actual_default_csv,
                         expected_dupe_files_dir,
                         "expected_default.csv",
                         actual_default_txt,
                         expected_default_txt)


def test_music_dupe_wav(request, expected_dupe_files_dir):
    actual_dupe_dir, musicdir = path_to_test_module(request,
                                                    'actual_dupe_files',
                                                    'dummy_music')

    actual_wav_csv = os.path.join(actual_dupe_dir, "actual_wav.csv")
    actual_wav_txt = os.path.join(actual_dupe_dir, "actual_wav.txt")
    expected_wav_txt = expected_dupe_files_dir / "expected_wav.txt"

    find_music_dupes(musicdir,
                     filter='wav',
                     filepath=str(actual_wav_csv),
                     output_type='csv')
    find_music_dupes(musicdir,
                     filter='wav',
                     filepath=str(actual_wav_txt),
                     output_type='txt')

    compare_and_test_all(actual_wav_csv,
                         expected_dupe_files_dir,
                         "expected_wav.csv",
                         actual_wav_txt,
                         expected_wav_txt)


def test_music_dupe_mp3(request, expected_dupe_files_dir):
    actual_dupe_dir, musicdir = path_to_test_module(request,
                                                    'actual_dupe_files',
                                                    'dummy_music')

    actual_mp3_csv = os.path.join(actual_dupe_dir, "actual_mp3.csv")
    actual_mp3_txt = os.path.join(actual_dupe_dir, "actual_mp3.txt")
    expected_mp3_txt = expected_dupe_files_dir / "expected_mp3.txt"

    find_music_dupes(musicdir,
                     filter='mp3',
                     filepath=str(actual_mp3_csv),
                     output_type='csv')
    find_music_dupes(musicdir,
                     filter='mp3',
                     filepath=str(actual_mp3_txt),
                     output_type='txt')

    compare_and_test_all(actual_mp3_csv,
                         expected_dupe_files_dir,
                         "expected_mp3.csv",
                         actual_mp3_txt,
                         expected_mp3_txt)


def test_music_dupe_flac(request, expected_dupe_files_dir):
    actual_dupe_dir, musicdir = path_to_test_module(request,
                                                    'actual_dupe_files',
                                                    'dummy_music')

    actual_flac_csv = os.path.join(actual_dupe_dir, "actual_flac.csv")
    actual_flac_txt = os.path.join(actual_dupe_dir, "actual_flac.txt")
    expected_flac_txt = expected_dupe_files_dir / "expected_flac.txt"

    find_music_dupes(musicdir,
                     filter='flac',
                     filepath=str(actual_flac_csv),
                     output_type='csv')
    find_music_dupes(musicdir,
                     filter='flac',
                     filepath=str(actual_flac_txt),
                     output_type='txt')

    compare_and_test_all(actual_flac_csv,
                         expected_dupe_files_dir,
                         "expected_flac.csv",
                         actual_flac_txt,
                         expected_flac_txt)
