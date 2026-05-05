# Shonen Jump Database

*Weekly Shōnen Jump* is a manga (comic book) magazine that has been published weekly in Japan since 1969. In this project I have created a SQLite database to track the weekly releases of the series in the magazine. This repository contains both the SQLite file itself as well as scripts to make adding to the database easier, or to analyze its contents. One major area of investigation is using machine learning to predict the success of a series running in the magazine based upon the performance of its initial chapters.

## Repository Contents

### Folder: `classifiers`
Includes fitted classifiers used to predict the success of a series based upon its initial performance. More details can be found in the folder's included README.

### Folder: `sql_files`
Includes a collection of SQL queries to be executed on the database.

### `db_setup.ipynb`
A Jupyter Notebook which walks through the process of constructing the database initially.

### `interactive_entry.ipynb`
A Jupyter Notebook used to dynamically update the database with additional chapter information. Because of the ad hoc nature of testing and adding involved this notebook will always appear messy and only individual cells should be run at any given time.

### `ml_play.ipynb`
A testing ground for machine learning techniques on an up-to-date version of the database.

### `model_testing.ipynb`
A Jupyter Notebook which serves as a tutorial on how to load and use models from the `classifiers` folder. 

### `predicting_success.ipynb`
A Jupyter Notebook which considers the task of determining the long term success of a series from the performance of its initial chapters.  This notebook walks through the process of creating an ML classifier via a processing pipeline and grid search.

### `shonen_jump_copy.sqlite3`
A backup of the database which is included when making major changes.

### `shonen_jump_demo.sqlite3`
An older version of the database that `predicting_success.ipynb` runs off of.

### `shonen_jump.sqlite3`
The full database with all available updates included.

### `sj_db_functions.py`
A collection of utility functions which help with tasks such as adding new chapter information to the database or procuring modeling data for ML tasks.

## Database Structure
The database `shonen_jump.sqlite3` contains the following tables and views, of which `chapters` and `series` are the most important. We provide a brief synopsis of the contents of each table and view below.

### Table: `chapter_types`
A simple list of the valid kinds of chapters which can be published in *Weekly Shōnen Jump.* In addition to normal chapters some can start with a page or two in full color, or the series could have been on the cover of the magazine.

### Table: `chapters`
Tracks the individual chapter release for each series in the magazine including information such as the date, chapter type, chapter number, rank, and placement.  For our purposes placement is the position of the chapter in the magazine while toc rank is the position when only normal chapters beyond chapter 7 are included. It is commonly thought that reader surveys cannot affect the placement of a series until at least chapter 8 (because of the time it takes to collect and process the first surveys), and color pages typically occur around the same parts of the magazine. Thus toc rank may be the easiest way to compare the performance of series running simultaneously (with a lower number representing an earlier, and preferable, appearance in the magazine). This table is the one most often updated to include the latest releases or to expand the historical depth of the database.

### Table: `genres`
A list of the different genres series may belong to. In this database we will assume series only belong to one genre, even though series often blend elements from multiple genres (such as battle and comedy, or sports and romance).

### Table: `series`
A list all series which have chapters appearing in the `chapters` table. This includes information such as the number of chapters published in *Weekly Shōnen Jump*, the name of the creator (or writer and artist, if a collaboration), and current status. 