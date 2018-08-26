# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4
"""
Wrapper class for Bugzilla's XML-RPC API
"""

import xmlrpc.client
from datetime import datetime, timezone

class BugzillaError(Exception):
    """
    Bugzilla errors like XML-RPC transport failures or method failures.
    """
    def __init__(self, message):
        super().__init__(message)
        self.message = message

def xmlrpc_method(method):
    """
    Catch-all wrapper for XML-RPC errors, should be applied
    to methods that use XML-RPC calls.
    """
    def wrapper(*args, **kwargs):
        """decorator's wrapper"""
        try:
            return method(*args, **kwargs)
        except xmlrpc.client.ProtocolError as ex:
            raise BugzillaError('{}: {} {}'.format(ex.url, \
                ex.errcode, ex.errmsg))
        except xmlrpc.client.Fault as ex:
            raise BugzillaError('{} ({})'.format(ex.faultString, ex.faultCode))

    return wrapper

class Attachment(object):
    """Bugzilla attachment representation"""
    def __init__(self, d):
        self.object_id = int(d['id'])
        self.bug_id = int(d['bug_id'])
        self.file_name = d['file_name']
        self.summary = d['summary']
        self.content_type = d['content_type']
        self.size = int(d['size'])
        time_tuple = d['creation_time'].timetuple()
        # Convert from UTC to local timezone
        self.creation_time = datetime(*time_tuple[0:6], tzinfo=timezone.utc).astimezone(tz=None)
        time_tuple = d['last_change_time'].timetuple()
        # Convert from UTC to local timezone
        self.last_change_time = datetime(*time_tuple[0:6], tzinfo=timezone.utc).astimezone(tz=None)
        self.creator = d['creator']
        self.is_obsolete = d['is_obsolete']
        if 'data' in d:
            self.data = d['data'].data
        else:
            self.data = b''

    def __repr__(self):
        return "Attachment(%d, '%s')" % (self.object_id, self.file_name)

class Bugzilla(object):
    """Wrapper for Bugzilla's XML-RPC API"""
    __api_key = None

    def __init__(self, url):
        self.__proxy = xmlrpc.client.ServerProxy(url)

    def set_api_key(self, api_key):
        """Set API key for current session"""
        self.__api_key = api_key

    def __common_args(self):
        """Initialize part of parameters common for all XML-RPC methods"""
        return {'Bugzilla_api_key': self.__api_key}

    @xmlrpc_method
    def attachments(self, bug_id, include_obsolete=False):
        """
        Get list of attachment for specified bug_id
        Args:
            bug_id (int): bug ID
            include_obsolete (boolean, optional):
                if provided and set to True, include attachments
                marked as obsolete into result
        Returns:
            list of Attachment objects representing files attached
            to the specified bug. Returns empty list of there are none.
        """
        args = self.__common_args()
        args['ids'] = [bug_id]
        # Do not requets attachment data
        args['exclude_fields'] = ['data']
        reply = self.__proxy.Bug.attachments(args)
        result = []
        for attachment in reply['bugs'][str(bug_id)]:
            result.append(Attachment(attachment))
        if not include_obsolete:
            result = [a for a in result if not a.is_obsolete]
        result.sort(key=lambda a: a.object_id)

        return result

    @xmlrpc_method
    def attachment(self, attachment_id, data=False):
        """
        Get Attachment object for specified attachment_id. Returns
        None if attachment_id does not exist
        """
        args = self.__common_args()
        args['attachment_ids'] = [attachment_id]
        if not data:
            args['exclude_fields'] = ['data']
        reply = self.__proxy.Bug.attachments(args)
        if not str(attachment_id) in reply['attachments']:
            return None
        return Attachment(reply['attachments'][str(attachment_id)])

    @xmlrpc_method
    def add_attachment(self, bug_id, file_name, data, \
      summary=None, comment=None, content_type='application/octect-stream'):
        """
        Add attachment to specified bug.
        Args:
            bug_id (int): bug ID
            file_name (str): Remote filename (not a local path to the file).
                To be stored as a part of attachment metadata. Should not
                contain path elements.
            data (str): base64-encoded content of the file
            summary (str, optional): one-line description of the attachment
            comment (str, optional): comment to be posted along with the attachment
            content_type (str, optional): content-type of the attachment.
                If not provided application/octet-stream is assumed
        """
        args = self.__common_args()
        args['ids'] = [bug_id]
        args['file_name'] = file_name
        args['data'] = data
        args['summary'] = summary if summary is not None else file_name
        args['content_type'] = content_type
        if comment is not None:
            args['comment'] = comment
        reply = self.__proxy.Bug.add_attachment(args)
        ids = reply.get('ids', [])
        if ids:
            return ids[0]
        return None
