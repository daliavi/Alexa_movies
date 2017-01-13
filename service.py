import requests
from datetime import datetime
from keys import API_KEY
from test_data import DATA


class SpeechService(object):

    @classmethod
    def movie_showtimes(self, showtimes_dict, date):
        speech = ''
        was_missing = False
        if showtimes_dict:
            for movie, showtimes in showtimes_dict.iteritems():
                if showtimes:
                    if was_missing:
                        speech = 'The showtimes for ' + movie
                    else:
                        speech += 'The showtimes for ' + movie
                    for theatre, times in showtimes.iteritems():
                        t = ', '.join(times)
                        speech = speech + ' at ' + theatre
                    speech = speech + ' for ' + date + ' are: ' + t + '. '
                else:
                    # could not find showtimes
                    was_missing = True
                    speech = 'I could not find any showtimes in the location you asked. ' \
                         'To hear showtimes in a different cinema, say movie title and the name of the cinema. ' \
                         'For example, say: showtimes for Doctor Strange at Van Ness cinema on Friday.'
        else:
            # could not find the movie
            speech = 'I could not find the movie you asked for. ' \
                     'To hear showtimes say movie title and the name of the cinema. ' \
                     'For example, say: showtimes for Trolls at Sundance  cinema on Friday.'

        return speech

    @classmethod
    def movies_by_genre(self, movies_dict):
        speech = ''
        for movie, cinemas in movies_dict.iteritems():
            speech += ' The movie, ' + movie + ', is showing at:'
            for cinema in cinemas:
                speech += ' ' + cinema + ','
            speech = speech[:-1] + '.'
        return speech

    @classmethod
    def movies_by_zip(self, movies_dict):
        if movies_dict:
            speech = 'Here is some popular movies playing in your area: '

            for movie, showtimes in movies_dict.iteritems():
                if len(showtimes) > 4:
                    speech = speech + movie + ', '
            speech = speech[:-2] + '. '
            speech += "If you want to hear showtimes say movie title and the name of the cinema. " \
                              "For example, say: showtimes for Spiderman at Presidio theatre for tonight."
        else:
            speech = 'I could not find any movies in your area. Please tell me again your zip code?'
        return speech


class APIService(object):

    @classmethod
    def get_movie_data(self,
                       zip_code,
                       start_date,
                       given_movie,
                       given_cinema):
        if not DATA:
            data = DATA
        else:
            payload = {'api_key': API_KEY,
                       'startDate': start_date,
                       'zip': zip_code
                       }
            url = 'http://data.tmsapi.com/v1.1/movies/showings'
            r = requests.get(url, params=payload)
            print r.url
            data = r.json()
        print data
        print "*****************"
        cin_movie_dict = {}

        for i in data:
            try:
                if given_movie.lower() in i['title'].lower():
                    cinema_dict = {}
                    for s in i['showtimes']:
                        if given_cinema.lower() in s['theatre']['name'].lower():
                            if s['dateTime'] > datetime.now().isoformat():
                                t = s['dateTime'].split('T')[1]
                                d = datetime.strptime(t, "%H:%M")
                                d = d.strftime("%I:%M %p")
                                if s['theatre']['name'] in cinema_dict:
                                    cinema_dict[s['theatre']['name']].append(d)
                                else:
                                    cinema_dict[s['theatre']['name']] = [d]
                    cin_movie_dict[i['title']] = cinema_dict
            except KeyError:
                pass
            except TypeError:
                return {}
            except:
                return {}
        return cin_movie_dict

    @classmethod
    def get_movies_by_zip(self, zip_code, start_date):
        print "###### entered get_movies_by_zip"
        print 'zip: ', zip_code
        print 'date: ', start_date
        if not DATA:
            data = DATA
        else:
            payload = {'api_key': API_KEY,
                       'startDate': start_date,
                       'zip': zip_code
                       }
            url = 'http://data.tmsapi.com/v1.1/movies/showings'
            r = requests.get(url, params=payload)
            print r.url
            data = r.json()
            print data
            print "zzzzzzzzzzzzzzz"
        movies_for_zip = {}
        for i in data:
            try:
                for s in i['showtimes']:
                    if s['dateTime'] > datetime.now().isoformat():
                        if i['title'] in movies_for_zip:
                            movies_for_zip[i['title']].add(s['theatre']['name'])
                        else:
                            movies_for_zip[i['title']] = set()
                            movies_for_zip[i['title']].add(s['theatre']['name'])
            except KeyError:
                pass
            except TypeError:
                return {}
            except:
                return {}
        return movies_for_zip

    @classmethod
    def get_movies_by_zip_genre(self, zip_code, start_date, genre):
        if not DATA:
            data = DATA
        else:
            payload = {'api_key': API_KEY,
                       'startDate': start_date,
                       'zip': zip_code
                       }
            url = 'http://data.tmsapi.com/v1.1/movies/showings'
            r = requests.get(url, params=payload)
            print r.url
            data = r.json()
        print "*****************"
        movies_for_zip_genre = {}
        for i in data:
            try:
                for s in i['showtimes']:
                    if s['dateTime'] > datetime.now().isoformat() and genre in i['genres']:
                        if i['title'] in movies_for_zip_genre:
                            movies_for_zip_genre[i['title']].add(s['theatre']['name'])
                        else:
                            movies_for_zip_genre[i['title']] = set()
                            movies_for_zip_genre[i['title']].add(s['theatre']['name'])
            except KeyError:
                pass
        return movies_for_zip_genre

