#!/usr/bin/env python
#
# Copyright 2015 Flavio Garcia
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
#
# vim: set expandtab tabstop=4 shiftwidth=4 softtabstop=4:

import firenado.conf
from firenado.core.management import ManagementTask
from firenado.util import file as _file
from firenado.util.argparse_util import FirenadoArgumentError

import os
import sys
from tornado import template

class ValidateAppCommandsTask(ManagementTask):
    """Validate application related commands
    """
    def run(self, namespace):
        print "buuu"
        if namespace.app_command == 'start':
            task = StartAppTask(namespace)

    def add_arguments(self, parser):
        parser.add_argument(
            'app_command', type=str,
            choices=['start'], help="The ")

class ValidateProjectCommandsTask(ManagementTask):
    """Validate project related commands
    """
    def run(self, namespace):
        if namespace.project_command == 'init':
            task = CreateProjectTask(namespace)
            task.add_arguments(self.parser)
            try:
                self.parser.parse_args()
            except FirenadoArgumentError as exception:
                print exception.message

    def add_arguments(self, parser):
        self.parser = parser
        parser.add_argument(
            'project_command', type=str,
            choices=['init'], help="The project module")

    def get_error_message(self, parser, exception):
        help_header_message = ""#get_command_header(parser, true)
        loader = template.Loader(os.path.join(
            firenado.conf.ROOT, 'core', 'management', 'templates', 'project'))
        help_message = loader.load("init_command_help.txt").generate()
        return help_message


class CreateProjectTask(ManagementTask):
    """
    Creates a new project from scratch
    """
    def run(self, namespace):
        from tornado import template
        print namespace
        if len(sys.argv) > 2:
            module = namespace.module
            component = module.replace('.', ' ').title().replace(' ', '')
            project_name = module.replace('.', '_').lower()
            project_directory = _file.create_module(module, os.getcwd())
            #TODO: Check if project exists
            #TODO: If doesn't exists create project
            #TODO: If exists throw an error
            loader = template.Loader(os.path.join(
                firenado.conf.ROOT, 'core', 'management', 'templates', 'init'))
            project_init_content = loader.load("__init__.py.txt").generate(
                project_name=project_name, module=module, component=component)
            # Generating application firenado component and handlers
            _file.write(os.path.join(project_directory, '__init__.py'),
                        project_init_content)
            handlers_file_name = os.path.join(project_directory, 'handlers.py')
            _file.touch(handlers_file_name)
            project_handlers_content = loader.load("handlers.py.txt").generate(
                handlers=['Index'])
            _file.write(handlers_file_name, project_handlers_content)
            # Generating configuration
            project_conf_directory = os.path.join(project_directory, 'conf')
            os.mkdir(project_conf_directory)
            project_conf_file = os.path.join(project_conf_directory,
                                             'firenado.yaml')
            _file.touch(project_conf_file)
            project_init_content = loader.load("firenado.yaml.txt").generate(
                app_name=project_name, module=module, component=component)
            _file.write(project_conf_file, project_init_content)
        else:
            #TODO: This thing has to go. The parameter validation should be
            #TODO: executed by the argument parser.
            loader = template.Loader(os.path.join(
                firenado.conf.ROOT, 'core', 'management', 'templates', 'help'))
            help_message = loader.load("init_command_help.txt").generate()

    def add_arguments(self, parser):
        """
        Add module argument to the command parser.

        :param parser: The current parser validating the command holding this
        task.
        """
        parser.add_argument('module', help="The project module")

    def get_error_message(self, parser, exception):
        return exception.message
        


class StartAppTask(ManagementTask):
    """ Task that starts an Firenado Tornado Application based 
    on the it's project configuration
    """
    def run(self, namespace):
        import tornado.ioloop
        import tornado.httpserver
        # TODO: Resolve module if doesnt exists
        if firenado.conf.app['python_path']:
            sys.path.append(firenado.conf.app['python_path'])
        http_server = tornado.httpserver.HTTPServer(
            firenado.core.TornadoApplication())
        http_server.listen(firenado.conf.app['port'])
        tornado.ioloop.IOLoop.instance().start()
