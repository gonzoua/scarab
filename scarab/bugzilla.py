# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4

import xmlrpc.client
from datetime import datetime, timezone


class BugzillaError(Exception):
    def __init__(self, message):
        super().__init__(message)
        self.message = message

def xmlrpc_method(method):
    def wrapper(*args, **kwargs):
        try:
            return method(*args, **kwargs)
        except xmlrpc.client.ProtocolError as e:
            raise BugzillaError('{}: {} {}'.format(e.url, e.errcode, e.errmsg))
        except xmlrpc.client.Fault as e:
            raise BugzillaError('{} ({})'.format(e.faultString, e.faultCode))

    return wrapper

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
        if 'data' in d:
            self.data = d['data'].data
        else:
            self.data = b''

    def __repr__(self):
        return ("Attachment(%d, '%s')" % (self.object_id, self.file_name))

class Bugzilla(object):
    __api_key = None

    def __init__(self, url):
        self.__proxy = xmlrpc.client.ServerProxy(url)

    def set_api_key(self, api_key):
        self.__api_key = api_key

    def common_args(self):
        return {'Bugzilla_api_key': self.__api_key}

    @xmlrpc_method
    def products(self):
        args = self.common_args()
        result = self.__proxy.Product.get_selectable_products(args)
        return result

    @xmlrpc_method
    def bug(self, bug_id):
        args = self.common_args()
        args['ids'] = [bug_id]
        result = self.__proxy.Bug.get(args)
        return result

    @xmlrpc_method
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

    @xmlrpc_method
    def attachment(self, attachment_id, data=False):
        args = self.common_args()
        args['attachment_ids'] = [attachment_id]
        if not data:
            args['exclude_fields'] = ['data']
        reply = self.__proxy.Bug.attachments(args)
        if not str(attachment_id) in reply['attachments']:
            return None
        return Attachment(reply['attachments'][str(attachment_id)])

    @xmlrpc_method
    def add_attachment(self, bug_id, file_name, data, summary=None, comment=None, content_type='application/octect-stream'):
        args = self.common_args()
        args['ids'] = [bug_id]
        args['file_name'] = file_name
        args['data'] = data
        args['summary'] = summary if summary is not None else file_name
        args['content_type'] = content_type
        if comment is not None:
            args['comment'] = comment
        reply = self.__proxy.Bug.add_attachment(args)
        ids = reply.get('ids', [])
        if len(ids) > 0:
            return ids[0]
        return None
