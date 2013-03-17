#!/usr/bin/env python
from pyramid.response import Response
from pyramid.view import view_config
from pyramid.config import Configurator
from pyramid.httpexceptions import HTTPForbidden
from waitress import serve

class BlogentryViews(object):
    def __init__(self, request):
        self.request = request

    @view_config(route_name='blogentry_show')
    def show(self):
        print self.request.cookies.get('userid')
        return Response('Shown')

    # [1]
    @view_config(route_name='blogentry_delete')
    def delete(self):
        userid = self.request.cookies.get('userid')
        if userid is None:
            raise HTTPForbidden()
        return Response('Deleted')

    # [2]
    @view_config(route_name='login')
    def login(self):
        userid = self.request.params.get('userid')
        headers = [('Set-Cookie',
                    'userid=%s' % str(userid))]
        return Response(
            'Logged in as %s' % userid,
            headers=headers
            )

    # [3]
    @view_config(route_name='logout')
    def logout(self):
        headers = [
            ('Set-Cookie',
             'userid=deleted; Expires=Thu, 01-Jan-1970 00:00:01 GMT')
            ]
        return Response(
            'Logged out',
            headers=headers
            )

# [4]
if __name__ == '__main__':
    config = Configurator()
    config.add_route('blogentry_show', '/blog/{id}')
    config.add_route('blogentry_delete', '/blog/{id}/delete')
    config.add_route('login', '/login')
    config.add_route('logout', '/logout')
    config.scan()
    app = config.make_wsgi_app()
    serve(app)
    
# Basic security; only authenticated users can delete blog entries.  all others
# can view blog entries.
#
# New features:
#
# [4] Wiring up login and logout views into config.
# [2] Login view to service authorization checks.  Just a stub, a real app 
#     would require password checking.
# [3] Logout view to forget login credentials.
# [1] Imperative authorization code to check whether a logged in user can delete
#
# Noteworthy:
#
# - No frameworky bits, it's all your code.
#
# - Imperative code to check whether a logged in user can delete must
#   be repeated everywhere to be useful.
#
# - Married to cookie-based authentication throughout codebase (everywhere:
#   [1], [2], and [3]).  A change to the authentication mechanism implies
#   visiting each place the imperative security checking is done.
#
# - Authentication is "who you are".  Authorization is "what you can do".  In
#   this application, authentication and authorization are intertwined.
#
# - While authorization typically depends on authentication, authentication is
#   almost always logically independent of authorization.  Our application does
#   not take this into consideration, however.  It has no abstractions that
#   would allow them to be changed independently.
#
# - Curiosity: httpexceptions can either be raised or returned.  Typically you
#   raise if you want the work done in the current transaction to be rolled
#   back.  We raise HTTPForbidden above, but return HTTPFound, for this
#   notional reason.

