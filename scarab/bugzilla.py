# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4

import xmlrpc.client
from datetime import datetime
from datetime import timezone

class Attachment(object):
    def __init__(self, d):
        self.object_id = int(d['id'])
        self.bug_id = int(d['bug_id'])
        self.file_name = d['file_name']
        self.summary = d['summary']
        self.content_type = d['content_type']
        self.size = int(d['size'])
        time_tuple = d['creation_time'].timetuple()
        # Convert from UTC to local timezone
        dt = datetime(*time_tuple[0:6], tzinfo=timezone.utc).astimezone(tz=None)
        self.creation_time = dt
        time_tuple = d['last_change_time'].timetuple()
        # Convert from UTC to local timezone
        dt = datetime(*time_tuple[0:6], tzinfo=timezone.utc).astimezone(tz=None)
        self.last_change_time = dt
        self.creator = d['creator']
        self.is_obsolete = d['is_obsolete']

    def __repr__(self):
        return ("Attachment(%d, '%s')" % (self.object_id, self.file_name))

class Bugzilla(object):
    __token = None

    def __init__(self, url):
        self.__proxy = xmlrpc.client.ServerProxy(url)

    def set_auth_token(self, token):
        self.__token = token

    def common_args(self):
        return {'Bugzilla_token': self.__token}

    def products(self):
        args = self.common_args()
        result = self.__proxy.Product.get_selectable_products(args)
        return result

    def bug(self, bug_id):
        args = self.common_args()
        args['ids'] = [bug_id]
        result = self.__proxy.Bug.get(args)
        return result

    def attachments(self, bug_id, include_obsolete=False):
        args = self.common_args()
        args['ids'] = [bug_id]
        # Do not requets attachment data
        args['exclude_fields'] = ['data']
        reply = self.__proxy.Bug.attachments(args)
        result = []
        for d in reply['bugs'][str(bug_id)]:
            result.append(Attachment(d))
        if not include_obsolete:
            result = [a for a in result if not a.is_obsolete]
        result.sort(key=lambda a: a.object_id)

        return result

    def attachment(self, attachment_id):
        args = self.common_args()
        args['attachment_ids'] = [attachment_id]
        # Do not requets attachment data
        args['exclude_fields'] = ['data']
        result = self.__proxy.Bug.attachments(args)
        return result
