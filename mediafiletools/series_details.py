import logging
import os
import re

from bs4 import BeautifulSoup
from requests import get
import pandas as pd
from .common import save_to_file, EXTENSIONS, _print_file_loc, clean_filename


# Keep log of results of `rename_episodes`.
log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'log')
os.makedirs(log_dir, exist_ok=True)

log_file = os.path.join(log_dir, 'rename.log')
logging.basicConfig(filename=log_file, level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')


def make_seriesdb(imdb_id, start=None, end=None, filepath=None,
                  output_type="csv", from_write_ep=False, final=False):
    """
    Scrape the data of all the episodes in the given seasons and
    organize into a DataFrame. Default setting will scrape every
    episode from the first season until the last.
    The resulting columns are 'Season', 'Episode Number', 'Title',
    'Air date', 'Description'

    Example:
        1) make_seriesdb('tt0264235')
        2) make_seriesdb('tt0058805', start=1, end=3,
                         filepath='home/user/shows', output_type='txt')

    Parameters
    ----------
    imdb_id: str
        The IMDB id of the show (e.g. 'tt0903747')
    start: int
        The season to start scraping from.
    end: int
        The last season to scrape.
    filepath: str, optional
        The output directory for the txt/csv file.
        Default is home/user.
    output_type: str, default `csv`
        Choose the resulting filetype/output. Valid types are `txt`,
        `csv`, `console`.
    from_write_ep: bool, default False
        Flag to call `_extract_data()` and return DataFrame
        to `write_episode_names()` function.
    final: bool, default False
        If True, stops scraping after the final season of
        a series has been reached.
    """
    if start is None:
        start = 1
    if filepath is None:
        filepath = os.path.expanduser('~')

    episodelist = []
    while True:
        season_url = rf"https://www.imdb.com/title/{imdb_id}/episodes/?season={start}"
        season = int(start)
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
            episode_details = soup.find_all("section", class_=re.compile("sc-56c21e9b-0.*"))
            # Check for absense of 'Next Season' element in soup.
            if not soup.find('button', {'id': 'next-season-btn'}):
                final = True

            # End loop after reaching final season.
            end_loop = _reach_end_of_season(start, end, final=final)
            _extract_data(
                episode_details, episodelist, season, from_write_ep=from_write_ep
            )
            start += 1

        if end_loop:
            if from_write_ep:
                # Return episodelist to `rename_episodes()`
                return episodelist

            f_name = clean_filename(soup.find('h2').text.strip())
            # Output file location to console.
            _print_file_loc(output_type, filepath, f_name)

            # Output a DataFrame to a txt/csv file or print to console.
            save_to_file(
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
                fname=f_name,
            )
            break


def _reach_end_of_season(start, end, final=False):
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
    else:  # Default setting to scrape all seasons.
        # Check that no further seasons exist on IMDB.
        if final:
            endloop = True
        return endloop


def rename_episodes(root_folder_path, info=None, **kwargs):
    """
    Overwrite the old file names of the show's episodes with the new
    names scraped from IMDB with `make_seriesdb()`.
    Must be called from the show's root folder and will scan for
    folders with the following naming scheme:

    <Series Name> (root)
      |
      |-- Season 1
      |-- Season 2
      |-- Season 3
      |-- (etc.)

    Example:
        rename_episodes("home/user/Some Show",
                         csv_path="home/user/eps.csv",
                         info="1080p.x265")

    Parameters
    ----------
    root_folder_path: str
        The root directory of the series.
    info: str, optional
        Any additional information about the file.
    **kwargs : dict, optional
        Arbitrary keyword arguments.
        - imdb_id: str, optional
            The IMDB id of the show (e.g. 'tt0903747'). If passed,
            will rename the episodes with the names scraped from
            IMDB.
        - csv_path: str, optional
            The csv file containing the series data. If passed,
            will rename the episodes from the input csv file.
    Raises
    ------
    ValueError
        If neither 'imdb_id' nor 'csv_path' is provided in the keyword arguments.
    """
    if info is not None:
        info = " - " + info
    else:
        info = ""

    if 'csv_path' in kwargs:
        if kwargs['csv_path'].endswith(".csv"):
            df = pd.read_csv(kwargs['csv_path'])
        else:
            raise ValueError(f"{os.path.basename(kwargs['csv_path'])} must be a csv file.")
        # Ensure the CSV file has the required columns.
        if not all(
            col in df.columns
            for col in ["Season", "Episode Number", "Title", "Air date", "Description"]
        ):
            raise ValueError(
                "CSV file columns do not match pattern 'Season', "
                "'Episode Number', 'Title', 'Air date', 'Description'. Is it the correct file?"
            )
    elif 'imdb_id' in kwargs:
        df = pd.DataFrame(
            make_seriesdb(kwargs['imdb_id'], from_write_ep=True),
            columns=["Season", "Episode Number", "Title"],
        )
    else:
        raise ValueError("At least one of 'imdb_id' or 'csv_path' must be provided.")

    def _rename_files(file_name):
        # Helper function.
        for old_name, (_, row) in zip(file_name, group.iterrows()):
            episode_name = "".join(c for c in row["Title"] if c not in r'\/:*?"<>|')
            episode_num = row["Episode Number"]
            file_ext = os.path.splitext(old_name)[1]
            new_name = (
                f"S{season:02d}E{int(episode_num):02d} - {episode_name}{info}{file_ext}"
            )
            old_file_path = os.path.join(season_folder, old_name)
            new_file_path = os.path.join(season_folder, new_name)

            try:
                os.rename(old_file_path, new_file_path)
                logging.info(f"Renamed: {old_name} -> {new_name}")
                print(f"Renamed: {old_name} -> {new_name}")
            except Exception as e:
                logging.error(f"Error renaming {old_name}: {str(e)}")
                print(f"Error renaming {old_name}: {str(e)}")

    # Group the data by season
    grouped = df.groupby("Season")
    for season, group in grouped:
        # Look for folders titled 'Season X'. Change depending on naming scheme.
        # TODO add way of handling other naming schemes.
        season_folder = os.path.join(root_folder_path, f"Season {season}")
        if not os.path.exists(season_folder):
            print(f"Season folder {season_folder} does not exist. Skipping...")
            continue

        # Loop through the folder and add each file name to the lists.
        # Separate lists for video files and sub files.
        files = {
            "video": [f for f in os.listdir(season_folder) if f.lower().endswith(EXTENSIONS)],
            "subs": [f for f in os.listdir(season_folder) if f.lower().endswith((".srt", ".vtt"))]
        }
        ep_num = max(files, key=lambda k: len(files[k]))
        if len(files[ep_num]) != len(group):
            print(
                f"The number of video files in {season_folder} does not match the number "
                f"of rows in the CSV for season {season}."
            )
            continue

        for v in files.values():
            _rename_files(v)


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
                airdate = eps.find('span', class_='sc-f2169d65-10')
                date_text = airdate.get_text(strip=True) if airdate else None
                descr = eps.find_all("div", class_='ipc-html-content-inner-div')
                descr_str = re.search(r"<div.*?>(.*?)</div>", str(descr)).group(1)
                episode_data.extend([date_text, descr_str])
            episodelist.append(episode_data)
