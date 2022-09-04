"""Views for the search app."""

import json
import logging
from http import client
from pprint import pformat
from typing import Any

from django.conf import settings
from django.http import JsonResponse


def _words_api(word: str) -> dict:
    """
    Pass a request to Words API and return the parsed results as a dictionary.

    Example response from Words API:
    {
      'word': 'opinion',
      'definitions': [
        {
          'definition': "the reason for a court's judgment",
          'partOfSpeech': 'noun'
        },
        {
          'definition': 'the legal document stating the reasons for a judicial decision',
          'partOfSpeech': 'noun'
        },
        {
          'definition': 'a personal belief not founded on proof or certainty',
          'partOfSpeech': 'noun'
        }
      ]
    }

    Example return value:
    {
      'word': 'opinion',
      'meanings': {
        'noun': {
          'definitions': [
            {
              'definition': "the reason for a court's judgment"
            },
            {
              'definition': 'the legal document stating the reasons for a judicial decision'
            },
            {
              'definition': 'a personal belief not founded on proof or certainty'
            }
          ]
        }
      }
    }
    """
    host = 'wordsapiv1.p.rapidapi.com'
    request_url = f'/words/{word}/definitions'
    headers = {
        'x-rapidapi-key': settings.RAPIDAPI_KEY,
        'x-rapidapi-host': host,
    }
    connection = client.HTTPSConnection(host)  # noqa: S309
    connection.request('GET', request_url, headers=headers)
    logging.debug(f'Made Words API request to {request_url}...')
    data = json.loads(connection.getresponse().read().decode('utf-8'))
    logging.info(f'Received response from Words API: {data}')
    parsed_data: dict[str, Any] = {}
    for result in data.get('definitions', []):
        part_of_speech = result['partOfSpeech']
        definition = {'definition': result['definition']}
        if parsed_data.get(part_of_speech):
            parsed_data[part_of_speech].append(definition)
        else:
            parsed_data[part_of_speech] = [definition]
    return parsed_data


def _google_dict_api(word: str) -> dict:
    """
    Return a response from Google Dictionary API.

    Example response:
    [
        {
            "word": "opinion",
            "phonetics": [
                {
                    "text": "/həˈloʊ/",
                    "audio": "https://lex-audio.useremarkable.com/mp3/hello_us_1_rr.mp3"
                },
                {
                    "text": "/hɛˈloʊ/",
                    "audio": "https://lex-audio.useremarkable.com/mp3/hello_us_2_rr.mp3"
                }
            ],
            "meanings": [
                {
                    "partOfSpeech": "exclamation",
                    "definitions": [
                        {
                            "definition": "Used as a greeting or to begin a phone conversation.",
                            "example": "hello there, Katie!"
                        }
                    ]
                },
                {
                    "partOfSpeech": "noun",
                    "definitions": [
                        {
                            "definition": "An utterance of “hello”; a greeting.",
                            "example": "she was getting polite nods and hellos from people",
                            "synonyms": [
                                "greeting",
                                "welcome",
                                "salutation",
                                "saluting",
                                "hailing",
                                "address",
                                "hello",
                                "hallo"
                            ]
                        }
                    ]
                },
                {
                    "partOfSpeech": "intransitive verb",
                    "definitions": [
                        {
                            "definition": "Say or shout “hello”; greet someone.",
                            "example": "I pressed the phone button and helloed"
                        }
                    ]
                }
            ]
        }
    ]

    """
    host = 'api.dictionaryapi.dev'
    request_url = f'/api/v2/entries/en/{word}'
    connection = client.HTTPSConnection(host)  # noqa: S309
    connection.request('GET', request_url)
    data = json.loads(connection.getresponse().read().decode('utf-8'))
    logging.info(f'Received response from Google Dictionary API: {pformat(data)}')
    return data


def word_search(request, word: str) -> JsonResponse:
    """Pass a request to Words API and return the results as JSON."""
    use_words_api = True
    if use_words_api:
        data = _words_api(word)
    else:
        data = _google_dict_api(word)
    return JsonResponse(data)
