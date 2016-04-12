import tillerlib.tillerlib as tl
from tillerlib.resources.tiller import TillerResource
import logging
import os
import json
import subprocess

class PackerResource(TillerResource):
    """docstring for PackerResource"""
    def __init__(self, name, path, *args, **kwargs):
        logging.debug("Creating PackerResource")
        super(PackerResource, self).__init__(name, path, *args, **kwargs)
        self.name = name
        self.path = path
        self.args = args
        self.kwargs = kwargs
        self._template_extension = '.json.tiller'
        self._tiller_extention = os.path.splitext(self._template_extension)[1]
        self._packer_file = None
        self._staged = False

    @tl.logged(logging.DEBUG)
    def stage(self, *args, **kwargs):
        logging.debug("args: {}".format(args))
        logging.debug("kwargs: {}".format(kwargs))
        self._packer_file = self.generate_json(**kwargs)
        self.validate_tiller_config()
        self._staged = all([self._config_valid, self._packer_file])
        
        logging.debug("Staging: self._packer_file: {}".format(self._packer_file))
        logging.debug("Staging: self._config_valid: {}".format(self._config_valid))
        logging.debug("Staging: self._staged: {}".format(self._staged))

        return self._staged

    @tl.logged(logging.DEBUG)
    def build(self, *args, **kwargs):
        if not self._staged:
            logging.debug("Environment is not staged - attempting to stage")
            self.stage(*args, **kwargs)
            logging.debug("self._staged after staging attempt: {}".format(self._staged))
        if not self._staged:
            raise TillerException("Unable to build - environment not staged.")

        logging.debug("args {}".format(args))
        logging.debug("kwargs {}".format(kwargs))
        logging.debug("Trying to build {}".format(os.path.join(self.path, self._packer_file)))
        try:
            if not subprocess.check_call(['packer','build','-machine-readable',self._packer_file], cwd=self.path, env=os.environ):
                logging.error("Could not build {} ({}). See output for details.".format('/'.join([self.namespace, self.name]), self._packer_file))
                logging.debug("{} not deleted".format(self._packer_file))
            else:
                logging.info("Resource {} successfully built".format('/'.join([self.namespace, self.name])))
                logging.debug("Deleting {}".format(self._packer_file))
                os.remove(self._packer_file)
        except Exception as e:
            logging.error("Error while building packer file: {}".format(e))

    @tl.logged(logging.DEBUG)
    def validate_tiller_config(self):
        super(PackerResource, self).validate_tiller_config()
        logging.debug(self.name)
        config_path = os.path.join(self.path, self.name + self._template_extension)
        logging.debug("Validating config path: {} ".format(config_path))
        if os.path.exists(config_path):
            self._config_valid = True
        return self._config_valid

    def validate(self, packer_file=None):
        if not packer_file:
            packer_file = self._packer_file

        try:
            subprocess.check_call(['packer','validate',packer_file], cwd=self.path)
            logging.debug("Validated Packer file successfully: {}".format(packer_file))
            return packer_file
        except subprocess.CalledProcessError as e:
            logging.error("{} not a valid config: {}".format(packer_file, e))
        except Exception as e:
            logging.error("Error while attempting to validate {}: {}".format(packer_file, e))
        else:
            return None


    # TODO: change this so we can figure out what variables to require. For instance, a
    #   'secret_bucket' should not be a hard-coded requirement. We should be able to
    #   infer which variables are required from the template file
    @tl.logged(logging.DEBUG, msg="Generating JSON")
    def generate_json(self, *args, **kwargs):
        logging.debug("args: {}".format(repr(args)))
        logging.debug("kwargs: %r" % kwargs)

        _file = os.path.join(self.path, '{}.json.tiller'.format(self.name))
        with open(_file) as f:
            template = json.load(f)

        # bring variables in
        template_vars = dict(template['variables'])
        logging.debug("Variables imported from template {}: {}".format(_file, template_vars))

        env_vars = {
            'aws_access_key':  os.environ.get('PACKER_ACCESS_KEY'),
            'aws_secret_key':  os.environ.get('PACKER_SECRET_KEY'),
            'bucket_access_key':  os.environ.get('PACKER_BUCKET_ACCESS_KEY'),
            'bucket_secret_key':  os.environ.get('PACKER_BUCKET_SECRET_KEY'),
            'secret_bucket':  os.environ.get('PACKER_SECRET_BUCKET'),
            'aws_region':  os.environ.get('PACKER_REGION')
        }
        logging.debug(repr(env_vars))

        # overwrite with ones passed in from the environment
        for k,v in env_vars.iteritems():
            logging.debug("attempting to overwrite k: {}, v: {}".format(k,v))
            # only change the var if it exists. Otherwise leave it alone.
            template_vars[k] = v if v else template_vars[k]

        # overwrite w/ kwargs, but only if they match existing keys
        # (i.e., we don't want to create new keys that are passed in)
        for key in template_vars.keys():
            override_val = kwargs.get(key)
            logging.debug("--var key: {}, --var value: {}".format(key, override_val))
            template_vars[key] = override_val if override_val else template_vars[key]

        # Now bail if any variables are empty
        if None in template_vars.itervalues():
            raise TillerException("Empty variables in packer configuration are not allowed.")
        else:
            with open(_file.rstrip(self._tiller_extention), 'w') as f:
                template['variables'] = template_vars
                json.dump(template, f, indent=4, separators=[',',': '])

        # Packer validate, return None if fail, else return the fname of the finished file
        _out_file = os.path.basename(_file.rstrip(self._tiller_extention))
        logging.debug("Wrote file: {}".format(_out_file))

        # return file name if valid or None
        return self.validate(_out_file)

    @tl.logged(logging.DEBUG)
    def plan(self):
        pass