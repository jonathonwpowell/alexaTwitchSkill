import requests


# --------------- Helpers that build all of the responses ----------------------
# These helpers are from amazon


def build_speechlet_response(title, output, reprompt_text, should_end_session):
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
    return {
        'version': '1.0',
        'sessionAttributes': session_attributes,
        'response': speechlet_response
    }


# ---------------------- Twitch Auth Helpers--------------------------------------
def get_twitch_auth(session):
    raise NotImplementedError
    # TODO


# ------------------------Twitch API Helpers -------------------------------------
def twitch_top_streamers(num_of_responses):
    api_info = get_twitch_api_info()
    url = api_info['base_api_url'] + api_info['top_streams']
    headers = {"Accept": "application/json", "Client-ID": api_info['Client-ID']}

    api_response = requests.get(url, headers=headers)
    json = api_response.json()

    streams = ""
    for num in range(0, num_of_responses):
        streams = streams + " " + json['streams'][num]['channel']['display_name']

    return streams


def twitch_my_top_streamers(num_of_response, auth_info):
    return "Not implemented yet"
    # TODO


def twitch_game_top_streamers(num_of_response, game):
    return "Not implemented yet"
    # TODO


def get_twitch_api_info():
    api_info = {
        "Client-ID": "fq5m7globoglp4zanbya8c4r5q8e1i",
        "base_api_url": "https://api.twitch.tv/kraken/",
        "top_streams": "streams",
        "top_game_streams": "streams/?game={}",
        "my_top_streams": "/followed"
    }
    return api_info


# --------------- Functions that modify behavior --------------------------------

def get_welcome_response(session):
    # TODO tell user if they are authenticated
    session_attributes = {}
    card_title = "Welcome to the My Twitch Streams Alexa Skill"
    speech_output = "Welcome to the My Twitch streams app. To use please to do"
    reprompt_text = "To use this skill, please todo"
    should_end_session = False

    return build_response(session_attributes,
                          build_speechlet_response(card_title, speech_output, reprompt_text, should_end_session))


def get_end_response():
    session_attributes = {}
    card_title = None
    speech_output = None
    reprompt_text = None
    should_end_session = True

    return build_response(session_attributes,
                          build_speechlet_response(card_title, speech_output, reprompt_text, should_end_session))


def get_top_streamers(session):
    num_of_streams = 5
    auth_info = get_twitch_auth(session)
    top_streamers = twitch_top_streamers(num_of_streams)

    session_attributes = {}
    card_title = "Top Twitch Streamers On Now"
    speech_output = "Here are the top {} streamers: {}".format(num_of_streams, top_streamers)
    reprompt_text = None
    should_end_session = False

    return build_response(session_attributes,
                          build_speechlet_response(card_title, speech_output, reprompt_text, should_end_session))


def get_my_top_streamers(session):
    num_of_streams = 5

    auth_info = get_twitch_auth(session)
    my_top_streamers = twitch_my_top_streamers(num_of_streams, auth_info)

    session_attributes = {}
    card_title = "Top Twitch Streamers On Now"
    speech_output = "Here are your top {} streamers: {}".format(num_of_streams, my_top_streamers)
    reprompt_text = None
    should_end_session = False

    return build_response(session_attributes,
                          build_speechlet_response(card_title, speech_output, reprompt_text, should_end_session))


def get_game_top_streamers(request, session):
    num_of_streams = 5
    game = request['intent']['slots']['Game']['value']
    streamers = twitch_game_top_streamers(num_of_streams, game)

    session_attributes = {}
    card_title = "Top Twitch Streamers On Now"
    speech_output = "Here are the top {} streamers for {}: {}".format(num_of_streams, game, streamers)
    reprompt_text = None
    should_end_session = False

    return build_response(session_attributes,
                          build_speechlet_response(card_title, speech_output, reprompt_text, should_end_session))


# ---------------------------- Events -------------------------------------------

def on_intent(request, session):
    intent_name = request['intent']['name']
    log_action("Intent ({})".format(intent_name), request, session)

    if intent_name == "GetMyStreams":
        return get_my_top_streamers(session)
    elif intent_name == "GetTopStreams":
        return get_top_streamers(session)
    elif intent_name == "GetTopStreamsByGame":
        return get_game_top_streamers(request, session)
    elif intent_name == "AMAZON.CancelIntent" or intent_name == "AMAZON.StopIntent":
        return get_end_response()
    else:
        print ("Invalid intent passed in: {}".format(intent_name))
        raise ValueError("Invalid intent: " + intent_name)


def on_launch(request, session):
    log_action("Launch", request, session)
    return get_welcome_response(session)


def on_end(request, session):
    log_action("End session", request, session)
    return get_end_response()


# ---------------------------- Logging ------------------------------------------
def log_action(action, request, session):
    print("{}: requestId={}, sessionId={}".format(action, request['requestId'], session['sessionId']))


# -------------------------- Main -----------------------------------------------
def lambda_handler(event, context):
    print("event.session.application.applicationId=" +
          event['session']['application']['applicationId'])

    # confirm the API call is from the expected skill
    # if (event['session']['application']['applicationId'] !=
    #         "amzn1.ask.skill.d84e53f8-eec2-48fd-a22e-f31f16177f8c"):
    #     raise ValueError("Invalid Application ID")

    if event['session']['new']:
        log_action("New Session", event['request'], event['session'])

    if event['request']['type'] == "LaunchRequest":
        return on_launch(event['request'], event['session'])
    elif event['request']['type'] == "IntentRequest":
        return on_intent(event['request'], event['session'])
    elif event['request']['type'] == "SessionEndedRequest":
        return on_end(event['request'], event['session'])
    else:
        raise ValueError("Invalid request: " + event['request']['type'])
