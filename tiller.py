#!/usr/bin/env python
"""Usage:
    tiller.py [options]... plan <resource> [--destroy]
    tiller.py [options]... build <resource>
    tiller.py [options]... show <resource>
    tiller.py [options]... destroy <resource>
    tiller.py [options]... list
    tiller.py [options]... describe <resource>
    tiller.py [options]... stage

Commands:
    plan        Show the plan for the specified resource.
                (add --destroy to see the destroy plan)
    build       Build the specified resource.
    show        Describe the specified resource.
    destroy     Destroy the specified resource.
    list        List valid resources.
    describe    Show a more detailed description of a resource.
    stage       Experimental. Stage the environment for manual TF run.

Options:
    --var=<key=value>  key/value pairs to write to configuration
    -h --help          show this screen and exit
    -E ENV, --env=env  target environment
    -v --verbose       be noisy
    -D --debug         be really noisy
    --force            don't ask, just do - USE AT YOUR OWN RISK!

"""

from docopt import docopt
import logging
import os
import ConfigParser
import textwrap
from abc import ABCMeta, abstractmethod
import json

name = 'tiller'
version = '0.0.1'

class Packer:
    """docstring for Packer"""
    __metaclass__ = ABCMeta
    def __init__(self):
        logging.debug("In Packer metaclass")
        super(Packer, self).__init__()
    
    @abstractmethod
    def build(self):
        pass
        

class Terraform:
    """docstring for Terraform"""
    __metaclass__ = ABCMeta

    def __init__(self):
        logging.debug("In Terraform metaclass")
        super(Terraform, self).__init__()

    @abstractmethod
    def plan(self):
        pass

    @abstractmethod
    def build(self):
        pass

    @abstractmethod
    def show(self):
        pass

    @abstractmethod
    def destroy(self):
        pass
        

class TillerResource(object):
    """A TillerResource describes an object which tiller can build, destroy, or describe"""
    def __init__(self, name, path, *args, **kwargs):
        logging.debug("TillerResource.__init__()")
        logging.debug("{}:{}\n*args: {}\n**kwargs: {}".format(name, path, args, kwargs))
        super(TillerResource, self).__init__()
        self.name = name
        self.path = path
        self.description = kwargs.get('description')
        self.long_description = kwargs.get('long_description')
        self.depends_on = kwargs.get('depends_on')
        if self.depends_on:
            self.depends_on = json.loads(self.depends_on)
        self.required_vars = kwargs.get('required_vars')
        if self.required_vars:
            self.required_vars = json.loads(self.required_vars)
        self.__staged = False


    @classmethod
    def from_config(cls, config_file):
        """Create a TillerResource from a configuration file"""
        configuration = dict()
        config = ConfigParser.RawConfigParser()
        config.read(config_file)
        section = "resource"
        logging.debug("Creating new resource from config file %s" % config_file)

        configuration['path'] = os.path.dirname(config_file)
        logging.debug("Resource path: %s" % configuration['path'])
        try:
            for param in config.options(section):
                try:
                    configuration[param] = config.get(section, param).strip('"').strip("'")
                except ConfigParser.NoOptionError:
                    if param == "name":
                        logging.warn("'name' option not set in %s" % config_file)
                        return None
                    else:
                        configuration[param] = None
                        continue
        except ConfigParser.NoSectionError:
            logging.error("No section '%s' in '%s'" % (section, config_file))
        except:
            raise

        return cls(configuration.pop('name'), 
                   configuration.pop('path'), 
                   **configuration)


    def validate_config(self):
        # TODO: verify path actually exists
        if self.configuration['path'] and self.configuration['name']:
            self.__config_valid = True
        return self.__config_valid

    @abstractmethod
    def stage(self):
        """Stages a resource prior to executing a command.
        Sets environment, parses configuration files, and stops
        just prior to executing requested command"""
        pass


    def __str__(self):
        return "%s: %s" % (self.name, self.path)

    def __bool__(self):
        return self.validate_config()


class TillerTerraformResource(TillerResource, Terraform):
    """docstring for TillerTerraformResource"""
    def __init__(self, name, path, *args, **kwargs):
        logging.debug("Creating TillerTerraformResource")
        super(TillerTerraformResource, self).__init__(name, path, *args, **kwargs)

    def plan(self):
        pass

    def build(self):
        # build command = self.kwargs['build_cmd']
        pass

    def show(self):
        pass

    def destroy(self):
        pass


class TillerPackerResource(TillerResource, Packer):
    """docstring for TillerPackerResource"""
    def __init__(self, name, path, *args, **kwargs):
        logging.debug("Creating TillerPackerResource")
        super(TillerPackerResource, self).__init__(name, path, *args, **kwargs)
        self.name = name
        self.path = path
        self.args = args
        self.kwargs = kwargs

    def build(self):
        pass
        

def compile_resources():
    resources = {}
    # Enter resources subdirectory(-ies) and look for config files
    resources_dirname = "resources"
    config_filename = "config.tiller"
    for root, dirs, files in os.walk(resources_dirname):
        for f in files:
            if f == config_filename:
                logging.debug("creating resource from %s in %s" % (f,root))
                namespace = root.split('/')[1]
                if namespace == 'terraform':
                    r = TillerTerraformResource.from_config(os.path.join(root, f))
                elif namespace == 'packer':
                    r = TillerPackerResource.from_config(os.path.join(root,f))
                else:
                    r = TillerResource.from_config(os.path.join(root, f))
                # Create a new entry in resource{} with the name of the resource as the value
                if r:
                    r.name = '{}/{}'.format(namespace, r.name)
                    resources[r.name] = r

    return resources

def plan(resource, env=None):
    logging.info("planning %s" % resource)


def build(resource, env=None):
    logging.info("building %s" % resource)


def show(resource, env=None):
    logging.info("showing output for %s" % resource)
    pass

def describe(resource, env=None):
    logging.info("describing %s" % resource)
    # TODO: Check if resource exists
    pass

def destroy(resource, env=None, force=False):
    logging.info("destroying", resource, force)


def stage_terraform_run(env=None):
    logging.info("Staging environment for terraform run")


def main(args):
    if args['--debug']:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.ERROR)

    if args['plan']:
        # TODO: Implement 'plan'
        logging.info("Planning.")
    elif args['build']:
        # TODO: Implement 'build'
        logging.info("Building.")
    elif args['show']:
        # TODO: Implement 'show'
        logging.info("Showing.")
    elif args['describe']:
        logging.info("Describing resource")
        r = compile_resources()[args['<resource>']]
        print "Resource: ", r.name
        desc_prefix="Description: "
        description = textwrap.TextWrapper(initial_indent=desc_prefix,
                                           width = 64,
                                           subsequent_indent = ' '*len(desc_prefix),
                                           replace_whitespace = False,
                                           expand_tabs = True)
        print description.fill(r.long_description)

    elif args['destroy']:
        # TODO: Implement 'destroy'
        logging.info("Destroying.")
    elif args['list']:
        logging.info("Listing resources.")
        resources = compile_resources()
        print('The following resources are availble:')
        for r in resources.values():
            if r.depends_on:
                print('\t{:<16}\t{} (Depends on {})'.format(*[r.name, r.description, ', '.join(r.depends_on)]))
            else:
                print('\t{:<16}\t{}'.format(*[r.name, r.description]))


        print('\nFor more information see: ./tiller.py describe <resource>')

    elif args['stage']:
        # TODO: Implement 'stage'
        logging.info("Staging terraform for manual run.")


if __name__ == '__main__':
    args = docopt(__doc__, version='%s v%s' % (name, version))
    if args['--debug']:
        print args
    main(args)
