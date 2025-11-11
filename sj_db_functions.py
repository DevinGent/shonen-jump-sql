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


def _add_week(date: str, data, recency=None):

    """This function is a now deprecated attempt to add weeks to the SJ database.  The class DataLoader is now preferred.
    
    This function updates the Shonen Jump database (shonen_jump.sqlite3) by adding a week's worth of chapters to the 
    chapters table.  Date should be a string of the form YYYY-MM-DD. 
    
    By using the optional parameter "recency" chapter numbers can
    be automatically assigned based on the currently known chapters. If recency='latest' then the chapter number will be 1 more than
    the currently recorded total chapters of the series. If recency='previous' then the chapter number will be 1 less than the smallest recorded chapter
    for the series in the database. 
    
    Data should be a list of dictionaries, with each dictionary containing the following:
    
        {'s': "Name of Series as a string"  # Required

        'r': Rank in the table of contents as an int. # Optional. Should be omitted if chapter type is not 'Normal'

        't': "Type of chapter as a string: 'Absent','Color', 'Cover', or 'Normal'" # Optional, defaults to normal.

        'c': Chapter number as an int. # Optional. Will be overwritten if the recency parameter of add_week is included.}"""
    
    # First we scan the user entered data to warn for errors.
    for entry in data:
        for key in ['s','r','t','c']:
            entry[key]=entry.get(key)
        if entry.get('s')==None:
            raise Exception('The name of each series must be included.')
        if entry.get('r')!=None and entry.get('t').lower() in ['absent','color', 'cover']:
            raise Exception('A special chapter cannon be given a ranking in the table of contents.')
        if entry.get('r')!=None and entry.get('r')<1:
            raise Exception('Rankings cannot be less than 1.')
        if entry.get('c')!=None and recency in ['latest', 'previous']:
            raise Warning('Chapter numbers which were provided have been ignored because the recency parameter was set.')
        entry['d']=date
        
    # We now connect to the database
    connection = sqlite3.connect("shonen_jump.sqlite3")
    cursor=connection.cursor()

    # If recency is set to latest we autocalculate the chapter numbers.
    if recency=='latest':
        cursor.executemany("""
                           INSERT INTO chapters (series, release, chapter, rank, type)
                           VALUES (:s, :d,
                           CASE WHEN :t='Absent' THEN NULL
                           ELSE (SELECT 1 + total_chapters FROM series WHERE title=:s),:r,:t)""",data)
    elif recency=='previous':
        cursor.executemany("""
                           INSERT INTO chapters (series, release, chapter, rank, type)
                           VALUES (:s, :d,
                           CASE WHEN :t='Absent' THEN NULL
                           ELSE (SELECT -1 + MIN(number) FROM chapters WHERE series=:s),:r,:t)""",data)
    # Otherwise we add the information given as is.
    else:
        cursor.executemany("""
                           INSERT INTO chapters (series, release, chapter, rank, type)
                           VALUES (:s,:d,:c,:r,:t)""",data)
    connection.commit()
    connection.close()


def update_absences(db_connection):
    """Searches through the chapters table of the database and adds entries where the series was absent to the absences table.
    This will include longer hiatuses to the absences table which should be handled separately.
    The connection must still be committed after this function is called."""

    cursor=db_connection.cursor()
    # We first query the table to find the earliest and latest recorded chapters.
    cursor.execute("""SELECT MIN(release_date), MAX(release_date) FROM chapters;""")
    (earliest, latest)=cursor.fetchone()

    # We get a table with series as well as their start and end dates.  If a series started before the earliest record in
    # the database we proceed using the earliest known record.  If a series is not finished we use the most recent record.
    df=pd.read_sql_query("""                     
                    SELECT chapters.series, 
                    COALESCE(debuts.release_date,?) AS start, 
                    COALESCE(finales.release_date,?) AS stop 
                    FROM chapters LEFT JOIN debuts ON chapters.series=debuts.series
                    LEFT JOIN finales ON chapters.series=finales.series
                    GROUP BY chapters.series;
                    """,params=(earliest,latest), con=db_connection)
    # We convert this dataframe to a list of dictionaries of the form: 
    # {'series': SERIES_NAME, 'start': START_DATE_STRING, 'stop': STOP_DATE_STRING}
    series_info=df.to_dict(orient='records')
    # We now add to the absences table.
    cursor.executemany("""
    INSERT OR IGNORE INTO absences(series, issue_date)
    SELECT DISTINCT :series AS series_title, release_date FROM chapters 
    WHERE release_date BETWEEN :start AND :stop 
    EXCEPT SELECT DISTINCT :series AS series_title, release_date FROM chapters
    WHERE series= :series;""",series_info)

        

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
    
    
def fill_batches(db_connection):
    """This function updates the batches table of the database. The contents of the batches table are emptied and then replaced.
    The connection must still be committed after this function is called."""    

    cursor=db_connection.cursor()
    # We will use the results of the batch_locator view.
    df=pd.read_sql_query('SELECT * FROM batch_locator ORDER BY release_date',db_connection)

    # Creating a dataframe to record all magazine release dates in order.
    issues= pd.read_sql_query("SELECT DISTINCT release_date FROM chapters ORDER BY release_date", db_connection)
    issues.reset_index(inplace=True)
    issues.set_index('release_date', inplace=True)
    issues.rename(columns={'index':'issue'},inplace=True)
    # We only need the result as a series indexed by date.
    issues = issues['issue']

    # Grouping starting/ending series into batches by those within three issues of each other.
    # Changing this variable changes the tolerance.
    issue_tolerance=3
    # We only need to work with the dates to create a column naming which batch each debut/finale fits into,
    # so we name the series of dates.
    chapters=df['release_date']
    # This will keep track of which batch the date belongs to.
    batch_index=0
    # We will fill out a list that will become a new column of the dataframe.
    batch_column=[0]
    # For each add/completed series, we check if the last (previous) added/completed
    # series was within three issues.  If not, we label it as part of a new batch.
    for i in range(1,len(chapters)):
        if issues.loc[chapters[i]]-issues.loc[chapters[i-1]]>issue_tolerance:
            batch_index+=1
        batch_column.append(batch_index)
    # We set the resulting column as a part of our dataframe
    df['batch']=batch_column

    # Now we create a dataframe to export to the SQL database.
    # output_df is indexed by batch and has two columns: Debut and Finale
    output_df=df.groupby(['batch','debut_or_finale']).size().unstack(fill_value = 0)
    # Next we add a column of start dates and a column of end dates to our output.
    grouped=df.groupby('batch')
    output_df['Start']=grouped['release_date'].min()
    output_df['Stop']=grouped['release_date'].max()

    # We relabel columns 
    col_dict={
            'Start': 'start_date',
            'Stop': 'end_date',
            'Debut': 'added',
            'Finale': 'completed'
        }
    # We remove the contents of the previous batches table.
    cursor.execute("""DELETE FROM batches""")
    # and insert the output_df into the batches table.
    output_df.rename(columns=col_dict).to_sql(name='batches', con=db_connection, if_exists='append', index=False)
    # After this function has been called the user must still commit the connection.



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