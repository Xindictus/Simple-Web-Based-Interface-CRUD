#!/Python27/python

from ..database.database import Database

# A class used for artist insertion


class Artist:

    def __init__(self, national_id, name, surname, birth_year):
        self.national_id = national_id
        self.name = name
        self.surname = surname
        self.birth_year = birth_year

    def insert_artist(self):

        # get a new database connection
        connection = Database().start_connection()
        try:
            # check for empty fields
            if(self.national_id == '' or
               self.name == '' or
               self.surname == '' or
               self.birth_year == ''):
                raise Exception('Empty Fields')

            # insert artist with prepared statement
            with connection.cursor() as cursor:
                query = "INSERT INTO `kalitexnis` (`ar_taut`, `onoma`, `epitheto`, `etos_gen`) VALUES (%s, %s, %s, %s)"
                cursor.execute(query, (self.national_id, self.name, self.surname, self.birth_year))

            # commit database changes
            connection.commit()

            # return the class for the alert box and the message to be shown
            return [
                'class="alert alert-success text-center"',
                'Artist inserted successfully.'
            ]
        except:
            # on exception, return the class for the alert box and the message to be shown
            return [
                'class="alert alert-danger text-center"',
                'Artist could not be inserted.'
            ]
        finally:
            # close the database connection
            Database().close_connection(connection)

    def update_artist(self):

        # get a new database connection
        connection = Database().start_connection()
        try:
            # check for empty fields
            if (self.national_id == '' or
                self.name == '' or
                self.surname == '' or
                    self.birth_year == ''):
                raise Exception('Empty Fields')

            # update artist with prepared statement
            with connection.cursor() as cursor:
                query = "UPDATE kalitexnis " \
                        "SET onoma=%s, epitheto=%s, etos_gen=%s " \
                        "WHERE ar_taut=%s"
                cursor.execute(query,
                               (self.name,
                                self.surname,
                                self.birth_year,
                                self.national_id))

            # commit database changes
            connection.commit()

            # return the class for the alert box and the message to be shown
            return [
                'class="alert alert-success text-center"',
                'Artist updated successfully.'
            ]

        except:
            # on exception, return the class for the alert box and the message to be shown
            return [
                'class="alert alert-danger text-center"',
                'Artist could not be updated.'
            ]
        finally:
            # close the database connection
            Database().close_connection(connection)
