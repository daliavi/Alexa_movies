'''
Lambda function to get movie showtimes
'''
from datetime import datetime, timedelta
from service import SpeechService, APIService
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
    speech_output = "Hi there! I can help you to find movie showtimes around you. What is your ZIP code?"
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
    session_attributes = {}


def get_zip(intent, session):
    """ Get users zip code.
    """
    card_title = 'Popular Movies'
    should_end_session = False
    speech_output = ''
    reprompt_text = ''

    if 'zip' in intent['slots'] and intent['slots']['zip']['value'].isdigit():
        zip_code = intent['slots']['zip']['value']
        session_attributes['zip'] = zip_code

        if 'date' not in session_attributes:
            tomorrow_date = datetime.now() + timedelta(days=1)
            tomorrow_date = tomorrow_date.strftime('%Y-%m-%d')
            session_attributes['date'] = tomorrow_date

        movies_by_zip = APIService.get_movies_by_zip(session_attributes['zip'],
                                                     session_attributes['date'])
        print 'movies by zip: ', movies_by_zip

        speech_output = SpeechService.movies_by_zip(movies_by_zip)

        reprompt_text = "If you want to hear showtimes say movie title and the name of the cinema. " \
                              "For example, say: showtimes for Spiderman at Presidio theatre for tonight."
    else:
        speech_output = "I did not understand your zip code. " \
                        "Please repeat your zip code."
        reprompt_text = "Please repeat your zip code."

    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


def get_showtimes(intent, session):
    card_title = 'Showtimes'
    should_end_session = False
    speech_output = ''
    reprompt_text = ''

    if 'date' in intent['slots']:
        session_attributes['date'] = intent['slots']['date']['value']
    else:
        tomorrow_date = datetime.now() + timedelta(days=1)
        tomorrow_date = tomorrow_date.strftime('%Y-%m-%d')
        session_attributes['date'] = tomorrow_date
        session_attributes['date'] = datetime.now().strftime('%Y-%m-%d')

    if 'movie' in intent['slots'] and 'cinema' in intent['slots'] and 'zip' in session_attributes:
        movie = intent['slots']['movie']['value']
        session_attributes['movie'] = movie.lower()

        cinema = intent['slots']['cinema']['value']
        session_attributes['cinema'] = cinema.lower()

        showtimes = APIService.get_movie_data(
            session_attributes['zip'],
            session_attributes['date'],
            session_attributes['movie'],
            session_attributes['cinema'])

        print 'printing showtimes: ', showtimes

        speech_output = SpeechService.movie_showtimes(showtimes, session_attributes['date'])
        reprompt_text = "To hear other showtimes say movie title and the name of the cinema." \
                        "For example, say: showtimes for Xmen at Marina theatre on Saturday."
    elif 'zip' not in session_attributes:
        speech_output = "hmm... it seems I don't have your zip code. Please say what is your zip code?"
        reprompt_text = "Are you still there? What is your ZIP code?"

    elif 'movie' not in intent['movie']:
        speech_output = "I did not understand the movie. Please try again. " \
                        "To hear showtimes say movie title and the name of the cinema. " \
                        "For example, say: showtimes for Lion King at New York theatre for tonight."
        reprompt_text = "To hear showtimes say movie title and the name of the cinema. " \
                        "For example, say: showtimes for Finding Nemo at Century San Francisco tomorrow."
    elif 'cinema' not in intent['cinema']:
        speech_output = "I did not understand the name of the cinema. Please try again. " \
                        "To hear showtimes say movie title and the name of the cinema. " \
                        "For example, say: showtimes for Lion King at New York theatre for tonight."
        reprompt_text = "To hear showtimes say movie title and the name of the cinema. " \
                        "For example, say: showtimes for Finding Nemo at Century San Francisco tomorrow."
    else:
        speech_output = "I could not find showtimes for" + \
                        session_attributes['movie'] + " at " + \
                        session_attributes['cinema'] + " for today. Please try again!"
        reprompt_text = "Say: showtimes for movie at theatre"

    return build_response(session_attributes, build_speechlet_response(
    card_title, speech_output, reprompt_text, should_end_session))


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
