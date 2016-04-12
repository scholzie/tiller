#!/usr/bin/env python
"""Usage:
    tiller.py [options] plan <resource> [--destroy] [--var=<key=val>]...
    tiller.py [options] build <resource> [--var=<key=val>]...
    tiller.py [options] show <resource>
    tiller.py [options] destroy <resource>
    tiller.py [options] list
    tiller.py [options] describe <resource>
    tiller.py [options] stage <resource> [--var=<key=val>]...

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

import tillerlib.tillerlib as tl
from tillerlib.resources.tiller import TillerResource
from tillerlib.resources.terraform import TerraformResource
from tillerlib.resources.packer import PackerResource

from docopt import docopt
import logging
import os
# import ConfigParser
import textwrap
# from abc import ABCMeta, abstractmethod
# import json
# from functools import wraps
# import subprocess

name = 'tiller'
version = '0.0.1'


# class TillerException(Exception):
#     """Wrapper for Tiller Exceptions"""
#     def __init__(self, *args, **kwargs):
#         super(TillerException, self).__init__(self, *args, **kwargs)


# def logged(level, name=None, msg=None):
#     '''
#     Add logging to a function. level is logging.LEVEL,
#     name is the logger name, and msg is the log message.
#     If name and msg are not defined, they default to the
#     function's module and name
#     '''
#     def decorate(func):
#         logname = name if name else func.__module__
#         log = logging.getLogger(logname)
#         if msg:
#             logmsg = '{}(): {}'.format(func.__name__, msg)
#         else:
#             logmsg = func.__name__ + "()"

#         @wraps(func)
#         def wrapper(*args, **kwargs):
#             log.log(level, logmsg)
#             return func(*args, **kwargs)
#         return wrapper
#     return decorate


# class Packer:
#     """Defines an abstract interface for Packer"""
#     __metaclass__ = ABCMeta
#     def __init__(self):
#         logging.debug("[Tiller:Packer:__init__]")
#         super(Packer, self).__init__()
    
#     @abstractmethod
#     def build(self):
#         logging.debug("[Tiller:Packer:build]")
#         pass


# class Terraform:
#     """Defines an abstract interface for Terraform"""
#     __metaclass__ = ABCMeta

#     def __init__(self):
#         logging.debug("[Tiller:Terraform:__init__]")
#         super(Terraform, self).__init__()

#     @abstractmethod
#     def plan(self):
#         logging.debug("[Tiller:Terraform:plan]")
#         pass

#     @abstractmethod
#     def build(self):
#         logging.debug("[Tiller:Terraform:build]")
#         pass

#     @abstractmethod
#     def show(self):
#         logging.debug("[Tiller:Terraform:show]")
#         pass

#     @abstractmethod
#     def destroy(self):
#         logging.debug("[Tiller:Terraform:destroy]")
#         pass


# class TillerResource(object):
#     """A TillerResource describes an object which tiller can build, destroy, or describe"""
#     @tl.logged(logging.DEBUG, msg="TillerResource")
#     def __init__(self, name, path, *args, **kwargs):
#         logging.debug("{}:{}\n*args: {}\n**kwargs: {}".format(name, path, args, kwargs))
#         super(TillerResource, self).__init__()
#         self.name = name
#         self.path = path
#         self.namespace = path.split('/')[1]
#         self.description = kwargs.get('description')
#         self.long_description = kwargs.get('long_description')
#         self.depends_on = kwargs.get('depends_on')

#         if self.depends_on:
#             self.depends_on = json.loads(self.depends_on)
#         self.required_vars = kwargs.get('required_vars')
#         if self.required_vars:
#             self.required_vars = json.loads(self.required_vars)
#         self._staged = False
#         self._config_valid = False

#         logging.debug("""
#           name = {}
#           path = {}
#           namespace = {}
#           description = {}
#           long_description = {}
#           depends_on = {}
#           required_vars = {}
#           """.format(self.name,
#                      self.path,
#                      self.namespace,
#                      self.description,
#                      self.long_description,
#                      self.depends_on,
#                      self.required_vars))


#     @classmethod
#     def from_config(cls, config_file):
#         """Create a TillerResource from a configuration file"""
#         configuration = dict()
#         config = ConfigParser.RawConfigParser()
#         config.read(config_file)
#         section = "resource"
#         logging.debug("Creating new resource from config file %s" % config_file)

#         configuration['path'] = os.path.dirname(config_file)
#         logging.debug("Resource path: %s" % configuration['path'])
#         try:
#             for param in config.options(section):
#                 try:
#                     configuration[param] = config.get(section, param).strip("\"").strip("'")
#                 except ConfigParser.NoOptionError:
#                     if param == "name":
#                         logging.warn("'name' option not set in %s" % config_file)
#                         return None
#                     else:
#                         configuration[param] = None
#                         continue
#         except ConfigParser.NoSectionError:
#             logging.error("No section '%s' in '%s'" % (section, config_file))


#         return cls(configuration.pop('name'),
#                    configuration.pop('path'),
#                    **configuration)


#     def validate_tiller_config(self):
#         if all([os.path.exists(self.path), self.name, self.namespace]):
#             self.__config_valid = True
#         return self.__config_valid

#     @abstractmethod
#     def stage(self):
#         """Stages a resource prior to executing a command.
#         Sets environment, parses configuration files, and stops
#         just prior to executing requested command"""
#         pass

#     @abstractmethod
#     def validate(self):
#         """Validate the Resource"""
#         pass

#     def __str__(self):
#         return '{}/{}: {}'.format(self.namespace, self.name, self.path)

#     def __bool__(self):
#         return self.validate_tiller_config()


# class TerraformResource(TillerResource, Terraform):
#     """docstring for TerraformResource"""
#     def __init__(self, name, path, *args, **kwargs):
#         logging.debug("[Tiller:TerraformResource:__init__]")
#         super(TerraformResource, self).__init__(name, path, *args, **kwargs)

#     def plan(self):
#         pass

#     def build(self):
#         pass

#     def show(self):
#         pass

#     def destroy(self):
#         pass


# class PackerResource(TillerResource, Packer):
#     """docstring for PackerResource"""
#     def __init__(self, name, path, *args, **kwargs):
#         logging.debug("Creating PackerResource")
#         super(PackerResource, self).__init__(name, path, *args, **kwargs)
#         self.name = name
#         self.path = path
#         self.args = args
#         self.kwargs = kwargs
#         self._template_extension = '.json.tiller'
#         self._tiller_extention = os.path.splitext(self._template_extension)[1]
#         self._packer_file = None
#         self._staged = False

#     @tl.logged(logging.DEBUG)
#     def stage(self, *args, **kwargs):
#         logging.debug("args: {}".format(args))
#         logging.debug("kwargs: {}".format(kwargs))
#         self._packer_file = self.generate_json(**kwargs)
#         self.validate_tiller_config()
#         self._staged = all([self._config_valid, self._packer_file])
        
#         logging.debug("Staging: self._packer_file: {}".format(self._packer_file))
#         logging.debug("Staging: self._config_valid: {}".format(self._config_valid))
#         logging.debug("Staging: self._staged: {}".format(self._staged))

#         return self._staged

#     @tl.logged(logging.DEBUG)
#     def build(self, *args, **kwargs):
#         if not self._staged:
#             logging.debug("Environment is not staged - attempting to stage")
#             self.stage(*args, **kwargs)
#             logging.debug("self._staged after staging attempt: {}".format(self._staged))
#         if not self._staged:
#             raise TillerException("Unable to build - environment not staged.")

#         logging.debug("args {}".format(args))
#         logging.debug("kwargs {}".format(kwargs))
#         logging.debug("Trying to build {}".format(os.path.join(self.path, self._packer_file)))
#         try:
#             if not subprocess.check_call(['packer','build','-machine-readable',self._packer_file], cwd=self.path, env=os.environ):
#                 logging.error("Could not build {} ({}). See output for details.".format('/'.join([self.namespace, self.name]), self._packer_file))
#                 logging.debug("{} not deleted".format(self._packer_file))
#             else:
#                 logging.info("Resource {} successfully built".format('/'.join([self.namespace, self.name])))
#                 logging.debug("Deleting {}".format(self._packer_file))
#                 os.remove(self._packer_file)
#         except Exception as e:
#             logging.error("Error while building packer file: {}".format(e))

#     @tl.logged(logging.DEBUG)
#     def validate_tiller_config(self):
#         super(PackerResource, self).validate_tiller_config()
#         logging.debug(self.name)
#         config_path = os.path.join(self.path, self.name + self._template_extension)
#         logging.debug("Validating config path: {} ".format(config_path))
#         if os.path.exists(config_path):
#             self._config_valid = True
#         return self._config_valid

#     def validate(self, packer_file=None):
#         if not packer_file:
#             packer_file = self._packer_file

#         try:
#             subprocess.check_call(['packer','validate',packer_file], cwd=self.path)
#             logging.debug("Validated Packer file successfully: {}".format(packer_file))
#             return packer_file
#         except subprocess.CalledProcessError as e:
#             logging.error("{} not a valid config: {}".format(packer_file, e))
#         except Exception as e:
#             logging.error("Error while attempting to validate {}: {}".format(packer_file, e))
#         else:
#             return None


#     # TODO: change this so we can figure out what variables to require. For instance, a
#     #   'secret_bucket' should not be a hard-coded requirement. We should be able to
#     #   infer which variables are required from the template file
#     @tl.logged(logging.DEBUG, msg="Generating JSON")
#     def generate_json(self, *args, **kwargs):
#         logging.debug("args: {}".format(repr(args)))
#         logging.debug("kwargs: %r" % kwargs)

#         _file = os.path.join(self.path, '{}.json.tiller'.format(self.name))
#         with open(_file) as f:
#             template = json.load(f)

#         # bring variables in
#         template_vars = dict(template['variables'])
#         logging.debug("Variables imported from template {}: {}".format(_file, template_vars))

#         env_vars = {
#             'aws_access_key':  os.environ.get('PACKER_ACCESS_KEY'),
#             'aws_secret_key':  os.environ.get('PACKER_SECRET_KEY'),
#             'bucket_access_key':  os.environ.get('PACKER_BUCKET_ACCESS_KEY'),
#             'bucket_secret_key':  os.environ.get('PACKER_BUCKET_SECRET_KEY'),
#             'secret_bucket':  os.environ.get('PACKER_SECRET_BUCKET'),
#             'aws_region':  os.environ.get('PACKER_REGION')
#         }
#         logging.debug(repr(env_vars))

#         # overwrite with ones passed in from the environment
#         for k,v in env_vars.iteritems():
#             logging.debug("attempting to overwrite k: {}, v: {}".format(k,v))
#             # only change the var if it exists. Otherwise leave it alone.
#             template_vars[k] = v if v else template_vars[k]

#         # overwrite w/ kwargs, but only if they match existing keys
#         # (i.e., we don't want to create new keys that are passed in)
#         for key in template_vars.keys():
#             override_val = kwargs.get(key)
#             logging.debug("--var key: {}, --var value: {}".format(key, override_val))
#             template_vars[key] = override_val if override_val else template_vars[key]

#         # Now bail if any variables are empty
#         if None in template_vars.itervalues():
#             raise TillerException("Empty variables in packer configuration are not allowed.")
#         else:
#             with open(_file.rstrip(self._tiller_extention), 'w') as f:
#                 template['variables'] = template_vars
#                 json.dump(template, f, indent=4, separators=[',',': '])

#         # Packer validate, return None if fail, else return the fname of the finished file
#         _out_file = os.path.basename(_file.rstrip(self._tiller_extention))
#         logging.debug("Wrote file: {}".format(_out_file))

#         # return file name if valid or None
#         return self.validate(_out_file)

#     @tl.logged(logging.DEBUG)
#     def plan(self):
#         pass


@tl.logged(logging.DEBUG)
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
                    r = TerraformResource.from_config(os.path.join(root, f))
                elif namespace == 'packer':
                    logging.debug('creating resource')
                    r = PackerResource.from_config(os.path.join(root,f))
                else:
                    r = TillerResource.from_config(os.path.join(root, f))
                # Create a new entry in resource{} with the name of the resource as the value
                if r:
                    rkey = '{}/{}'.format(r.namespace, r.name)
                    resources[rkey] = r

    logging.debug("[Tiller:{}] resources: {}".format(__name__, resources))
    return resources


# TODO: Rather than compile all resources and pick one, start by assuming we know the name
# reach out and grab it, then return the proper TillerResource.from_config()
def resource_by_name(resource_name):
    """return a named resource (namespace/name)"""
    pass


@tl.logged(logging.DEBUG)
def describe(resource):
    """Describe a resource"""
    print "Resource: ", '/'.join([resource.namespace,resource.name])
    prefix="Description: "
    description = textwrap.TextWrapper(initial_indent=prefix,
                                       width = 64,
                                       subsequent_indent = ' '*len(prefix),
                                       replace_whitespace = False,
                                       expand_tabs = True)
    print description.fill(resource.long_description)
    logging.debug(resource)

    if resource.depends_on:
        prefix = "Depends on:"
        depends_text = textwrap.TextWrapper(initial_indent=prefix,
                                            width = 64,
                                            subsequent_indent = ' '*len(prefix),
                                            expand_tabs = True)
        print depends_text.fill("\n".join(resource.depends_on[1:]))
    if resource.required_vars:
        pass


@tl.logged(logging.DEBUG)
def parse_runtime_args(args):
    """
        Given a list of key=value, return a dict
        Validate given list
    """
    return dict(kv.split('=') for kv in args)

def main(args):
    if args['--debug']:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.ERROR)

    if args['plan']:
        # TODO: Implement 'plan'
        logging.info("Planning for {}".format(args['<resource>']))
        plan_args = parse_runtime_args(args['--var'])

        res = compile_resources()
        r = res[args['<resource>']]
        r.plan()

    elif args['build']:
        # TODO: finish build
        logging.info("Building {}".format(args['<resource>']))
        build_args = parse_runtime_args(args['--var'])
        logging.debug("build_args: {}".format(build_args))
        res = compile_resources()
        r = res[args['<resource>']]
        r.build(**build_args)

    elif args['show']:
        # TODO: Implement 'show'
        logging.info("Showing.")
    elif args['describe']:
        resname = args['<resource>']
        logging.info("Describing {}".format(resname))
        try:
            describe(compile_resources()[resname])
        except KeyError as err:
            msg = "No valid resource named {}".format(resname)
            logging.error("[Tiller:{}] {}".format(__name__, msg))
            raise TillerException(msg)



    elif args['destroy']:
        # TODO: Implement 'destroy'
        logging.info("Destroying.")
    elif args['list']:
        logging.info("Listing resources.")
        resources = compile_resources()
        print('The following resources are availble:')
        for r in resources.values():
            if r.depends_on:
                print('\t{:<16}\t{} (Depends on {})'.format(*['/'.join([r.namespace,r.name]), r.description, ', '.join(r.depends_on)]))
            else:
                print('\t{:<16}\t{}'.format(*['/'.join([r.namespace,r.name]), r.description]))


        print('\nFor more information see: ./tiller.py describe <resource>')

    elif args['stage']:
        # TODO: Implement 'stage'
        logging.info("Staging terraform for manual run.")


if __name__ == '__main__':
    args = docopt(__doc__, version='%s v%s' % (name, version))

    # fix for repeating values
    if args['--debug']:
        print args
    main(args)
