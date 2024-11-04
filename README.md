# media-file-tools

## Description

Media File Tools is a Python package designed to automate some of the tedious tasks of organizing your media files. 

## Features

- Bulk rename TV series episodes that have undescriptive names.
- Create a TV show database with episode title, air date and plot summary.
- Create a movies database organized alphabetically or by folder.
- Find duplicate music files.
- Uses BeautifulSoup4 and Cinemagoer to scrape data from IMDB.

## Installation

You can install media-file-tools using pip:

```bash
pip install media-file-tools
```

## How to use
To create a csv file with the seasons, titles and plot summaries of a TV series:
```py
from mediafiletools import make_seriesdb

make_seriesdb(imdb_id='tt0098904')
```
To overwrite the old file names of the show on your disc with the ones one the csv file:
```py
from mediafiletools import rename_episodes

rename_episodes('C:\Users\user\Videos\Seinfeld', csv_path='C:\Users\user\episodes.csv')
```
> Use caution with this command. Right now, this only looks for folders titled 'Season 1', 'Season 2', 'Season 3' etc. 
> Any folders not following this naming convention will be skipped. The names of the files before and after they're 
> renamed are recorded in a log.

To get the episodes and write the file names in one command, pass the `imdb_id` as a keyword to `rename_episodes`:
```py
rename_episodes('C:\Users\user\Videos\Seinfeld', imdb_id='tt0098904')
```
> Sometimes the episodes on IMDB are in a different order or have episode 0/unaired pilots 
> not on a DVD or BlueRay. Make sure the episodes list lines up perfectly with the ones on your disc.
> 
To specify which season(s) to get, pass the season numbers as the `start` and `end` keywords:
```py
make_seriesdb(imdb_id='tt0098904', start=3, end=6)
```

To create an organized movie database from every movie file in the directory:
```py
from mediafiletools import make_moviedb

make_moviedb('C:\Users\user\Movies')
```
> Calling with no arguments will sort the movies alphabetically by default. To organize movies by folder instead, use the `sort_type` keyword:
```py
make_moviedb('C:\Users\user\Movies', sort_type='folder')
```
To clean up the filenames, use the `strip` keyword:
```py
make_moviedb('C:\Users\user\Movies', sort_type='folder', strip=True)
```
> This will remove extraneous text from the filename. e.g.
> Double.Down.2005.DVDRip.x264.mkv will be written as:
> Double Down 2005
 
To find duplicate music files:
```py
from mediafiletools import find_music_dupes

find_music_dupes(r'C:/Users/user/Music')
```

To output to the console or a text file instead of a csv, use the `output_type` keyword:
```py
make_moviedb('C:\Users\user\Movies', output_type='txt')
```
> Supported keywords are `csv`, `txt` and `console`.