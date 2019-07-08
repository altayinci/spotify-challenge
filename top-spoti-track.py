import os
import json
import sys
import random

from spotifyclient import SpotifyClient
from credentials import credentials
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify

app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'


@app.route('/')
def main_page():
    return redirect(url_for('get_track_genre'))


@app.route('/tracks')
def get_track_genre():
    return render_template('tracks.html')


@app.route('/tracks', methods=['POST'])
def get_song_list():
    text = request.form['text']
    genre = text.lower()

    file_name = os.path.join(sys.path[0], "genres.json")

    with open(os.path.join(file_name)) as json_file:
        genres_info = json.load(json_file)

    singers = genres_info.get(genre)

    if singers:
        random_singer = random.choice(singers)
        client = SpotifyClient(client_id=credentials['client_id'], client_secret=credentials['client_secret'],
                               base_url=credentials['base_url'])

        data = {'q': random_singer, 'type': 'artist'}
        songs_list = client.get_top_tracks(data)

        return jsonify(songs_list)

    else:
        flash("There is not this genre in list")
        return redirect(url_for('get_track_genre'))


if __name__ == '__main__':
    app.run(host="127.0.0.1", port="8080")
