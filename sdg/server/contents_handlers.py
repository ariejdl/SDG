
from notebook.base.handlers import path_regex
from notebook.services.contents.handlers import ContentsHandler

from .handler_utils import BaseHandler

class AuthContentsHandler(BaseHandler, ContentsHandler):

    pass


handlers = [
    (r"/api/contents%s" % path_regex, AuthContentsHandler),
]
