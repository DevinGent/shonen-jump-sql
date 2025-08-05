import sqlite3



def add_week(date: str, data, recency=None):

    """This function updates the Shonen Jump database (shonen_jump.sqlite3) by adding a week's worth of chapters to the 
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

        

    
    


def main():
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
    #add_week(release_date,new_chapters)
    connection.commit()
    connection.close()



if __name__ == "__main__":
    main()