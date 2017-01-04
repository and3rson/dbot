# -*- coding: utf-8 -*-
import re


def replace(match, context):
    fn, var, args = match.groups()
    args = args.split(',')
    input = context[var]
    # print fn, var, ', '.join(args)
    if fn == 'gender':
        if input[1] == 'm':
            return args[0].format(v=input[0])
        if input[1] == 'f':
            return args[1].format(v=input[0])
        return args[2].format(v=input[0])
    elif fn == 'count':
        if input[0] % 10 == 1 and input[0] % 100 != 11:
            return args[0].format(v=input[0])
        elif input[0] % 10 in (2, 3, 4) and input[0] % 100 not in (12, 13, 14):
            return args[1].format(v=input[0])
        return args[2].format(v=input[0])
    elif fn == 'value':
        return args[0].format(v=input[0])


def make_message(template, **kwargs):
    return re.sub(r'\[(?P<fn>[\w]+)\((?P<var>[\w\d_]+)\)\:(?P<args>[^\]]+)\]', lambda match: replace(match, kwargs), template)


def unite(parts):
    names, genders = zip(*parts)
    if len(parts) == 1:
        return parts[0]
    elif len(parts) == 2:
        return (u' і '.join(names), 'p')
    else:
        return (u' і '.join((
            u', '.join(names[:-1]),
            names[-1]
        )), 'p')


STRINGS = {
    'won': [
        u'[gender(who):{v} залив соляри,{v} залила соляри,{v} залили соляри]',
        u'[gender(who):{v} задомінував,{v} задомінувала,{v} задомінували]',
        u'[gender(who):{v} забамбурив,{v} забамбурила,{v} забамбурили]',
        u'[gender(who):{v} засадив,{v} засадила,{v} засадили] ворогам по самі ґоґошари',
        u'[value(who):{v} +25]',
    ],
    'lost': [
        u'[gender(who):{v} насосав,{v} насосала,{v} насосали]',
        u'[gender(who):{v} взяв,{v} взяла,{v} взяли] за щоку',
        u'[value(who):{v} -25]',
        u'[gender(who):{v} віддався,{v} віддалась,{v} віддались] банді чорних пантер',
        u'[gender(who):{v} тактично нафідив,{v} тактично нафідила,{v} тактично нафідили]',
        u'[gender(who):{v} лососнув,{v} лососнула,{v} лососнули]',

        u'[gender(who):{v} взяв,{v} взяла,{v} взяли] за щоку цілих п`ять пісюнів.',
        u'[gender(who):{v} віддався,{v} віддалась,{v} віддались] банді чорних друзів',
        u'[gender(who):{v} лососнув,{v} лососнула,{v} лососнули]',
        u'[gender(who):{v} продав,{v} продала,{v} продали] свою цноту',
        u'[gender(who):{v} згарцював,{v} згарцювала,{v} згарцювали] качучу на твердих чорних членах',
        u'Хтось щойно повертів [gender(who):{v},{v},{v}] на хуї',
        u'Банда ворогів щойно виїбала [gender(who):{v},{v},{v}] і не заплатила',
    ]
}
