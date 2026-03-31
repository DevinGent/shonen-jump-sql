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

### `model_testing.ipynb`
A Jupyter Notebook which serves as a tutorial on how to load and use models from the `classifiers` folder. 

## Database Structure