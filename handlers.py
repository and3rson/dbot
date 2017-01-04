# -*- coding: utf-8 -*-
from telegram import ChatAction
import settings
from terminaltables import AsciiTable
from log import logger
from api import DotaBuffAPI
import strings
from random import choice
# from redis import Redis


class DotaBuffPollJob(object):
    def __init__(self):
        self.__name__ = 'DotaBuffPollJob'

        self.guys = {
            48355300: ('@irember', 'm'),
            90366968: ('@barbieavi', 'f'),
            104978674: ('@leslviv', 'm'),
            31563138: ('@andunai', 'm'),
            87255844: ('@slickwood', 'm'),
            110284210: ('@megaspro', 'm')
        }

        self.api = DotaBuffAPI(debug=getattr(settings, 'DEBUG', False))
        # api.get_matches(48355300)
        for user_id in self.guys.keys():
            self.api.track(settings.CHAT_ID, user_id)
        self.api.init()

    def pluralize(self, forms, count):
        return forms[1 if count > 1 else 0]

    def trim(self, s, maxlen, ellipsis='..'):
        return s[:maxlen] + (s[maxlen:] and ellipsis)

    def get_guy_info_from_po(self, po):
        if po.profile_id in self.guys:
            info = self.guys[po.profile_id]
        else:
            info = (po.nickname, 'm')

        return info

#        return (u'{} ({})'.format(info[0], po.hero), info[1])

    def __call__(self, bot, job):
        # logger.info('call: %s %s', bot, job)
        logger.info('Polling...')
        for match in self.api.poll(settings.CHAT_ID):
            logger.info('Found new match: %s', match)
            match = self.api.get_match(match.id)
            team, is_winner = self.api.find_our_guys(settings.CHAT_ID, match)
            all_members = match.players[0] + match.players[1]

            our_guys_po_list = filter(lambda po: po.profile_id in self.api.tracks[settings.CHAT_ID], all_members)
            our_guys_infos = [self.guys[po.profile_id] for po in our_guys_po_list]

            our_guys_team_po_list = match.players[0 if team == 'radiant' else 1]

            our_guys_team_po_list_sorted = list(sorted(our_guys_team_po_list, key=lambda po: -po.get_kda_ratio()))

            top_po, bottom_po = our_guys_team_po_list_sorted[0], our_guys_team_po_list_sorted[-1]

            s = choice(strings.STRINGS['won' if is_winner else 'lost'])

            # print our_guys_infos, strings.unite(our_guys_infos)

            message = strings.make_message(s, who=strings.unite(our_guys_infos))

            bot.sendMessage(job.context, u'{}!\n\n - MVP - {}! Катнув на {}, як Ісусик! (KDA: {} = {}).\n - Дно матчу - {}. Ніколи більше не пікай {}! (KDA: {} = {}).\n\n{}'.format(
                message,
                self.get_guy_info_from_po(top_po)[0], top_po.hero,'/'.join(top_po.kda), top_po.get_kda_ratio(),
                self.get_guy_info_from_po(bottom_po)[0], bottom_po.hero, '/'.join(bottom_po.kda), bottom_po.get_kda_ratio(),
                match.get_url()
            ), parse_mode='Markdown')

            # our_guys_names = [u'{} ({})'.format(po.nickname, po.hero) for po in our_guys]

            # summary = u'{members} щойно *{what}*{in_solo}.'.format(
            #     members=self.unite(our_guys_names),
            #     what=self.pluralize((u'затащив', u'затащили') if is_winner else (u'насосав', u'насосали'), len(our_guys)),
            #     in_solo=u'... В соляндру' if len(our_guys) == 1 else ''
            # )
            # tables = []
            # for team_id in (0, 1):
            #     details = [
            #         [self.trim(member.nickname, 8), self.trim(member.hero, 8), '/'.join(member.kda), member.nw] for member in match.players[team_id]
            #     ]
            #     details.insert(0, ['Player', 'Hero', 'K/D/A', 'Net Worth'])
            #     table = AsciiTable(details, ('Radiant', 'Dire')[team_id])
            #     tables.append(table.table)
            # # table.inner_heading_row_border = False
            # bot.sendMessage(job.context, u'{}\n```\n{}\n```\n{}'.format(summary, '\n'.join(tables), match.get_url()), parse_mode='Markdown')
        logger.info('Poll finished')
