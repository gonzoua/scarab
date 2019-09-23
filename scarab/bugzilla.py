# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4
"""
Wrapper class for Bugzilla's XML-RPC API
"""

import xmlrpc.client
from datetime import datetime, timezone
import urllib

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
        self.flags = []
        for df in d['flags']:
            self.flags.append(Flag(df))

    def __repr__(self):
        return "Attachment(%d, '%s')" % (self.object_id, self.file_name)

class Flag(object):
    """Bugzilla flag representation"""
    def __init__(self, d):
        self.object_id = int(d['id'])
        self.name = d['name']
        self.requestee = d.get('requestee', '')
        self.status = d['status']

    def __repr__(self):
        return "Flag(%d, '%s')" % (self.object_id, self.name)

class Bug(object):
    """Bugzilla bug representation"""
    def __init__(self, d):
        self.object_id = int(d['id'])
        self.summary = d['summary']
        self.product = d['product']
        self.version = d['version']
        self.os = d['op_sys']
        self.status = d['status']
        self.resolution = d['resolution']
        self.severity = d['severity']
        self.priority = d['priority']
        self.component = d['component']
        self.assigned_to = User(d['assigned_to_detail'])
        self.creator = User(d['creator_detail'])
        time_tuple = d['creation_time'].timetuple()
        # Convert from UTC to local timezone
        self.creation_time = datetime(*time_tuple[0:6], tzinfo=timezone.utc).astimezone(tz=None)
        time_tuple = d['last_change_time'].timetuple()
        # Convert from UTC to local timezone
        self.last_change_time = datetime(*time_tuple[0:6], tzinfo=timezone.utc).astimezone(tz=None)
        self.flags = []
        for df in d['flags']:
            self.flags.append(Flag(df))

    def __repr__(self):
        return "Bug(%d, '%s')" % (self.object_id, self.summary)

class User(object):
    """Bugzilla user representation"""
    def __init__(self, d):
        self.object_id = int(d['id'])
        self.name = d['name']
        self.real_name = d['real_name']
        self.email = d['email']

    def __str__(self):
        if self.real_name:
            return '{} <{}>'.format(self.real_name, self.email)
        else:
            return self.email

    def __repr__(self):
        return "User(%d, '%s')" % (self.object_id, self.name)

class Product(object):
    """Bugzilla product representation"""

    class Component(object):
        """Bugzilla product's component representation"""
        def __init__(self, d):
            self.object_id = int(d['id'])
            self.name = d['name']

        def __repr__(self):
            return "Component(%d, '%s')" % (self.object_id, self.name)

    class Version(object):
        """Bugzilla product's version representation"""
        def __init__(self, d):
            self.object_id = int(d['id'])
            self.name = d['name']

        def __repr__(self):
            return "Component(%d, '%s')" % (self.object_id, self.name)

    def __init__(self, d):
        self.object_id = int(d['id'])
        self.name = d['name']
        self.description = d['description']
        self.components = []
        self.versions = []
        for component_d in d['components']:
            self.components.append(self.Component(component_d))
        for version_d in d['versions']:
            self.versions.append(self.Version(version_d))

    def __repr__(self):
        return "Product(%d, '%s')" % (self.object_id, self.name)

class Bugzilla(object):
    """Wrapper for Bugzilla's XML-RPC API"""
    __api_key = None

    def __init__(self, url):
        self.__base_url = url
        if not self.__base_url.endswith('/'):
            self.__base_url += '/'
        xmlrpc_url = self.__url('xmlrpc.cgi')
        self.__proxy = xmlrpc.client.ServerProxy(xmlrpc_url)

    def set_api_key(self, api_key):
        """Set API key for current session"""
        self.__api_key = api_key

    def bug_url(self, bug):
        url = 'show_bug.cgi?id={}'.format(bug)
        return self.__url(url)

    def attachment_url(self, attachment):
        url = 'attachment.cgi?id={}&action=edit'.format(attachment)
        return self.__url(url)

    def __url(self, relative_url):
        """Returns absolute URL for relative_url using bugzilla URL as a base"""
        return urllib.parse.urljoin(self.__base_url, relative_url)

    def __common_args(self):
        """Initialize part of parameters common for all XML-RPC methods"""
        if self.__api_key is None:
            return {}

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

    @xmlrpc_method
    def update(self, bug_id, status=None, \
        resolution=None, assigned_to=None,
        add_cc=None, remove_cc=None, comment=None):
        """
        Modify existing PR
        Args:
            bug_id (int): bug ID
            status (str, optional): new status value
            resolution (str, optional): new resolution value
            assigned_to (str, optional): user to assign PR to
            add_cc (list, optional): list of email to be added to Cc
            remove_cc (list, optional): list of email to be removed from Cc
            comment (str, optional): comment to be associated with the change
        """
        args = self.__common_args()
        args['ids'] = [bug_id]
        if status is not None:
            args['status'] = status
        if resolution is not None:
            args['resolution'] = resolution
        if assigned_to is not None:
            args['assigned_to'] = assigned_to
        cc = {}
        if add_cc:
            cc['add'] = add_cc
        if remove_cc:
            cc['remove'] = remove_cc
        if len(cc) > 0:
            args['cc'] = cc
        if comment is not None:
            args['comment'] = { 'body': comment }
        reply = self.__proxy.Bug.update(args)
        return None

    @xmlrpc_method
    def products(self):
        """
        Returns list of Product objects representing
        products to which user can submit bugs
        """
        args = self.__common_args()
        ids = self.__proxy.Product.get_accessible_products(args)
        reply = self.__proxy.Product.get(ids)
        result = []
        for obj in reply['products']:
            product = Product(obj)
            result.append(product)
        return result

    @xmlrpc_method
    def submit(self, product, component, version, summary, \
            description=None, cc_list=None, platform=None,
            severity=None):
        """
        Submit new bug
        Args:
            product (string): product name
            component (string): component name
            version (string): version value
            summary (string): one-line summary of the bug
            description (string, optional): description of the bug
            cc_list (list, optional): list of users' emails to add to Cc list of the bug
            severity (string, optional): bug severity
            platform (string, optional): platform where bug was found
        """
        args = self.__common_args()
        args['product'] = product
        args['component'] = component
        args['summary'] = summary
        args['version'] = version
        if description:
            args['description'] = description
        if cc_list:
            args['cc'] = cc_list
        if platform:
            args['platform'] = platform
        if severity:
            args['severity'] = severity
        reply = self.__proxy.Bug.create(args)
        return reply['id']

    @xmlrpc_method
    def bug(self, bug_id):
        """
        Get information for bug wiht id bug_id
        Args:
            bug_id (int): bug ID
        Returns:
            Bugzilla::Bug object
        """
        args = self.__common_args()
        args['ids'] = [bug_id]
        reply = self.__proxy.Bug.get(args)
        bug = Bug(reply['bugs'][0])

        return bug

    @xmlrpc_method
    def bug_description(self, bug_id):
        """
        Get comment #0 (description) for bug wiht id bug_id
        Args:
            bug_id (int): bug ID
        Returns:
            str with the text of bug description
        """
        args = self.__common_args()
        args['ids'] = [bug_id]
        reply = self.__proxy.Bug.comments(args)
        description = reply['bugs'][str(bug_id)]['comments'][0]['text']

        return description

    @xmlrpc_method
    def add_flag(self, bug_id, name, requestee):
        """
        Add new flag to bug bug_id with value ?
        Args:
            bug_id (int): bug ID
            name (str): flag name or numberic id of flag instance
            requestee (str): requestee for flag or None
        Returns:
            None
        """
        args = self.__common_args()
        d = {'name': name, 'status': '?', 'new': True}
        if requestee:
            d['requestee'] = requestee
        args['ids'] = [bug_id]
        args['flags'] = [d]
        reply = self.__proxy.Bug.update(args)
        return None

    @xmlrpc_method
    def rm_flags(self, bug_id, names):
        """
        Delete flags from specified bugs
        Args:
            bug_id (int): bug ID
            names (list of str): list of flag names or numberic ids of flag instance
        Returns:
            None
        """
        args = self.__common_args()
        flags = []
        for name in names:
            d = {'status': 'X'}

            if name.isdigit():
                d['id'] = int(name)
            else:
                d['name'] = name
            flags.append(d)
        args['ids'] = [bug_id]
        args['flags'] = flags
        reply = self.__proxy.Bug.update(args)
        return None

    @xmlrpc_method
    def update_flag(self, bug_id, name, status):
        """
        Change flag status
        Args:
            bug_id (int): bug ID
            name (str): flag name or numberic id of flag instance
            statsus: new status, either - or +
        Returns:
            None
        """
        args = self.__common_args()
        d = {'status': status}
        if name.isdigit():
            d['id'] = int(name)
        else:
            d['name'] = name
        args['ids'] = [bug_id]
        args['flags'] = [d]
        reply = self.__proxy.Bug.update(args)
        return None

    @xmlrpc_method
    def add_aflag(self, attachment_id, name, requestee):
        """
        Add new flag to attachment attachment_id with value ?
        Args:
            attachment_id (int): attachment ID
            name (str): flag name or numberic id of flag instance
            requestee (str): requestee for flag or None
        Returns:
            None
        """
        args = self.__common_args()
        d = {'name': name, 'status': '?', 'new': True}
        if requestee:
            d['requestee'] = requestee
        args['ids'] = [attachment_id]
        args['flags'] = [d]
        reply = self.__proxy.Bug.update_attachment(args)
        return None

    @xmlrpc_method
    def rm_aflags(self, attachment_id, names):
        """
        Delete flags from specified attachments
        Args:
            attachment_id (int): attachment ID
            names (list of str): list of flag names or numberic ids of flag instance
        Returns:
            None
        """
        args = self.__common_args()
        flags = []
        for name in names:
            d = {'status': 'X'}

            if name.isdigit():
                d['id'] = int(name)
            else:
                d['name'] = name
            flags.append(d)
        args['ids'] = [attachment_id]
        args['flags'] = flags
        reply = self.__proxy.Bug.update_attachment(args)
        return None

    @xmlrpc_method
    def update_aflag(self, attachment_id, name, status):
        """
        Change attachment flug status
        Args:
            attachment_id (int): attachment ID
            name (str): flag name or numberic id of flag instance
            statsus: new status, either - or +
        Returns:
            None
        """
        args = self.__common_args()
        d = {'status': status}
        if name.isdigit():
            d['id'] = int(name)
        else:
            d['name'] = name
        args['ids'] = [attachment_id]
        args['flags'] = [d]
        reply = self.__proxy.Bug.update_attachment(args)
        return None
