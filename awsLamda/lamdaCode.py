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

# --------------- Functions that modify behavior --------------------------------

def get_welcome_response():
    session_attributes = {}
    card_title = "Welcome to the My Twitch Streams Alexa Skill"
    speech_output = "Welcome to the My Twitch streams app. To use please to do"
    reprompt_text = "To use this skill, please todo"
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(card_title,speech_output,reprompt_text, should_end_session))



# ---------------------------- Events -------------------------------------------

def on_intent(request, session):
    intent = request['intent']
    intent_name = request['intent']['name']
    log_action("Intent ({})".format(intent_name), request, session)

    #TODO handle intents



def on_launch(request, session):
    log_action("Launch",request,session)

def on_end(request, session):
    #TODO: cleanup?
    log_action("End session",request,session)
# ---------------------------- Logging ------------------------------------------
def log_action(action,request, session):
    print("{}: requestId={}, sessionId={}".format(action,request['requestId'], session['sessionId']))
# -------------------------- Main -----------------------------------------------
def lambda_handler(event, context):

    print("event.session.application.applicationId=" +
          event['session']['application']['applicationId'])

    #confirm the API call is from the expected skill
    #TODO: switch this to the new skill id
    if (event['session']['application']['applicationId'] !=
             "amzn1.ask.skill.d84e53f8-eec2-48fd-a22e-f31f16177f8c"):
        raise ValueError("Invalid Application ID")

    if event['session']['new']:
        log_action("New Session",event['request'], event['session'])

    if event['request']['type'] == "LaunchRequest":
        return on_launch(event['request'], event['session'])
    elif event['request']['type'] == "IntentRequest":
        return on_intent(event['request'], event['session'])
    elif event['request']['type'] == "SessionEndedRequest":
        return on_end(event['request'], event['session'])
