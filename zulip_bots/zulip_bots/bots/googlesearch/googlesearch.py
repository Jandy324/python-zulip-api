# See readme.md for instructions on running this code.
from __future__ import print_function
import logging
from six.moves.urllib import parse

import requests

from bs4 import BeautifulSoup

def google_search(keywords):
    query = {'q': keywords}
    # Gets the page
    page = requests.get('http://www.google.com/search', params=query)
    # Parses the page into BeautifulSoup
    soup = BeautifulSoup(page.text, "lxml")

    # Gets all search URLs
    anchors = soup.find(id='search').findAll('a')
    results = []

    for a in anchors:
        try:
            # Tries to get the href property of the URL
            link = a['href']
        except KeyError:
            continue
        # Link must start with '/url?', as these are the search result links
        if (not link.startswith('/url?')):
            continue
        # Makes sure a hidden 'cached' result isn't displayed
        if (a.text.strip() == 'Cached' and 'webcache.googleusercontent.com'):
            continue
        if (a.text.strip() == ''):
            continue
        # a.text: The name of the page
        result = {'url': "https://www.google.com{}".format(link),
                  'name': a.text}
        results.append(result)
    return results

def get_google_result(search_keywords):
    help_message = "To use this bot, start messages with @mentioned-bot, \
                    followed by what you want to search for. If \
                    found, Zulip will return the first search result \
                    on Google.\
                    \
                    An example message that could be sent is:\
                    '@mentioned-bot zulip' or \
                    '@mentioned-bot how to create a chatbot'."

    search_keywords = search_keywords.strip()

    if search_keywords == 'help':
        return help_message
    elif search_keywords == '' or search_keywords is None:
        return help_message
    else:
        try:
            results = google_search(search_keywords)
            if (len(results) == 0):
                return "Found no results."
            return "Found Result: [{}]({})".format(results[0]['name'], results[0]['url'])
        except ConnectionError as c_err:
            return "Error: Failed to connect. {}.".format(c_err)
        except AttributeError as a_err:
            # google.search query failed and urls is of object
            # 'NoneType'
            logging.exception(a_err)
            return "Error: Google search failed with a NoneType result. {}.".format(a_err)
        except TypeError as t_err:
            # google.search query failed and returned None
            # This technically should not happen but the prior
            # error check assumed this behavior
            logging.exception(t_err)
            return "Error: Google search function failed. {}.".format(t_err)
        except Exception as e:
            return 'Error: Search failed. {}.'.format(e)

class GoogleSearchHandler(object):
    '''
    This plugin allows users to enter a search
    term in Zulip and get the top URL sent back
    to the context (stream or private) in which
    it was called. It looks for messages starting
    with @mentioned-bot.
    '''

    def usage(self):
        return '''
            This plugin will allow users to search
            for a given search term on Google from
            Zulip. Use '@mentioned-bot help' to get
            more information on the bot usage. Users
            should preface messages with
            @mentioned-bot.
            '''

    def handle_message(self, message, bot_handler):
        original_content = message['content']
        result = get_google_result(original_content)
        bot_handler.send_reply(message, result)

handler_class = GoogleSearchHandler
