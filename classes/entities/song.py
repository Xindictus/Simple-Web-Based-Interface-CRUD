#!/Python27/python

from ..database.database import Database

# A class used for song insertion


class Song:

    def __init__(self, title, production_year, cd, singer, composer, song_writer):
        self.title = title
        self.production_year = production_year
        self.cd = cd
        self.singer = singer
        self.composer = composer
        self.song_writer = song_writer

    def insert_song(self):

        # get a new database connection
        connection = Database().start_connection()

        try:
            # check for empty fields
            if(self.title == '' or
               self.production_year == '' or
               self.cd == '' or
               self.singer == '' or
               self.composer == '' or
               self.song_writer == ''):
                raise Exception('Empty Fields')

            # insert the song with prepared statement
            with connection.cursor() as cursor:
                song_query = "INSERT INTO `tragoudi` (`titlos`, `sinthetis`, `etos_par`, `stixourgos`) " \
                             "VALUES (%s, %s, %s, %s)"
                cursor.execute(song_query, (self.title, self.composer, self.production_year, self.song_writer))
                sinprod_query = "INSERT INTO `singer_prod` (`cd`, `tragoudistis`, `title`) VALUES  (%s, %s, %s)"
                cursor.execute(sinprod_query, (self.cd, self.singer, self.title))

            # commit database changes
            connection.commit()

            # return the class for the alert box and the message to be shown
            return [
                'class="alert alert-success text-center"',
                'Song inserted successfully.'
            ]
        except:
            # on exception, return the class for the alert box and the message to be shown
            return [
                'class="alert alert-danger text-center"',
                'Song could not be inserted.'
            ]
        finally:
            # close the database connection
            Database().close_connection(connection)
