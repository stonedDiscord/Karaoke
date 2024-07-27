import json
import sqlite3

# Function to create a table for a specific karaoke model
def create_model_table(cursor, model_name):
    table_name = f'karaoke_{model_name.replace(" ", "_").replace(".", "").replace("-", "_")}'
    cursor.execute(f'''
    CREATE TABLE IF NOT EXISTS {table_name} (
        requestNo TEXT,
        statusCode INTEGER,
        message TEXT,
        artistCode INTEGER,
        artist TEXT,
        title TEXT,
        titleYomi_Kana TEXT,
        firstLine TEXT,
        releaseDate INTEGER,
        shift INTEGER,
        mainMovieId INTEGER,
        mainMovieName TEXT,
        subMovieId INTEGER,
        subMovieName TEXT,
        honninFlag INTEGER,
        animeFlag INTEGER,
        liveFlag INTEGER,
        mamaotoFlag INTEGER,
        namaotoFlag INTEGER,
        duetFlag INTEGER,
        guideVocalFlag INTEGER,
        prookeFlag INTEGER,
        scoreFlag INTEGER,
        duetDxFlag INTEGER,
        damTomoMovieFlag INTEGER,
        damTomoRecordingFlag INTEGER,
        myListFlag INTEGER,
        titleAvailable INTEGER
    )''')
    return table_name

# Function to insert data into the respective model table
def insert_data(cursor, data):    
    # Extracting basic information
    requestNo = data['data'].get('requestNo')
    print(requestNo)
    statusCode = data['result'].get('statusCode')
    message = data['result'].get('message')
    artistCode = data['data'].get('artistCode')
    artist = data['data'].get('artist')
    title = data['data'].get('title')
    titleYomi_Kana = data['data'].get('titleYomi_Kana')
    firstLine = data['data'].get('firstLine')
    
    # Insert model data
    for item in data['list']:
        for kModelMusicInfo in item['kModelMusicInfoList']:
            for model in kModelMusicInfo['eachModelMusicInfoList']:
                titleAvailable = 1 if model['karaokeModelNum'] else 0
                if not hasattr(model, 'shift'):
                    model['shift'] = 0
                table_name = create_model_table(cursor, model['karaokeModelName'])
                cursor.execute(f'''
                INSERT INTO {table_name} (
                    requestNo, statusCode, message, artistCode, artist, title, titleYomi_Kana, firstLine,
                    releaseDate, shift, mainMovieId, mainMovieName,
                    subMovieId, subMovieName, honninFlag, animeFlag, liveFlag, mamaotoFlag, namaotoFlag,
                    duetFlag, guideVocalFlag, prookeFlag, scoreFlag, duetDxFlag, damTomoMovieFlag,
                    damTomoRecordingFlag, myListFlag, titleAvailable
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?,
                    date(?), ?, ?, ?,
                    ?, ?, ?, ?, ?, ?, ?,
                    ?, ?, ?, ?, ?, ?,
                    ?, ?, ?)
                ''', (
                    requestNo, statusCode, message, artistCode, artist, title, titleYomi_Kana, firstLine,
                    model['releaseDate'], model['shift'], model['mainMovieId'], model['mainMovieName'],
                    model['subMovieId'], model['subMovieName'], model['honninFlag'], model['animeFlag'], model['liveFlag'], model['mamaotoFlag'], model['namaotoFlag'],
                    model['duetFlag'], model['guideVocalFlag'], model['prookeFlag'], model['scoreFlag'], model['duetDxFlag'], model['damTomoMovieFlag'],
                    model['damTomoRecordingFlag'], model['myListFlag'], titleAvailable
                ))
    

# Main function to process the file
def main():
    # Connect to the SQLite database
    conn = sqlite3.connect('karaoke.db')
    cursor = conn.cursor()

    # Open the file and process each line
    with open('music_details.txt', 'r', encoding='utf-8') as file:
        for line in file:
            data = json.loads(line.strip())
            # Skip the line if artistCode is missing
            if 'artistCode' not in data['data']:
                continue
            insert_data(conn, data)
            conn.commit()
    
    conn.close()

if __name__ == '__main__':
    main()
