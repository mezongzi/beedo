# coding=utf-8
from __future__ import absolute_import

from flask import g


def get_response(trigger):
    if trigger['type'] == 'subscribe':
        response = g.files.get('subscribe')
    elif trigger['type'] == 'keywords':
        file_id = g.keys.get(trigger['key'])
        if file_id:
            response = g.files.get(file_id)
        else:
            response = None
    if not response:
        response = g.files.get('default')
    if response.get('status'):
        return response
    else:
        return None


def get_append_resp():
    appends = g.files.get('appends')
    if appends.get('status'):
        return appends
    else:
        return None
