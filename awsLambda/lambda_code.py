import requests


# --------------- Helpers that build all of the responses ----------------------
# These helpers are from amazon


def build_speechlet_response(title, output, reprompt_text, should_end_session):
    return {
        'outputSpeech': {
            'type': 'PlainText',
            'text': clean_return_for_TTS(output)
        },
        'card': {
            'type': 'Simple',
            'title': title,
            'content': output
        },
        'reprompt': {
            'outputSpeech': {
                'type': 'PlainText',
                'text': reprompt_text
            }
        },
        'shouldEndSession': should_end_session
    }


def build_login_card_response(title, output, reprompt_text, should_end_session):
    return {
        'outputSpeech': {
            'type': 'PlainText',
            'text': output
        },
        'card': {
            'type': 'LinkAccount',
            'title': title,
            'content': output
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
    if 'accessToken' in session['user']:
        return session['user']['accessToken']
    else:
        return None


# ------------------------Twitch API Helpers -------------------------------------
def twitch_top_streamers(num_of_responses):
    api_info = get_twitch_api_info()
    url = api_info['base_api_url'] + api_info['top_streams']
    headers = {"Accept": "application/json", "Client-ID": api_info['Client-ID']}

    api_response = requests.get(url, headers=headers)
    json = api_response.json()

    streams = ""
    for num in range(0, num_of_responses):
        if streams != "":
            streams = streams + ", "
        streams = streams + json['streams'][num]['channel']['display_name']

    return streams


def twitch_my_top_streamers(num_of_responses, auth_info):
    api_info = get_twitch_api_info()
    url = api_info['base_api_url'] + api_info['my_top_streams']
    headers = {"Accept": "application/json",
               "Client-ID": api_info['Client-ID'],
               "Authorization": "OAuth " + auth_info}

    api_response = requests.get(url, headers=headers)
    json = api_response.json()

    if 'streams' not in json:
        return None

    streams = ""
    i = 0

    while i < num_of_responses and i < len(json['streams']):
        if streams != "":
            streams = streams + ", "
        streams = streams + json['streams'][i]['channel']['display_name']
        i = i + 1

    if not streams:
        return 'no followed streams are live'

    return streams


def twitch_game_top_streamers(num_of_responses, game):
    api_info = get_twitch_api_info()
    url = api_info['base_api_url'] + api_info['top_game_streams'].format(game)
    headers = {"Accept": "application/json", "Client-ID": api_info['Client-ID']}

    api_response = requests.get(url, headers=headers)
    json = api_response.json()

    streams = ""
    for num in range(0, num_of_responses):
        if num < len(json['streams']):
            if streams != "":
                streams = streams + ", "
            streams = streams + json['streams'][num]['channel']['display_name']

    if not streams:
        return 'no streams are available'

    return streams


def get_twitch_api_info():
    api_info = {
        "Client-ID": "fq5m7globoglp4zanbya8c4r5q8e1i",
        "base_api_url": "https://api.twitch.tv/kraken/",
        "top_streams": "streams",
        "top_game_streams": "streams/?game={}",
        "my_top_streams": "streams/followed"
    }
    return api_info


# --------------- Functions that modify behavior --------------------------------

def get_welcome_response(session):
    if get_twitch_auth(session) is None:
        return get_login_card()

    session_attributes = {}
    card_title = "Welcome to the My Twitch Streams Alexa Skill"
    speech_output = "Welcome to the My Twitch streams skill. " \
                    "To get your available streams ask who is streaming. " \
                    "To get the top available streams ask what are the top streams. " \
                    "To get the top streams by game ask who is streaming League of Legends" \
        .format(get_skill_invocation_name())
    reprompt_text = None
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
    top_streamers = twitch_top_streamers(num_of_streams)

    session_attributes = {}
    card_title = "Top Twitch Streamers On Now"
    speech_output = "Here are the top available streamers: {}".format(top_streamers)
    reprompt_text = None
    should_end_session = True

    return build_response(session_attributes,
                          build_speechlet_response(card_title, speech_output, reprompt_text, should_end_session))


def get_my_top_streamers(session):
    num_of_streams = 5

    auth_info = get_twitch_auth(session)
    if auth_info is None:
        return get_login_card()

    my_top_streamers = twitch_my_top_streamers(num_of_streams, auth_info)

    if my_top_streamers is None:
        return get_login_card()

    session_attributes = {}
    card_title = "Your Twitch Streamers On Now"
    speech_output = "Here are your top available streamers: {}".format(my_top_streamers)
    reprompt_text = None
    should_end_session = True

    return build_response(session_attributes,
                          build_speechlet_response(card_title, speech_output, reprompt_text, should_end_session))


def get_game_top_streamers(request, session):
    num_of_streams = 5
    game = get_twitch_game_name(request['intent']['slots']['Game']['value'])

    if game is None:
        return get_invalid_game_response()

    streamers = twitch_game_top_streamers(num_of_streams, game)

    session_attributes = {}
    card_title = "Top Twitch Streamers On Now For {}".format(game)
    speech_output = "Here are the top available streamers for {}: {}".format(game, streamers)
    reprompt_text = None
    should_end_session = True

    return build_response(session_attributes,
                          build_speechlet_response(card_title, speech_output, reprompt_text, should_end_session))


def get_invalid_game_response():
    session_attributes = {}
    card_title = "Unknown game"
    speech_output = "Unknown game, please try again. Please note many games are not supported"
    reprompt_text = None
    should_end_session = False

    return build_response(session_attributes,
                          build_speechlet_response(card_title, speech_output, reprompt_text, should_end_session))


def get_login_card():
    session_attributes = {}
    card_title = "Register With Twitch"
    speech_output = "Thank you for using my twitch streams. " \
                    "Please register with your twitch account if you wish to get information about your followed streams. " \
                    "You can still get the top streams by asking what are the top streams, " \
                    "or get the top streams by game by asking who is streaming League of Legends" \
        .format(get_skill_invocation_name())
    reprompt_text = None
    should_end_session = False

    return build_response(session_attributes,
                          build_login_card_response(card_title, speech_output, reprompt_text, should_end_session))


def get_skill_invocation_name():
    return "my twitch streams"


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
    elif intent_name == "AMAZON.HelpIntent":
        return get_welcome_response(session)
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


# ------------------------- Game Name Conversion -----------------------
def get_twitch_game_name(game):
    name_dict = {}
    with open("twitchGameNameConversions.txt") as f:
        for line in f:
            (key, val) = line.split(",")
            name_dict[key.lower().strip()] = val.strip()

    if game.lower() in name_dict:
        return name_dict[game.lower().strip()]
    else:
        return None


# -----------------------------------TTS Conversions-------------------------------------
def clean_return_for_TTS(toConvert):
    if not toConvert:
        return ''

    temp = switch_names_for_TTS(toConvert)
    toReturn = remove_underscore_for_TTS(temp)
    return toReturn


def remove_underscore_for_TTS(toConvert):
    return toConvert.replace("_"," ")

# This is to change the name of the streamer to a way that Alexa TTS will say it correctly
def switch_names_for_TTS(toConvert):
    if toConvert is None:
        return None

    return_text = toConvert
    conversion_dict = {}

    with open("channelNameTTSConversion.txt") as f:
        print 'reading in name conversion file'
        for line in f:
            (key, val) = line.split(",")
            conversion_dict[key.strip()] = val.strip()

    for display_name in conversion_dict:
        if display_name in return_text:
            return_text = return_text.replace(display_name, conversion_dict[display_name])

    return return_text