import tillerlib.tillerlib as tl
import logging
from abc import abstractmethod
import ConfigParser
import os
import json

class TillerResource(object):
    """A TillerResource describes an object which tiller can build, destroy, or describe"""
    @tl.logged(logging.DEBUG, msg="TillerResource")
    def __init__(self, name, path, *args, **kwargs):
        logging.debug("{}:{}\n*args: {}\n**kwargs: {}".format(name, path, args, kwargs))
        super(TillerResource, self).__init__()
        self.name = name
        self.path = path
        self.namespace = path.split('/')[1]
        self.description = kwargs.get('description')
        self.long_description = kwargs.get('long_description')
        self.depends_on = kwargs.get('depends_on')

        if self.depends_on:
            self.depends_on = json.loads(self.depends_on)
        self.required_vars = kwargs.get('required_vars')
        if self.required_vars:
            self.required_vars = json.loads(self.required_vars)
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
                    configuration[param] = config.get(section, param).strip("\"").strip("'")
                except ConfigParser.NoOptionError:
                    if param == "name":
                        logging.warn("'name' option not set in %s" % config_file)
                        return None
                    else:
                        configuration[param] = None
                        continue
        except ConfigParser.NoSectionError:
            logging.error("No section '%s' in '%s'" % (section, config_file))


        return cls(configuration.pop('name'),
                   configuration.pop('path'),
                   **configuration)


    def validate_tiller_config(self):
        if all([os.path.exists(self.path), self.name, self.namespace]):
            self.__config_valid = True
        return self.__config_valid

    @abstractmethod
    def stage(self):
        """Stages a resource prior to executing a command.
        Sets environment, parses configuration files, and stops
        just prior to executing requested command"""
        pass

    @abstractmethod
    def validate(self):
        """Validate the Resource"""
        pass

    def __str__(self):
        return '{}/{}: {}'.format(self.namespace, self.name, self.path)

    def __bool__(self):
        return self.validate_tiller_config()
