import os
import re

from bs4 import BeautifulSoup
from requests import get
import pandas as pd


def get_episodes(url, start, end, show=False):
    """
    Scrape the data of all the episodes in the given seasons and
    organize into a csv file.
    The resulting columns are 'Season', 'Episode Number', 'Title', 'Airdate', 'Description'

    Example:
        get_episodes(r'https://www.imdb.com/title/tt0264235/episodes?season=', 1, 7)

    Parameters
    ----------
    url: str
        The url of the IMDB season page.
    start: int
        The season to start scraping from.
    end: int
        The last season to scrape from.
    show: bool, default False
        Print the data to stout instead of creating csv.
    """
    episodelist = []
    # Range of seasons + 1
    for s in range(start, end + 1):
        response = get(url + str(s),
                       headers={'User-Agent': 'Mozilla/5.0'})
        page_html = BeautifulSoup(response.text, 'html.parser')
        episode_details = page_html.find_all('section', class_='sc-33cc047c-0 guTCiW')

        for dump in episode_details:
            for eps in dump:
                title = eps.find_all('div', class_='ipc-title__text')
                airdate = eps.find_all('span', class_='sc-ccd6e31b-10 fVspdm')
                descr = eps.find_all('div', class_='ipc-html-content-inner-div')
                episode_data = [s,
                                re.search(r'\bE(\d+)\b', str(title)).group(1),
                                re.search(r'>[^∙]*∙\s*(.*?)<', str(title)).group(1),
                                re.search(r'\b\w{3}, \w{3} \d{1,2}, \d{4}\b', str(airdate)).group(0),
                                re.search(r'<div.*?>(.*?)</div>', str(descr)).group(1)]
                episodelist.append(episode_data)
    community_episodes = pd.DataFrame(episodelist,
                                      columns=['Season', 'Episode Number', 'Title', 'Airdate', 'Description'])
    if show:
        print(community_episodes.to_string())
    else:
        community_episodes.to_csv(r'C:\Users\causa\Desktop\eps.csv', index=False)


def write_episode_names(base_folder_path, csv_file_path, info=None):
    """
    Overwrite the old file names of the show's episodes with the new
    names scraped from IMDB with `get_episodes`.

    Example:
        write_episode_names("C:\\Users\\causa\\Desktop\\curb",
                                "C:\\Users\\causa\\Desktop\\eps.csv",
                                info="1080p.x265)

    Parameters
    ----------
    base_folder_path: str
        The file location of the show.
    csv_file_path: str
        The file location of the output csv file.
    info: str, optional
        Any additional information about the file.
    """
    if info is not None:
        info = ' - ' + info
    else:
        info = ''
    df = pd.read_csv(csv_file_path)
    # Ensure the CSV file has the required columns.
    if not all(col in df.columns for col in ['Season',
                                             'Episode Number',
                                             'Title',
                                             'Airdate',
                                             'Description']):
        raise ValueError("CSV file columns do not match pattern 'Season', "
                         "'Episode Number', 'Title', 'Airdate', 'Description'. Is it the correct file?")

    def _rename_files(file_name, ext):
        # Helper function.
        for old_name, (_, row) in zip(file_name, group.iterrows()):
            episode_name = ''.join(c for c in row['Title'] if c not in r'\/:*?"<>|')
            episode_num = row['Episode Number']
            new_name = f"S{season:02d}E{episode_num:02d} - {episode_name}{info}.{ext}"
            old_file_path = os.path.join(season_folder, old_name)
            new_file_path = os.path.join(season_folder, new_name)
            os.rename(old_file_path, new_file_path)
            print(f'Renamed: {old_name} -> {new_name}')

    # Group the data by season
    grouped = df.groupby('Season')
    for season, group in grouped:
        # Look for folders titled 'Season X'. Change depending on naming scheme.
        season_folder = os.path.join(base_folder_path, f'Season {season}')
        if not os.path.exists(season_folder):
            print(f"Season folder {season_folder} does not exist. Skipping...")
            continue

        # The keys in this dict are named after the file types because they
        # are passed as the file extensions in the `_rename_files(v, k)` function call.
        files = {'mp4': [f for f in os.listdir(season_folder) if f.endswith('.mp4')],
                 'mkv': [f for f in os.listdir(season_folder) if f.endswith('.mkv')],
                 'avi': [f for f in os.listdir(season_folder) if f.endswith('.avi')],
                 'srt': [f for f in os.listdir(season_folder) if f.endswith('.srt')],
                 'nfo': [f for f in os.listdir(season_folder) if f.endswith('.nfo')]}

        ep_num = max(files, key=lambda k: len(files[k]))
        if len(files[ep_num]) != len(group):
            print(
                f"The number of video files in {season_folder} does not match the number "
                f"of rows in the CSV for season {season}.")
            continue
        for k, v in files.items():
            _rename_files(v, k)
