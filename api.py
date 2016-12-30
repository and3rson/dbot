# -*- coding: utf-8 -*-
import urllib
import urllib2
import json
from bs4 import BeautifulSoup as BS
from log import logger
from time import sleep


class Remote(object):
    def __init__(self, url=None):
        self.opener = urllib2.build_opener()
        self.opener.addheaders = [('User-Agent', self.__class__.USER_AGENT)]

    def _request(self, url, **kwargs):
        logger.debug('Fetching %s', url)
        response = self.opener.open(
            self.__class__.BASE_URL.rstrip('/') + '/' + url.lstrip('/') + '?' + urllib.urlencode(kwargs)
        )
        return response.read()

    def _json_request(self, url, **kwargs):
        return json.loads(self._request(url, **kwargs))

    def _html_request(self, url, **kwargs):
        return BS(self._request(url, **kwargs), 'html.parser')


class DotaBuffAPI(Remote):
    BASE_URL = 'https://www.dotabuff.com/'
    USER_AGENT = 'Mozilla/1.22 (compatible; MSIE 2.0; Windows 3.1)'

    def __init__(self, debug=False):
        super(DotaBuffAPI, self).__init__()
        self.debug = debug
        self.tracks = {}
        self.last_known_matches = {}

    def get_matches(self, profile_id, reverse=False):
        doc = self._html_request('players/{}/matches'.format(
            profile_id
        ))

        matches = doc.select('article > table tbody tr')
        if reverse:
            matches = reversed(matches)

        for tr in matches:
            yield MatchInfoBasic(
                int(tr.select('td')[1].select_one('a')['href'].strip('/').split('/')[-1]),
                tr.select('td')[1].select_one('a').text,
                tr.select('td')[3].select_one('a').text.lower() == 'won match',
                tr.select('td')[5].text,
                tr.select('td')[6].select_one('span').text
            )

    def get_match(self, match_id):
        doc = self._html_request('matches/{}'.format(
            match_id
        ))
        match_result = 'radiant' if 'radiant' in doc.select_one('.match-result.team').text.lower() else 'dire'

        players = [], []

        for side_id, side in enumerate(doc.select('.team-results > section')):
            for tr in side.select('tbody tr'):
                player_td = tr.select_one('.tf-pl')
                a = player_td.select_one('a')
                if a:
                    profile_id = int(a['href'].strip('/').split('/')[-1])
                    nickname = a.text
                else:
                    profile_id = '?'
                    nickname = u'Анонім'
                players[side_id].append(PlayerOccurence(
                    profile_id,
                    nickname,
                    tr.select_one('.cell-fill-image').select_one('a img')['title'],
                    [el.text for el in tr.select('.tf-r.r-group-1')]
                ))

        return MatchInfo(match_id, match_result, players)

    def find_our_guys(self, chat_id, match):
        for profile_id in self.tracks[chat_id]:
            logger.error('Matching %s...', profile_id)
            if profile_id in [po.profile_id for po in match.players[0]]:
                return 'radiant', match.winner == 'radiant'
            elif profile_id in [po.profile_id for po in match.players[1]]:
                return 'dire', match.winner == 'dire'
        raise AssertionError('What the actual fuck?')

    def track(self, group_id, profile_id):
        if group_id not in self.tracks:
            self.tracks[group_id] = []
        if profile_id not in self.tracks:
            self.tracks[group_id].append(profile_id)

    def init(self):
        logger.info('Initial poll...')
        for group_id, profile_ids in self.tracks.items():
            for profile_id in profile_ids:
                matches = self.get_matches(profile_id)
                if self.debug:
                    # Skip first to simulate successful match
                    matches.next()
                self.last_known_matches[profile_id] = matches.next()
        logger.info('Ready')

    def poll(self, group_id):
        history = []
        for profile_id in self.tracks[group_id]:
            last_known_match = self.last_known_matches[profile_id]
            for match in self.get_matches(profile_id, reverse=True):
                if match.id > last_known_match.id:
                    self.last_known_matches[profile_id] = match
                    if match.id in history:
                        continue
                    history.append(match.id)
                    yield match


class MatchInfoBasic(object):
    def __init__(self, id, hero, result, duration, kda):
        self.id = id
        self.hero = hero
        self.result = result
        self.duration = duration
        self.kda = kda

    def __repr__(self):
        return '<MatchInfoBasic id={id} hero={hero} result={result} duration={duration} kda={kda}>'.format(
            id=self.id,
            hero=self.hero,
            result=self.result,
            duration=self.duration,
            kda=self.kda
        )


class MatchInfo(object):
    def __init__(self, id, winner, players):
        self.id = id
        self.winner = winner
        self.players = players

    def __repr__(self):
        return '<MatchInfo winner={winner} players={players}>'.format(
            winner=self.winner,
            players=self.players
        )

    def get_url(self):
        return 'https://www.dotabuff.com/matches/{}'.format(self.id)


class PlayerOccurence(object):
    def __init__(self, profile_id, nickname, hero, kdan):
        self.profile_id = profile_id
        self.nickname = nickname
        self.hero = hero
        self.kda = kdan[0:3]
        self.nw = kdan[3]

    def get_kda_ratio(self):
        k, d, a = map(float, map(lambda x: x if x.isdigit() else '0', self.kda))
        d = d if d > 0 else 1
        return round((k + a) / d, 2)


if __name__ == '__main__':
    api = DotaBuffAPI(debug=True)
    # api.get_matches(48355300)
    api.track('@andunai', 48355300)
    api.track('@andunai', 90366968)
    api.track('@andunai', 104978674)
    api.init()

    while True:
        logger.info('Polling...')
        for match in api.poll('@andunai'):
            logger.info('Found new match: %s', match)
            print api.get_match(match.id)
        logger.info('Poll finished')
        sleep(20)


#     def search(self, query):
#         doc = self._html_request('search', q=query)
#         s = doc.prettify()

#         for result in doc.select('html > body > p'):
#             if result.select_one('> a[href^="/images"]'):
#                 continue
#             green_stuff = result.select_one('font[color="green"]')
#             if green_stuff:
#                 green_stuff.extract()
#             link = result.select_one('> a')
#             if link:
#                 # Result link
#                 text = result.select_one('> table td > font')
#                 kind = 'page'
#             # if result.senect_one('> table > tr > td')
#             else:
#                 # Youtube link
#                 link = result.select('> table > tr > td')[2].select_one('a')
#                 text = result.select('> table > tr > td')[2].select_one('font')
#                 kind = 'video'
#             yield SearchResult(
#                 self._unbox_link(link['href']),
#                 link.text,
#                 text.text,
#                 kind
#             )

#     def _unbox_link(self, url):
#         query = parse_qs(urlparse(url).query)
#         return query.get('q')[0]


# class SearchResult(object):
#     def __init__(self, url, title, description, kind):
#         self.url = url
#         self.title = title
#         self.description = description.replace('\n', ' ').replace('  ', ' ')
#         self.kind = kind

#     def __unicode__(self):
#         return self.title

#     def __repr__(self):
#         return unicode(self).encode('utf-8')
