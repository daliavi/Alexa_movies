'''
Lambda function to get movie showtimes
'''
import requests
session_attributes = {}


# --------------- Helpers that build all of the responses ----------------------

def build_speechlet_response(title, output, reprompt_text, should_end_session):
    print "entered speechelet response"
    print 'text', output
    print 'title', title
    print 'reprompt', reprompt_text
    return {
        'outputSpeech': {
            'type': 'PlainText',
            'text': output
        },
        'card': {
            'type': 'Simple',
            'title': "SessionSpeechlet - " + title,
            'content': "SessionSpeechlet - " + output
        },
        'reprompt': {
            'outputSpeech': {
                'type': 'PlainText',
                'text': reprompt_text
            }
        },
        'shouldEndSession': should_end_session
    }


def build_response(session_attributes, speechlet_response):
    print "entered build response"
    return {
        'version': '1.0',
        'sessionAttributes': session_attributes,
        'response': speechlet_response
    }
# --------------- Functions that control the skill's behavior ------------------

def get_welcome_response():
    """ If we wanted to initialize the session to have some attributes we could
    add those here
    """

    session_attributes = {}
    card_title = "Welcome"
    speech_output = "Hi there! So you feel like a movie? " \
                    "Let me see what is showing in your area." \
                    "What is your ZIP code?"
    # If the user either does not reply to the welcome message or says something
    # that is not understood, they will be prompted again with this text.
    reprompt_text = "Please tell me your ZIP code."
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


def handle_session_end_request():
    card_title = "Session Ended"
    speech_output = "Cheers! Enjoy your movie, or whatever you decide to do!"
    # Setting this to true ends the session and exits the skill.
    should_end_session = True
    return build_response({}, build_speechlet_response(
        card_title, speech_output, None, should_end_session))

# --------------- Events ------------------

def on_session_started(session_started_request, session):
    """ Called when the session starts """

    print("on_session_started requestId=" + session_started_request['requestId']
          + ", sessionId=" + session['sessionId'])


def on_launch(launch_request, session):
    """ Called when the user launches the skill without specifying what they
    want
    """

    print("on_launch requestId=" + launch_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    # Dispatch to your skill's launch
    return get_welcome_response()


def on_intent(intent_request, session):
    """ Called when the user specifies an intent for this skill """

    print("on_intent requestId=" + intent_request['requestId'] +
          ", sessionId=" + session['sessionId'])

    intent = intent_request['intent']
    intent_name = intent_request['intent']['name']

    # Dispatch to your skill's intent handlers
    if intent_name == "get_zip":
        return get_zip(intent, session)
    elif intent_name == "get_genre":
        return get_genre(intent, session)
    elif intent_name == "get_date":
        return get_date(intent, session)
    elif intent_name == "get_showtimes":
        return get_showtimes(intent,session)
    elif intent_name == "AMAZON.HelpIntent":
        return get_welcome_response()
    elif intent_name == "AMAZON.CancelIntent" or intent_name == "AMAZON.StopIntent":
        return handle_session_end_request()
    else:
        raise ValueError("Invalid intent")


def on_session_ended(session_ended_request, session):
    """ Called when the user ends the session.

    Is not called when the skill returns should_end_session=true
    """
    print("on_session_ended requestId=" + session_ended_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    # add cleanup logic here


def get_zip(intent, session):
    """ Get users zip code.
    """
    card_title = intent['name']
    should_end_session = False

    if 'zip' in intent['slots'] and intent['slots']['zip']['value'].isdigit():
        print "passed get_zip intent if statement!!!"
        zip_code = intent['slots']['zip']['value']
        session_attributes['zip'] = zip_code
        speech_output = "Great! I will check movies near " + \
                        zip_code + \
                        " zip code. What movie genre do you prefer? " \
                        "Say Action, Drama, Comedy, Children or any kind "
        reprompt_text = "Are you still there? What movie genre would you like? " \
                        "Say Action, Drama, Comedy, Children or any kind "
    else:
        speech_output = "I did not understand the movie genre you wanted. " \
                        "Say Action, Drama, Comedy, Children or any kind "
        reprompt_text = "Are you still there? What movie genre would you like? " \
                        "Say Action, Drama, Comedy, Children or any kind "

    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


def get_showtimes(intent, session):
    card_title = intent['name']
    should_end_session = False
    session_attributes['date'] = '2016-11-12'

    if 'movie' in intent['slots'] and 'cinema' in intent['slots']:
        movie = intent['slots']['movie']['value']
        session_attributes['movie'] = movie

        cinema = intent['slots']['cinema']['value']
        session_attributes['cinema'] = cinema

        showtimes = get_movie_data(session_attributes['zip'],
                       session_attributes['date'])
        movie_showtimes = showtimes['movie']
        cinema_showtimes = movie_showtimes['cinema']
        showtimes_str = ','.join(cinema_showtimes)

        speech_output = "Here are the showtimes for " + \
                        movie + " at " + cinema + "for today. " + showtimes_str + \
                        " If you want to hear different movie, say the title and the cinema."
        reprompt_text = "Are you still there? What movie genre would you like? " \
                    "Say Action, Drama, Comedy, Children or any kind "
    else:
        speech_output = "I did not understand the movie or cinema."
        reprompt_text = "I did not understand the movie or cinema."

    return build_response(session_attributes, build_speechlet_response(
    card_title, speech_output, reprompt_text, should_end_session))

def get_date(intent, session):
    """ Get users prefered genre.
    """
    card_title = intent['name']
    should_end_session = False

    if 'date' in intent['slots']:
        #TODO check if the date is valid
        date = intent['slots']['date']['value']
        print 'date: ', date
        session_attributes['date'] = date
        speech_output = "OK, so you want to see movies showing on " + date
        reprompt_text = "Please tell me the date"
    else:
        speech_output = "I did not understand the date. " \
                        "Please try again."
        reprompt_text = "Please tell me teh date"
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


def get_genre(intent, session):
    """ Get users prefered genre.
    """
    card_title = intent['name']
    should_end_session = False

    if 'genre' in intent['slots']:
        #TODO check if valid zip code
        genre = intent['slots']['genre']['value']
        session_attributes = {'genre': genre}
        speech_output = "OK, so you like " + \
                        genre + " movies"
        reprompt_text = "Please tell me your zip code."
    else:
        speech_output = "I did not understand the zip code. " \
                        "Please try again."
        reprompt_text = "Please tell me your zip code." \
                        "It is a 5 digit number used everywhere in the united States "
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


def get_movie_data(zip_code, start_date):
    payload = {'api_key': 'nxmfat6d9p9fnt5qwx85kvaj',
               'startDate': start_date,
               'zip': zip_code
               }
    url = 'http://data.tmsapi.com/v1.1/movies/showings'
    r = requests.get(url, params=payload)
    data = r.json()
    cin_movie_dict = {}

    show_times = []

    for i in data[:6]:
        try:
            cinema_dict = {}
            for s in i['showtimes']:
                if s['theatre']['name'] in cinema_dict:
                    cinema_dict[s['theatre']['name']].append(s['dateTime'].split('T')[1])
                else:
                    cinema_dict[s['theatre']['name']] = [s['dateTime'].split('T')[1]]
            cin_movie_dict[i['title']] = cinema_dict
        except KeyError:
            pass

    return cin_movie_dict



# --------------- Main handler ------------------

def lambda_handler(event, context):
    """ Route the incoming request based on type (LaunchRequest, IntentRequest,
    etc.) The JSON body of the request is provided in the event parameter.
    """
    print("event.session.application.applicationId=" +
          event['session']['application']['applicationId'])

    """
    Uncomment this if statement and populate with your skill's application ID to
    prevent someone else from configuring a skill that sends requests to this
    function.
    """
    # if (event['session']['application']['applicationId'] !=
    #         "amzn1.echo-sdk-ams.app.[unique-value-here]"):
    #     raise ValueError("Invalid Application ID")

    if event['session']['new']:
        on_session_started({'requestId': event['request']['requestId']},
                           event['session'])

    if event['request']['type'] == "LaunchRequest":
        return on_launch(event['request'], event['session'])
    elif event['request']['type'] == "IntentRequest":
        return on_intent(event['request'], event['session'])
    elif event['request']['type'] == "SessionEndedRequest":
        return on_session_ended(event['request'], event['session'])
