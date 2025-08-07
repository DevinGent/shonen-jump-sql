import pandas as pd
import sqlite3
import re
import datetime
import urllib.request



class DataLoader:
    """Obtains information on weekly releases, cleans the obtained data, and then allows the user to insert the result directly into
    the shonen_jump.sqlite database."""

    dictionary_of_title_errors={
        "Me and Roboco": 'Me & Roboco',
        'WITCH WATCH': 'Witch Watch',
    }


    def __init__(self, db_connection):


        self.connection=db_connection
        self._cursor=self.connection.cursor()
        self._cursor.execute('SELECT title FROM series')
        self._all_series=[name[0] for name in self._cursor.fetchall()]

        self.valid_dataframes=[]
        self.invalid_dataframes=[]

    def _load_and_clean_df(self,url):
        """Loads and cleans an individual week's chapters given a url.  Returns a pair with two dataframes, 
        one containing valid entries to add to the chapters table and one containing entries to be omitted."""

        # Get the date from the url
        raw_date=re.search("\d{4}-\d{2}-\d{2}",url)
        # If none is found do not load the url or add dataframes.
        if raw_date==None:
            print(f"The url {url} contains no recognizable date.")
            return
        # Otherwise convert the date obtained to date format.
        raw_date=datetime.datetime.strptime(raw_date.group(0), '%Y-%m-%d').date()
        # Adjust the date to land on the U.S. release window
        corrected_date=raw_date-datetime.timedelta(days=15)
        # If the result is not a sunday, terminate.
        if corrected_date.weekday()!=6:
            print(f"Once adjusted, the date given by {url} is not a Sunday.")
            return
        # Return to string format
        else:
            corrected_date=datetime.datetime.strftime(corrected_date, '%Y-%m-%d')

        # Load a table given a url
        df=pd.read_html(url,attrs = {'class': 'chapters'},index_col=0)[0]

        # Add a column with the correct date.
        df['Date']=corrected_date

        # Strip the chapter number from the chapter title.
        df['Chapter Number']=df['Chapter Title'].str.extract(r'(\d+)').astype(float)

        # Create a new column 'Type' with all entries set to 'Normal.
        df['Type']='Normal'
        # Go through and adjust the special chapter types.
        df.loc[df['Chapter Title'].str.lower().str.contains('lead color'), 'Type'] = 'Cover'
        df.loc[df['Chapter Title'].str.lower().str.startswith('color'), 'Type'] = 'Color'
        df.loc[df['Chapter Title'].str.lower().str.contains('one-shot'), 'Type'] = 'One-Shot'
        
        # Add a Rank column (where only series with normal chapters (and 8 chapters in or later) are included)
        df['Rank']=df.index.map(df.loc[(df['Type'] == 'Normal')&(df['Chapter Number']>7)].index.to_series().rank())
        # Set the index (the raw order of the chapters in the magazine) to be labeled 'placement'
        df.index.name='placement'
        
        # Set the manga titles to match those in the database.
        df.replace({'Manga Title':self.dictionary_of_title_errors},inplace=True)



        # Record which series appear ready to be added to the database and which entries should be omitted 
        # (one-shots, specials, errors, etc)
        valid_series=df[df['Manga Title'].isin(self._all_series)]
        invalid_series=df[~df['Manga Title'].isin(self._all_series)]
        self.valid_dataframes.append(valid_series)
        self.invalid_dataframes.append(invalid_series)

        
    def _get_next_url_ending(self,current_url: str):
        """Obtains the next (previous chronologically) url to obtain TOC information from."""

        # Open the first url.
        first_page = urllib.request.urlopen(current_url)
        # Convert the page to a long string.
        expanded_page=first_page.read()
        expanded_page=expanded_page.decode("utf8")
        # Locate the link to the next url.
        result=re.search('<a class="prev-issue-link" href="(.*?)">', expanded_page)
        # Return the result.
        return result.group(1)
        


    def load_from_urls(self,url_stem: str,starting_url: str, stop_point: int=1):
        """Loads data from the given url and previous weeks to the class instance's list of valid and invalid dataframes.
        The optional argument stop_point determines how many urls should be used.  If stop_point is an integer N, then
        the starting urls and the N-1 which came before will be used."""

        url_list=[starting_url]
        current_url=starting_url
        for i in range(stop_point):
            new_ending=self._get_next_url_ending(current_url)
            current_url=url_stem+new_ending
            url_list.append(current_url)
        
        for url in url_list:
            self._load_and_clean_df(url)
        print("The final url used was:")
        print(url)

    def df_to_sql(self,dataframe):
        """Insert the selected dataframe (from either the valid or invalid lists of the class instance)
        into the chapters table using the provided database connection of the class."""

        col_dict={
            'Manga Title': 'series',
            'Date': 'release_date',
            'Chapter Number': 'chapter',
            'Type': 'type',
            'Rank':'toc_rank'
        }

        dataframe.drop(columns=['Chapter Title']).rename(columns=col_dict).to_sql(name='chapters', con=self.connection, if_exists='append')

    def insert_all_valid(self):
        """Inserts every dataframe in the list of valid series into the database."""
        for df in self.valid_dataframes:
            self.df_to_sql(df)










def main():
    connec=sqlite3.connect('shonen_jump.sqlite3')

    loader=DataLoader(connec)
    loader.load_from_urls('https://www.jajanken.net',
                          'https://www.jajanken.net/en/issues/2025-08-18',
                          5)

    loader.insert_all_valid()
    connec.commit()
    connec.close()

if __name__ == "__main__":
    main()