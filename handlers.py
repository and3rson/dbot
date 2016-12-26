# -*- coding: utf-8 -*-
from telegram import ChatAction
import settings
from terminaltables import AsciiTable
from log import logger
from api import DotaBuffAPI
# from redis import Redis


class DotaBuffPollJob(object):
    def __init__(self):
        self.__name__ = 'DotaBuffPollJob'

        self.api = DotaBuffAPI(debug=False)
        # api.get_matches(48355300)
        self.api.track(settings.CHAT_ID, 48355300)
        self.api.track(settings.CHAT_ID, 90366968)
        self.api.track(settings.CHAT_ID, 104978674)
        self.api.track(settings.CHAT_ID, 31563138)
        self.api.track(settings.CHAT_ID, 87255844)
        self.api.init()

    def unite(self, parts):
        if len(parts) == 1:
            return parts[0]
        elif len(parts) == 2:
            return u' і '.join(parts)
        else:
            return u' і '.join((
                u', '.join(parts[:-1]),
                parts[-1]
            ))

    def pluralize(self, forms, count):
        return forms[1 if count > 1 else 0]

    def trim(self, s, maxlen, ellipsis='..'):
        return s[:maxlen] + (s[maxlen:] and ellipsis)

    def __call__(self, bot, job):
        # logger.info('call: %s %s', bot, job)
        logger.info('Polling...')
        for match in self.api.poll(settings.CHAT_ID):
            logger.info('Found new match: %s', match)
            match = self.api.get_match(match.id)
            team, is_winner = self.api.find_our_guys(settings.CHAT_ID, match)
            all_members = match.players[0] + match.players[1]

            our_guys = filter(lambda po: po.profile_id in self.api.tracks[settings.CHAT_ID], all_members)
            our_guys_names = [u'{} ({})'.format(po.nickname, po.hero) for po in our_guys]

            summary = u'{members} щойно *{what}*{in_solo}.'.format(
                members=self.unite(our_guys_names),
                what=self.pluralize((u'затащив', u'затащили') if is_winner else (u'насосав', u'насосали'), len(our_guys)),
                in_solo=u'... В соляндру' if len(our_guys) == 1 else ''
            )
            tables = []
            for team_id in (0, 1):
                details = [
                    [self.trim(member.nickname, 8), self.trim(member.hero, 8), '/'.join(member.kda), member.nw] for member in match.players[team_id]
                ]
                details.insert(0, ['Player', 'Hero', 'K/D/A', 'Net Worth'])
                table = AsciiTable(details, ('Radiant', 'Dire')[team_id])
                tables.append(table.table)
            # table.inner_heading_row_border = False
            bot.sendMessage(job.context, u'{}\n```\n{}\n```\n{}'.format(summary, '\n'.join(tables), match.get_url()), parse_mode='Markdown')
        logger.info('Poll finished')
