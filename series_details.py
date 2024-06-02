import os
import re

from bs4 import BeautifulSoup
from requests import get
import pandas as pd
from movie_sort_to_df import _save_to_file


def get_episodes(
    imdb_id,
    start=None,
    end=None,
    filepath=None,
    output_type="csv",
    from_write_ep=False,
    from_nfo=False,
):
    """
    Scrape the data of all the episodes in the given seasons and
    organize into a DataFrame. Default setting will scrape every
    episode from the first season until the last.
    The resulting columns are 'Season', 'Episode Number', 'Title',
    'Air date', 'Description'

    Example:
        1) get_episodes('tt0264235')
        2) get_episodes('tt0058805', start=1, end=3, filepath='C:\\Users\\user\\Desktop',
                        output_type='txt')

    Parameters
    ----------
    imdb_id: str
        The IMDB id of the show (e.g. 'tt0903747')
    start: int
        The season to start scraping from.
    end: int
        The last season to scrape.
    filepath: str, optional
        The output directory for the txt/csv file. Default is current
        working directory.
    output_type: str, default `csv`
        Choose the resulting filetype/output. Valid types are `txt`,
        `csv`, `console`.
    from_write_ep: bool, default False
        Flag to call `_extract_data()` and return DataFrame
        to `write_episode_names()` function.
    from_nfo: bool, default False
        Flag to return page_html values to`makenfo()` function.
    """
    if start is None:
        start = 1
    if filepath is None:
        filepath = os.getcwd()

    episodelist = []
    while True:
        season_url = rf"https://www.imdb.com/title/{imdb_id}/episodes/?season={start}"
        season = int(season_url[-1])
        response = get(
            season_url,
            headers={
                "User-Agent": "Mozilla/5.0",
                "Accept": "application/json",
                "Accept-Language": "en-US,en;q=0.5",
                "Accept-Encoding": "gzip, deflate",
                "Connection": "keep-alive",
                "Referer": "http://example.com",
                "Cache-Control": "no-cache",
            },
        )
        if response.status_code != 200:
            raise ValueError(
                f"Error: Received HTTP status code {response.status_code} "
                f"({response.reason}) for URL: {season_url}. Please check the URL "
                f"or IMDB ID and try again."
            )
        else:
            soup = BeautifulSoup(response.text, "html.parser")
            episode_details = soup.find_all("section", class_="sc-33cc047c-0 guTCiW")

            if from_nfo:
                return episode_details

            # End loop after reaching final season.
            end_loop = _reach_end_of_season(episode_details, start, end)
            _extract_data(
                episode_details, episodelist, season, from_write_ep=from_write_ep
            )
            start += 1

        if end_loop:
            if from_write_ep:
                return episodelist
            # Output a DataFrame to a txt/csv file or print to console.
            _save_to_file(
                pd.DataFrame(
                    episodelist,
                    columns=[
                        "Season",
                        "Episode Number",
                        "Title",
                        "Air date",
                        "Description",
                    ],
                ),
                filepath=filepath,
                output_type=output_type,
                fname="Episode Database",
            )
            break


def _reach_end_of_season(episode_details, start, end):
    """
    Determine when the scraper has reached the final
    season and then stop searching.
    """
    endloop = False
    # If start and end seasons were explicitly entered.
    if end is not None:
        if start == end:
            endloop = True
        return endloop
    else:
        # Check that no further seasons exist on IMDB.
        for ep in episode_details:
            if ep.find("a", class_="ipc-title-link-wrapper") is None:
                endloop = True
            return endloop


def write_episode_names(root_folder_path, imdb_id=None,
                        csv_path=None, info=None):
    """
    Overwrite the old file names of the show's episodes with the new
    names scraped from IMDB with `get_episodes`.
    Must be called from the show's root folder and will scan for
    folders with the following naming scheme:

    Series Name (root)
      |
      |-- Season 1
      |-- Season 2
      |-- Season 3
      |-- (etc.)

    Example:
        write_episode_names("C:\\Users\\user\\Desktop\\curb",
                            csv_path="C:\\Users\\user\\Desktop\\eps.csv",
                            info="1080p.x265)

    Parameters
    ----------
    root_folder_path: str
        The root directory of the series.
    imdb_id: str, optional
        The IMDB id of the show (e.g. 'tt0903747')
    csv_path: str, optional
        The csv file containing the series data.
    info: str, optional
        Any additional information about the file.
    """
    if info is not None:
        info = " - " + info
    else:
        info = ""

    if csv_path is not None:
        if csv_path.endswith(".csv"):
            df = pd.read_csv(csv_path)
        else:
            raise ValueError(f"{os.path.basename(csv_path)} must be a csv file.")

        # Ensure the CSV file has the required columns.
        if not all(
            col in df.columns
            for col in ["Season", "Episode Number", "Title", "Air date", "Description"]
        ):
            raise ValueError(
                "CSV file columns do not match pattern 'Season', "
                "'Episode Number', 'Title', 'Air date', 'Description'. Is it the correct file?"
            )

    else:
        df = pd.DataFrame(
            get_episodes(imdb_id, from_write_ep=True),
            columns=["Season", "Episode Number", "Title"],
        )

    def _rename_files(file_name, ext):
        # Helper function.
        for old_name, (_, row) in zip(file_name, group.iterrows()):
            episode_name = "".join(c for c in row["Title"] if c not in r'\/:*?"<>|')
            episode_num = row["Episode Number"]
            new_name = (
                f"S{season:02d}E{int(episode_num):02d} - {episode_name}{info}.{ext}"
            )
            old_file_path = os.path.join(season_folder, old_name)
            new_file_path = os.path.join(season_folder, new_name)
            os.rename(old_file_path, new_file_path)
            print(f"Renamed: {old_name} -> {new_name}")

    # Group the data by season
    grouped = df.groupby("Season")
    for season, group in grouped:
        # Look for folders titled 'Season X'. Change depending on naming scheme.
        season_folder = os.path.join(root_folder_path, f"Season {season}")

        if not os.path.exists(season_folder):
            print(f"Season folder {season_folder} does not exist. Skipping...")
            continue

        # The keys in this dict are named after the file types because they
        # are passed as the file extensions in the `_rename_files(v, k)` function call.
        files = {
            "mp4": [f for f in os.listdir(season_folder) if f.endswith(".mp4")],
            "mkv": [f for f in os.listdir(season_folder) if f.endswith(".mkv")],
            "avi": [f for f in os.listdir(season_folder) if f.endswith(".avi")],
            "srt": [f for f in os.listdir(season_folder) if f.endswith(".srt")],
            "nfo": [f for f in os.listdir(season_folder) if f.endswith(".vtt")],
        }

        ep_num = max(files, key=lambda k: len(files[k]))
        if len(files[ep_num]) != len(group):
            print(
                f"The number of video files in {season_folder} does not match the number "
                f"of rows in the CSV for season {season}."
            )
            continue

        for k, v in files.items():
            _rename_files(v, k)


def _extract_data(episode_details, episodelist,
                  season, from_write_ep=False):
    """
    Helper function to extract the useful information from the IMDB tags.
    """
    for dump in episode_details:
        for eps in dump:
            title = eps.find_all("div", class_="ipc-title__text")
            # Get episode number and title by default.
            ep_str = re.search(r"\bE(\d+)\b", str(title)).group(1)
            title_str = re.search(r">[^∙]*∙\s*(.*?)<", str(title)).group(1)
            episode_data = [season, ep_str, title_str]
            if not from_write_ep:
                # If called explicitly, also get all details about episodes.
                airdate = eps.find_all("span", class_="sc-ccd6e31b-10 fVspdm")
                descr = eps.find_all("div", class_="ipc-html-content-inner-div")
                airdate_str = re.search(
                    r"\b\w{3}, \w{3} \d{1,2}, \d{4}\b", str(airdate)
                ).group(0)
                descr_str = re.search(r"<div.*?>(.*?)</div>", str(descr)).group(1)
                episode_data.extend([airdate_str, descr_str])
            episodelist.append(episode_data)
