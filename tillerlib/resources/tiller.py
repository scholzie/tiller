import tillerlib.tillerlib as tl
import logging
from abc import abstractmethod
import ConfigParser
import os
import json
import sys


class TillerResource(object):
    """A TillerResource describes an object which tiller can build,
    destroy, or describe"""
    @tl.logged(logging.DEBUG, msg="TillerResource")
    def __init__(self, name, path, *args, **kwargs):
        logging.debug("{}:{}\n*args: {}\n**kwargs: {}".format(name,
                                                              path,
                                                              args,
                                                              kwargs))
        super(TillerResource, self).__init__()
        self.name = name
        self.path = path
        self.namespace = path.split('/')[1]
        self.environment = kwargs.get('environment')
        if self.environment:
            # remove all whitespace
            self.environment = ''.join(self.environment.split())
        self.description = kwargs.get('description')
        self.long_description = kwargs.get('long_description')
        self.depends_on = kwargs.get('depends_on')

        if self.depends_on:
            self.depends_on = json.loads(self.depends_on)
        self.required_vars = kwargs.get('required_vars')
        if self.required_vars:
            # Take the list and make it an empty dictionary:
            self.required_vars = {key: None for key in json.loads(
                self.required_vars)}
            # self.required_vars = json.loads(self.required_vars)

        self._staged = False
        self._config_valid = False

        logging.debug("""
          name = {}
          path = {}
          namespace = {}
          description = {}
          long_description = {}
          depends_on = {}
          required_vars = {}
          """.format(self.name,
                     self.path,
                     self.namespace,
                     self.description,
                     self.long_description,
                     self.depends_on,
                     self.required_vars))

    @tl.logged(logging.DEBUG)
    def required_vars_set(self):
        """
        Return True if all the required variables have a value. Else False.
        """

        all_vars_set = True
        if self.required_vars:
            for k, v in self.required_vars.items():
                if not v:
                    logging.error("Required variable {} is not set".format(k))
                    all_vars_set = False
        return all_vars_set

    @tl.logged(logging.DEBUG)
    def set_vars(self, *args, **kwargs):
        # resolution order (non-resource-dependent):
        # Env vars
        # command line (passed as **kwargs)

        # get --vars passed added to variable dict
        for k, v in kwargs.items():
            self.required_vars[k] = v

        # Env vars:
        for k in self.required_vars.keys():
            logging.debug("Checking for values for {}".format(k))
            if os.environ.get('TILLER_{}'.format(k)):
                self.required_vars[k] = os.environ.get('TILLER_{}'.format(k)).strip('"').strip("'")
                logging.debug("ENV $TILLER_{}: {}".format(k, os.environ.get('TILLER_{}'.format(k)).strip('"').strip("'")))
            if kwargs.get(k):
                self.required_vars[k] = kwargs.get(k).strip('"').strip("'")
                logging.debug("--vars {}: {}".format(k, kwargs.get(k).strip('"').strip("'")))

    @classmethod
    def from_config(cls, config_file):
        """Create a TillerResource from a configuration file"""
        configuration = dict()
        config = ConfigParser.RawConfigParser()
        config.read(config_file)
        section = "resource"
        logging.debug("Creating new resource from config file {}".format(
            config_file))

        configuration['path'] = os.path.dirname(config_file)
        logging.debug("Resource path: %s" % configuration['path'])
        try:
            for param in config.options(section):
                try:
                    configuration[param] = config.get(section, param).strip(
                        "\"").strip("'")
                except ConfigParser.NoOptionError:
                    if param == "name":
                        logging.warn("'name' option not set in {}".format(
                            config_file))
                        return None
                    else:
                        configuration[param] = None
                        continue
        except ConfigParser.NoSectionError:
            logging.error("No section '%s' in '%s'" % (section, config_file))

        return cls(configuration.pop('name'),
                   configuration.pop('path'),
                   **configuration)

    def setEnvironment(self, env):
        # remove whitespace
        self.environment = ''.join(env.split())

    def validate_tiller_config(self):
        if all([os.path.exists(self.path), self.name, self.namespace]):
            self.__config_valid = True
        return self.__config_valid

    @tl.logged(logging.DEBUG)
    def stage(self, *args, **kwargs):
        """Stages a resource prior to executing a command.
        Sets environment, parses configuration files, and stops
        just prior to executing requested command"""
        if not self.required_vars_set():
            raise tl.TillerException("Unable to stage parent. Not all required"
                                     " variables are set.")
        return True

    @abstractmethod
    def validate(self):
        """Validate the Resource"""
        pass

    def __str__(self):
        return '{}/{}'.format(self.namespace, self.name)

    def __bool__(self):
        return self.validate_tiller_config()
