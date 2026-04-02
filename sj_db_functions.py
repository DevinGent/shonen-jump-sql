import sqlite3
import re
import datetime
import pandas as pd
import urllib.request



class DataLoader:
    """Obtains information on weekly releases, cleans the obtained data, and then allows the user to insert the result directly into
    the shonen_jump.sqlite database."""

    dictionary_of_title_errors={
        "Me and Roboco": 'Me & Roboco',
        'Witch Watch': 'WITCH WATCH'
    }


    def __init__(self, db_connection):


        self.connection=db_connection
        self._cursor=self.connection.cursor()
        self._cursor.execute('SELECT title FROM series')
        self._all_series=[name[0] for name in self._cursor.fetchall()]

        self.valid_dataframes=[]
        self.invalid_dataframes=[]

    def _load_and_clean_df(self,url, day_offset):
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
        corrected_date=raw_date-datetime.timedelta(days=day_offset)
        # If the result is not a sunday, terminate.
        if corrected_date.weekday()!=6:
            print(f"Once adjusted, the date given by {url}: {corrected_date}, is not a Sunday.")
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
        # To protect against the case when the chapter number is excluded (final chapters will typically omit the number)
        # We will also include TOC ranks for series which have normal chapters but no chapter number.
        df['Rank']=df.index.map(df.loc[(df['Type'] == 'Normal')&
                                       ((df['Chapter Number'] > 7)|((df['Chapter Number'].isna())))].index.to_series().rank())
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
        


    def load_from_urls(self,url_stem: str,starting_url: str, stop_point: int=0, day_offset:int=15):
        """Loads data from the given url and previous weeks to the class instance's list of valid and invalid dataframes.
        The optional argument stop_point determines how many urls should be used.  If stop_point is an integer N, then
        the starting urls and the N-1 which came before will be used. The optional argument day_offset determines
        how to adjust the date provided by the url."""

        url_list=[starting_url]
        current_url=starting_url
        for i in range(stop_point):
            new_ending=self._get_next_url_ending(current_url)
            current_url=url_stem+new_ending
            url_list.append(current_url)
        
        for url in url_list:
            self._load_and_clean_df(url,day_offset)
        print("The final url used was:")
        print(url)

    def df_to_sql(self,dataframe):
        """Insert the selected dataframe (from either the valid or invalid lists of the class instance)
        into the chapters table using the provided database connection of the class.
        The connection must still be committed after this function is called."""

        col_dict={
            'Manga Title': 'series',
            'Date': 'release_date',
            'Chapter Number': 'chapter',
            'Type': 'type',
            'Rank':'toc_rank'
        }

        dataframe.drop(columns=['Chapter Title']).rename(columns=col_dict).to_sql(name='chapters', con=self.connection, if_exists='append')


    def insert_or_ignore_df(self,dataframe):
        """Insert the selected dataframe (from either the valid or invalid lists of the class instance)
        into the chapters table using the provided database connection of the class.
        The connection must still be committed after this function is called. Ignores inserting any row which already exists."""
        col_dict={
            'Manga Title': 'series',
            'Date': 'release_date',
            'Chapter Number': 'chapter',
            'Type': 'type',
            'Rank':'toc_rank'
        }
        dataframe.rename(columns=col_dict).reset_index().to_dict('records')
        self._cursor.executemany("""INSERT OR IGNORE INTO chapters(placement,series,release_date,chapter,type,toc_rank)
                                 VALUES (:placement,:series,:release_date,:chapter,:type,:toc_rank)
                                 """,dataframe.rename(columns=col_dict).reset_index().to_dict('records'))


    
    def insert_all_valid(self):
        """Inserts every dataframe in the list of valid series into the database."""
        for df in self.valid_dataframes:
            self.df_to_sql(df)

    def compile_all_invalid(self):
        """"Returns a data containing the combined rows from all the dataframes in self.invalid_dataframes."""
        return pd.concat(self.invalid_dataframes)
    
    def compile_all_valid(self):
        """"Returns a data containing the combined rows from all the dataframes in self.valid_dataframes."""
        return pd.concat(self.valid_dataframes)

# Here we start adding individual functions outside the class.

def update_last_chapter(db_connection):
    """This function searches through the chapters table of the database for null values.
    It then sets the chapter to be one more than the series' previous chapter. 
    The connection must still be committed after this function is called."""

    cursor=db_connection.cursor()
    cursor.execute("""UPDATE chapters SET
                   chapter=1+(SELECT MAX(chapter) FROM chapters as c
                   WHERE chapters.series=c.series
                   GROUP BY series)
                   WHERE chapter IS NULL AND type!='One-Shot';""")
    


def load_modeling_data(db_connection,basis_size: int):
    """Following the procedure in predicting_success.ipynb, this function generates a dataframe representing the
    early performance of each series in the database of their first basis_size chapters. Target labels can be obtained
    by passing the list of titles obtained here into the function success_or_failure."""

    # First load general series information.
    df=pd.read_sql_query("""
    -- We want the name and genre of each series.                     
    SELECT title,genre,  
    -- Next we want an indicator column where 1 indicates that the series has one creator (who both writes and draws) and 
    -- 0 if the series has a different artist and writer.  We call this column one_creator.
    CASE
    WHEN writer=artist THEN 1
    ELSE 0 END one_creator,
    -- We also want to track what the average placement of the series was, how many color pages it received, and
    -- and how many cover pages it received over its first basis_size number of chapters. 
    -- These columns will be obtained below.
    average_placement,
    color_pages,
    cover_pages,
    -- Finally we want the debut date and the size of the batch the series started in.
    debuts.release_date,
    batches.added AS batch_size

    -- We now begin obtaining the above columns and selecting series where we know their early performance. 
    FROM series
    -- By inner joining with debuts we restrict ourselves to series where the database includes chapters starting from 1.
    INNER JOIN debuts ON title=debuts.series
    -- We join with a selection which averages the placement of each series over its first basis_size chapters
    LEFT JOIN (SELECT AVG(placement) AS average_placement, series FROM chapters
    WHERE chapter<=:basis_size GROUP BY series) AS avplace
    ON title=avplace.series
    -- We join again with a selection which counts the number of color pages over the series' first basis_size chapters.
    LEFT JOIN (SELECT series,COUNT(series) AS color_pages FROM chapters
    WHERE type='Color' AND chapter<=:basis_size
    GROUP BY series) AS colorp
    ON title=colorp.series
    -- We join again with a selection which counts the number of cover pages over the series' first basis_size chapters.
    LEFT JOIN (SELECT series,COUNT(series) AS cover_pages FROM chapters
    WHERE type='Cover' AND chapter<=:basis_size
    GROUP BY series) AS coverp
    ON title=coverp.series
    -- We also join with batches by associating to each series' debut the batch it lands within.
    LEFT JOIN batches ON debuts.release_date BETWEEN batches.start_date AND batches.end_date
    ORDER BY title;
                """, con=db_connection, params={'basis_size':basis_size})
    
    # Next load the placement of individual chapters.
    chapter_placement_df=pd.read_sql_query("""
    SELECT series, chapter, placement FROM chapters WHERE chapter<=?
    ORDER BY series, release_date""",con=db_connection,params=[basis_size])

    # Pivot the dataframe of placements
    chapter_placement_df=chapter_placement_df.pivot(index='series',columns='chapter',values='placement').add_prefix("place_chap_")

    # Store the list of column titles.
    chapter_placement_columns=chapter_placement_df.columns.to_list()

    chapter_placement_df.dropna(axis='index',inplace=True)
    # Merge the two dataframes
    df=df.merge(chapter_placement_df,left_on='title',right_index=True)

    # Ensure placements are treated as int values.
    df[chapter_placement_columns]=df[chapter_placement_columns].astype(int)

    # Convert the date to a datetime and extract the year and month
    df['release_date']=pd.to_datetime(df['release_date'])
    df['release_year']=df['release_date'].dt.year
    df['release_month']=df['release_date'].dt.month

    # Drop the original release_date column.
    df.drop(columns=['release_date'],inplace=True)
    
    # Reset the index
    df.reset_index(drop=True, inplace=True)

    # Return the dataframe.
    return df

def average_placements(db_connection,basis_size: int, include_canceled=False):
    """For each series in the magazine recorded in the database, this function calculates the average placement over
    the first basis_size chapters and returns the result as a dataframe. Series missing chapters in the range 1-basis_size
    are excluded."""

    if include_canceled==False:
        # Getting average placements for series which include all basis_size first chapters in the database.
        df=pd.read_sql_query("""
        SELECT series AS title, AVG(placement) AS average_placement
        FROM chapters 
        WHERE chapter<=:basis_size
        GROUP BY series
        HAVING COUNT(*)=:basis_size;""",con=db_connection, params={'basis_size':basis_size})
    else:
        # If the optional argument include_canceled is set to True we will add the average placements of
        # series which were canceled before reaching basis_size chapters.
        df=pd.read_sql_query("""
        SELECT av.title, av.average_placement
        FROM (
        SELECT series AS title, AVG(placement) AS average_placement, COUNT(*) AS nchaps FROM
        chapters 
        WHERE chapter<=:basis_size
        GROUP BY series) as av
        LEFT JOIN series on av.title=series.title
        WHERE nchaps=:basis_size OR (nchaps=total_chapters AND status='Complete');""",
        con=db_connection, params={'basis_size':basis_size})

    # And then we return the result.
    return df






def success_or_failure(db_connection, success_criteria: int, titles: list):
    """Given a list of titles in Shonen Jump and a success criteria, this function determines (for each title)
    success or failure and returns a dataframe with two columns, title and success, where 1 represents a success and 0 a failure.  
    A title is considered a success if it runs for at least success_criteria chapters."""

    # We make a list of parameters to pass to an sql query.
    param_list=[success_criteria,success_criteria]+titles

    # We create a query.
    sql_query=f"""
    SELECT
    title,
    CASE
    WHEN total_chapters<? AND status='Complete' THEN 0
    WHEN total_chapters>=? THEN 1
    ELSE NULL
    END success FROM series
    WHERE title IN ({', '.join(['?' for title in titles])})"""

    # We return the desired dataframe
    return pd.read_sql_query(sql_query,params=param_list,con=db_connection)

    

def main():
    # Example usage.
    pass
    """
    connection = sqlite3.connect("shonen_jump.sqlite3")
    cursor=connection.cursor()
    new_chapters=[
        {'s':'One Piece', 'r':None,'t':'Cover'},
        {'s':'Kagurabachi', 'r':None,'t':'Color'},
        {'s':'Sakamoto Days', 'r':1,'t':'Normal'},
        {'s':'Ichi the Witch', 'r':None,'t':'Color'},
        {'s':'Kaedegami', 'r': None,'t':'Normal'},
        {'s':'The Elusive Samurai', 'r':13,'t':'Normal'},
        {'s':'Shinobi Undercover', 'r':4,'t':'Normal'},
        {'s':"Nue's Exorcist", 'r':12,'t':'Normal'},
        {'s':'Ultimate Exorcist Kiyoshi', 'r':2,'t':'Normal'},
        {'s':'Hima-Ten!', 'r':3,'t':'Normal'},
        {'s':'Witch Watch', 'r':10,'t':'Normal'},
        {'s':'Akane-banashi', 'r':8,'t':'Normal'},
        {'s':'Blue Box', 'r':5,'t':'Normal'},
        {'s':'Ekiden Bros', 'r':None,'t':'Normal'},
        {'s':'Harukaze Mound', 'r':6,'t':'Normal'},
        {'s':'Kill Blue', 'r':11,'t':'Normal'},
        {'s':'Me & Roboco', 'r':7,'t':'Normal'},
        {'s':'Nice Prison', 'r':9,'t':'Normal'},
        {'s':'Otr of the Flame', 'r':14,'t':'Normal'},
        {'s':'Ping-Pong Peril', 'r':None,'t':'Normal'},
    ]
    release_date='2025/08/03'
    add_week(release_date,new_chapters)
    """



if __name__ == "__main__":
    main()