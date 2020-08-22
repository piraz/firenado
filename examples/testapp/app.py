#!/usr/bin/env python
#
# Copyright 2015-2018 Flavio Garcia
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from . import handlers, services, uimodules
import firenado.tornadoweb
from firenado import service
import logging

logger = logging.getLogger(__name__)


class TestappComponent(firenado.tornadoweb.TornadoComponent):

    user_service: services.LoginService

    def __init__(self, name, application):
        super(TestappComponent, self).__init__(name, application)
        self.user_service = None

    def get_handlers(self):
        import firenado.conf
        default_login = firenado.conf.app['login']['urls']['default']
        return [
            (r"/", handlers.IndexHandler),
            (r"/async/timeout", handlers.AsyncTimeoutHandler),
            (r"/session/counter", handlers.SessionCounterHandler),
            (r"/session/config", handlers.SessionConfigHandler),
            (r"/pagination", handlers.PaginationHandler),
            (r"/%s" % default_login, handlers.LoginHandler),
            (r"/%s" % default_login, handlers.LoginHandler),
            (r"/logout", handlers.LogoutHandler),
            (r"/private", handlers.PrivateHandler),
        ]

    def get_ui_modules(self):
        return uimodules

    def initialize(self):
        import firenado.conf
        firenado.conf.app['login']['urls']['buga'] = 'buga'

    @service.served_by(services.UserService)
    def install(self):
        """  Installing test database
        """
        from firenado.util.sqlalchemy_util import Base
        print('Installing Diasporapy Pod...')
        print('Creating Pod ...')
        engine = self.application.get_data_source(
            'test').engine
        engine.echo = True
        # Dropping all
        # TODO Not to drop all if something is installed right?
        Base.metadata.drop_all(engine)
        # Creating database
        Base.metadata.create_all(engine)
        self.user_service.create({
            'username': "Test",
            'first_name': "Test",
            'last_name': "User",
            'password': "testpass",
            'email': "test@test.ts"
        })

    def get_data_sources(self):
        return self.application.data_sources

    def after_request(self, handler):
        logging.info("Doing something after handler's request: %s" % handler)

    def before_request(self, handler):
        logging.info("Doing something before handler's request: %s" % handler)
