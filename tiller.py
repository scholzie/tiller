#!/usr/bin/env python
"""Usage:
    tiller.py [options] plan <resource> [--destroy]
    tiller.py [options] build <resource>
    tiller.py [options] show <resource>
    tiller.py [options] destroy <resource>
    tiller.py [options] list
    tiller.py [options] describe <resource>
    tiller.py [options] stage

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

name = 'tiller'
version = '0.0.1'

class TillerResource(object):
    """A TillerResource describes an object which tiller can build, destroy, or describe"""
    def __init__(self, name, path, description=None, long_description=None):
        super(TillerResource, self).__init__()
        self.name = name
        self.path = path
        self.description = description
        self.long_description = long_description
        self.__staged = False


    @classmethod
    def from_config(cls, config_file):
        """Create a TillerResource from a configuration file"""
        configuration = {}
        config = ConfigParser.RawConfigParser()
        config.read(config_file)
        section = "resource"
        logging.debug("Creating new resource from config file %s" % config_file)

        configuration['path'] = os.path.dirname(config_file)
        logging.debug("Resource path: %s" % configuration['path'])
        try:
            for param in ['name', 'description', 'long_description']:
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

        logging.debug("TillerResource created: %r", configuration)

        return cls(configuration['name'],
                   configuration['path'],
                   configuration['description'],
                   configuration['long_description'])

    def validate_config(self):
        # TODO: verify path actually exists
        if self.configuration['path'] and self.configuration['name']:
            self.__config_valid = True
        return self.__config_valid

    def stage(self):
        """Stages a resource prior to executing a command. 
        Sets environment, parses configuration files, and stops 
        just prior to executing requested command"""
        # TODO: Implement TerraformResource.stage()
        pass

    def __str__(self):
        return "%s: %s" % (self.name, self.path)


    def __bool__(self):
        return self.validate_config()

def compile_resources():
    resources = {}
    # Enter resources subdirectory(-ies) and look for config files
    resources_dirname = "resources"
    config_filename = "config.tiller"
    for root, dirs, files in os.walk(resources_dirname):
        for f in files:
            if f == config_filename:
                logging.debug("creating resource from %s" % f)
                r = TillerResource.from_config(os.path.join(root, f))
                # Create a new entry in resource{} with the name of the resource as the value
                if r:
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
        output_lines = []
        for r in resources.values():
            print('\t{:<16}  {}'.format(*[r.name, r.description]))

    elif args['stage']:
        # TODO: Implement 'stage'
        logging.info("Staging terraform for manual run.")


if __name__ == '__main__':
    args = docopt(__doc__, version='%s v%s' % (name, version))
    main(args)
