#!/Python27/python
# -*- coding: UTF-8 -*-

import sys
import os
sys.path.append(os.path.join(os.path.split(os.path.abspath(__file__))[0], 'lib'))
from bottle import *
from classes.entities.artist import Artist
from classes.entities.song import Song
from classes.database.database import Database
import classes.database.settings as settings
import pymysql

app = Bottle()


# LOAD CSS FILES
@get('/<filename:re:.*\.css>')
def stylesheets(filename):
    return static_file(filename, root='static/css')


# LOAD JS FILES
@get('/<filename:re:.*\.js>')
def javascript(filename):
    return static_file(filename, root='static/js')


# LOAD IMG FILES
@get('/<filename:re:.*\.png>')
def images(filename):
    return static_file(filename, root='static/img')


# HOME
@route('/')
def index():
    return template('index')


# The page where we can search and update artists
@route('/searchArtists')
def search_artist():
    return template('presentationOfArtists', display='none', artists='', update_status='')


@post('/searchArtists')
def do_search_artist():
    artist_dictionary = {}

    name = request.forms.get('artistName')
    surname = request.forms.get('artistSurname')
    birth_year_from = request.forms.get('birthYearFrom')
    birth_year_to = request.forms.get('birthYearTo')
    artist_type = request.forms.get('type')

    type_dictionary = {
        'singer': 'JOIN singer_prod ON kalitexnis.ar_taut = singer_prod.tragoudistis ',
        'song_writer': 'JOIN tragoudi ON kalitexnis.ar_taut = tragoudi.stixourgos ',
        'composer': 'JOIN tragoudi ON kalitexnis.ar_taut = tragoudi.sinthetis ',
    }

    artist_sql = "SELECT ar_taut, onoma, epitheto, etos_gen " \
                 "FROM kalitexnis "

    try:
        artist_sql += type_dictionary[artist_type]
    except KeyError:
        print 'KeyError Exception @post/searchArtists '

    if name != '':
        artist_dictionary['onoma like'] = "%"+name+"%"

    if surname != '':
        artist_dictionary['epitheto like'] = "%"+surname+"%"

    if birth_year_from != '':
        artist_dictionary['etos_gen >='] = birth_year_from

    if birth_year_to != '':
        artist_dictionary['etos_gen <='] = birth_year_to

    flag = 0

    for key, value in artist_dictionary.iteritems():
        if flag == 0:
            artist_sql += "WHERE " + key + " '" + value + "' "
            flag = 1
        else:
            artist_sql += "AND " + key + " '" + value + "' "

    artist_sql += 'GROUP BY ar_taut'
    connection = Database().start_connection()

    try:
        with connection.cursor() as cursor:
            cursor = connection.cursor(pymysql.cursors.DictCursor)
            cursor.execute(artist_sql)
            artists = cursor.fetchall()
    finally:
        connection.close()

    return template('presentationOfArtists', display='inline', artists=artists, update_status='')


# The page where we update the selected artist
@route('/updateArtist')
def update_artist():

    # check if page has GET parameter
    try:
        nationalID = request.query['editID']
    except KeyError:
        return template('error404')

    # dynamically filling form text fields with current artist information
    artist_sql = "SELECT onoma, epitheto, etos_gen " \
                 "FROM kalitexnis " \
                 "WHERE ar_taut='"+nationalID+"'"

    connection = Database().start_connection()

    try:
        with connection.cursor() as cursor:
            cursor = connection.cursor(pymysql.cursors.DictCursor)
            cursor.execute(artist_sql)
            artist = cursor.fetchone()
    finally:
        connection.close()

    return template(
        'updateArtist',
        nationalID=nationalID,
        onoma=artist['onoma'],
        epitheto=artist['epitheto'],
        etos_gen=artist['etos_gen']
    )


@post('/updateArtist')
def do_update_artist():
    artist = Artist(
        request.forms.get('nationalID'),
        request.forms.get('artistName'),
        request.forms.get('artistSurname'),
        request.forms.get('birthYear'))

    result = artist.update_artist()
    message = '<div ' + result[0] + ' role="alert">' + result[1] + '</div>'

    return template('presentationOfArtists', display='none', artists='', update_status=message)


# The page for searching songs
@route('/searchSongs')
def search_song():
    return template('presentationOfSongs', display='none', songs='')


# posting data to search relevant songs
@post('/searchSongs')
def do_search_song():

    # post data
    song_title = request.forms.get('songTitle')
    production_year = request.forms.get('productionYear')
    company = request.forms.get('company')

    # basic sql query
    songs_sql = "SELECT titlos, etaireia, etos_par " \
                "FROM tragoudi " \
                "JOIN singer_prod " \
                "ON tragoudi.titlos = singer_prod.title " \
                "JOIN cd_production " \
                "ON singer_prod.cd = cd_production.code_cd "

    # dynamically appending specifications
    filters = {}

    if song_title != '':
        filters['titlos'] = song_title

    if production_year != '':
        filters['etos_par'] = production_year

    if company != '':
        filters['etaireia'] = company

    flag = 0
    for key, value in filters.iteritems():
        if flag == 0:
            songs_sql += "WHERE "+key+" like '%"+value+"%' "
            flag = 1
        else:
            songs_sql += "AND "+key+" like '%"+value+"%' "

    songs_sql += "GROUP BY titlos, etaireia"

    # a new connection and execution of select query
    connection = Database().start_connection()

    try:
        with connection.cursor() as cursor:
            cursor = connection.cursor(pymysql.cursors.DictCursor)
            cursor.execute(songs_sql)
            songs = cursor.fetchall()
    finally:
        connection.close()
    return template('presentationOfSongs', display='inline', songs=songs)


# The page for inserting a new artist
@route('/insertArtist')
def insert_artist():
    return template('insertArtist', insert_status='')


# posting data to insert artist
@post('/insertArtist')
def do_insert_artist():
    # a new instance of artist
    artist = Artist(
        request.forms.get('nationalID'),
        request.forms.get('name'),
        request.forms.get('surname'),
        request.forms.get('birthYear'))

    # inserting artist and getting the result of the insertion
    result = artist.insert_artist()
    message = '<div '+result[0]+' role="alert">'+result[1]+'</div>'

    return template('insertArtist', insert_status=message)


# The page for inserting a new song
@route('/insertSong')
def insert_song():

    # starting a new database connection
    connection = Database().start_connection()

    # getting the cds, and ids of singers, composers, song_writers
    try:
        with connection.cursor() as cursor:
            cursor = connection.cursor(pymysql.cursors.DictCursor)
            cd_sql = "SELECT `code_cd` FROM `cd_production`"
            kalitexnis_sql = "SELECT `ar_taut` FROM `kalitexnis`"
            cursor.execute(cd_sql)
            cds = cursor.fetchall()
            cursor.execute(kalitexnis_sql)
            kalitexnis = cursor.fetchall()
    finally:
        connection.close()

    # filling the select elements
    return template(
        'insertSong',
        cds=cds,
        singers=kalitexnis,
        composers=kalitexnis,
        song_writers=kalitexnis,
        insert_status=''
    )


# posting data to insert song
@post('/insertSong')
def do_insert_song():

    # a new instance of Song
    song = Song(
        request.forms.get('songTitle'),
        request.forms.get('productionYear'),
        request.forms.get('cdSelect'),
        request.forms.get('singerSelect'),
        request.forms.get('composerSelect'),
        request.forms.get('songWriterSelect'))

    # getting the result of the insertion
    result = song.insert_song()
    message = '<div ' + result[0] + ' role="alert">' + result[1] + '</div>'

    # filling select elements again
    connection = Database().start_connection()

    try:
        with connection.cursor() as cursor:
            cursor = connection.cursor(pymysql.cursors.DictCursor)
            cd_sql = "SELECT `code_cd` FROM `cd_production`"
            kalitexnis_sql = "SELECT `ar_taut` FROM `kalitexnis`"
            cursor.execute(cd_sql)
            cds = cursor.fetchall()
            cursor.execute(kalitexnis_sql)
            kalitexnis = cursor.fetchall()
    finally:
        connection.close()

    return template(
        'insertSong',
        cds=cds,
        singers=kalitexnis,
        composers=kalitexnis,
        song_writers=kalitexnis,
        insert_status=message
    )


# an error 404 page
# redirects the user to home page
@error(404)
def error_page(errno):
    return template('error404')


# starting localhost application
if __name__ == '__main__':
    port = int(os.environ.get('PORT', settings.web_port))
    run(host='localhost', port=port, debug=True)
