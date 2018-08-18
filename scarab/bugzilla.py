# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4

import xmlrpc.client

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

    def attachments(self, bug_id):
        args = self.common_args()
        args['ids'] = [bug_id]
        # Do not requets attachment data
        args['exclude_fields'] = ['data']
        result = self.__proxy.Bug.attachments(args)
        return result

    def attachment(self, attachment_id):
        args = self.common_args()
        args['attachment_ids'] = [attachment_id]
        # Do not requets attachment data
        args['exclude_fields'] = ['data']
        result = self.__proxy.Bug.attachments(args)
        return result
