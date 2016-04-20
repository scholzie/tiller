import tillerlib.tillerlib as tl
from tillerlib.resources.tiller import TillerResource
import os
import shutil
import subprocess
import logging

class TerraformResource(TillerResource):
    """docstring for TerraformResource"""
    def __init__(self, name, path, *args, **kwargs):
        logging.debug("[Tiller:TerraformResource:__init__]")
        super(TerraformResource, self).__init__(name, path, *args, **kwargs)
        self.name = name
        self.path = path
        self.tf_state_key = None
        self._global_terraform_args = '-no-color'.split()
        self._plan_args = "-detailed-exitcode".split()


    def setEnvironment(self, env):
        #remove all whitespace
        self.environment = ''.join(env.split())


    @tl.logged(logging.DEBUG)
    def cleanup(self):
        """Delete local tfstate files"""
        if os.path.exists(os.path.join(self.path, ".terraform")):
            try:
                os.remove(os.path.join(self.path, ".terraform", "terraform.tfstate"))
                shutil.rmtree(os.path.join(self.path, '.terraform', '.tiller'), ignore_errors=True)
            except OSError:
                logging.debug("No tfstate file found in {}".format(os.path.join(self.path, '.terraform')))
        else:
            logging.debug("No local .terraform directory exists.")
        pass

    @tl.logged(logging.DEBUG)
    # TODO: if config.tiller has a state_key_ext or state_key_var field, add the ext (literal string)
    # or var (interpolated, whitespace-stripped variable) to the state_key. This ensures that
    # resources which are identical other than their name will not share the same statefile. This is
    # particularly an issue for ECS clusters which should not share AWS resources
    def setup_remote_state(self, bucket, state_key, *args, **kwargs):
        """Set the remote state key. On success, returns True, else False."""
        tf_dot_dir = os.path.join(self.path, '.terraform')
        tiller_dot_dir = os.path.join(self.path, '.tiller')
        tfstate = os.path.join(tf_dot_dir, 'terraform.tfstate')
        logging.debug("Checking for tfstate file at {}".format(tfstate))
        if os.path.isfile(tfstate):
            logging.debug("Found tfstate file ({}).".format(tfstate))
            try:
                if not os.path.isdir(tiller_dot_dir):
                    logging.debug("Creating {}".format(tiller_dot_dir))
                    os.mkdir(tiller_dot_dir)
                logging.debug("Moving tfstate from {} to {}".format(
                                    tfstate, os.path.join(tiller_dot_dir, os.path.basename(tfstate))))
                shutil.move(tfstate, os.path.join(tiller_dot_dir, os.path.basename(tfstate)) )
            except Exception as e:
                logging.debug("Encountered error while trying to backup {}: {}".format(tfstate, e))
                self._staged = False
        else:
            logging.debug("No local tfstate file found.")
        cmd = "terraform remote config".split()
        args =  ['-backend=s3',
                '-backend-config=bucket=%s' % bucket,
                '-backend-config=key=%s' % state_key]
        logging.debug("Executing %r in %s" % (cmd + args, self.path))
        return True if tl.run(cmd, args, self.path,
                   log_only = True) == 0 else False

    def pull_remote_state(self):
        return tl.run('terraform remote pull'.split(), cwd=self.path)

    @tl.logged(logging.DEBUG)
    def stage(self, *args, **kwargs):

        if not self._staged:
            logging.debug("Environment not staged. Attempting to stage.")
            if not self.environment:
                raise tl.TillerException("Mandatory environment name for {} is not set.".format(self))

            try:
                tl.run('terraform get'.split(), cwd=self.path,
                   log_only = True )
            except Exception as e:
                logging.error("Encountered error while tryiing 'terraform get': %s" % e)


            # TODO: Better buckets - use config hierarchy (tl.getvar())
            bucket = os.environ.get('TILLER_SECRET_BUCKET')
            if not bucket:
                raise tl.TillerException("No secret bucket set. Ensure the"
                " TILLER_SECRET_BUCKET environment variable exists.")
            self.tf_state_key = kwargs.get('alternate_state_key')
            if not self.tf_state_key:
                self.tf_state_key = '%s_%s' % (self.name, self.environment)
            if all([self.validate(),
                    self.setup_remote_state(bucket, self.tf_state_key, *args, **kwargs)]):
                self._staged = True
            else:
                self._staged = False
            logging.debug("self._staged after staging attempt: {}".format(self._staged))

        return self._staged


    def validate(self, *args, **kwargs):
        logging.debug("args {}".format(args))
        logging.debug("kwargs {}".format(kwargs))

        try:
            cmd = "terraform validate".split()
            args = self._global_terraform_args
            return True if tl.run(cmd, args, self.path,
                   log_only = any([kwargs.get('verbose'), kwargs.get('debug')])) == 0 else False
        except Exception as e:
            logging.error("Terraform validation error: {}".format(e))
            raise


    @tl.logged(logging.DEBUG)
    def check_stage(self, *args, **kwargs):
        if not self._staged:
            logging.debug("Environment not staged - attempting to stage")
            self.stage(*args, **kwargs)
            logging.debug("Staged after attempt? {}".format(self._staged))
        if not self._staged:
            raise tl.TillerException("Unable to stage environment")

        return self._staged


    @tl.logged(logging.DEBUG)
    def plan(self, output=True, *args, **kwargs):
        """Plan a terraform run. If output=True, print (or log) the output. In any case,
        return True True if a plan will require changes, or False if the infrastructure
        already exists as described."""

        logging.debug("args {}".format(args))
        logging.debug("kwargs {}".format(kwargs))
        logging.debug("Depends on: {}".format(self.depends_on))
        try:
            self.check_stage(*args, **kwargs)

            cmd = "terraform plan".split()
            args = self._global_terraform_args
            args += self._plan_args
            args += ['-var', 'environment_name={}'.format(self.environment)]
            log_only = True if not output else any([kwargs.get('verbose'), kwargs.get('debug')])
            exit = tl.run(cmd, args, self.path,
                   log_only = log_only)
            if exit == 0:
                logging.info("No changes required.")
                return True
            elif exit == 2:
                logging.info("Changes required.")
                return False
            else:
                raise tl.TillerException("Terraform plan threw an error. "
                                         "See outout for more details (try re-running with --verbose or --debug)")
        except Exception as e:
            logging.error("Error while planning: {}".format(e))
            raise
        finally:
            self.cleanup()



    @tl.logged(logging.DEBUG)
    def build(self, *args, **kwargs):

        logging.debug("args {}".format(args))
        logging.debug("kwargs {}".format(kwargs))

        try:
            self.check_stage(*args, **kwargs)

            cmd = "terraform apply".split()
            args = self._global_terraform_args
            args += ['-var', 'environment_name={}'.format(self.environment)]
            tl.run(cmd, args, self.path, log_only=any([kwargs.get('verbose'), kwargs.get('debug')]))
        except Exception as e:
            logging.error("Error while building: {}".format(e))
            raise
        finally:
            self.cleanup()


    def show(self, *args, **kwargs):
        # TODO: implement TerraformResource.show()
        try:
            self.check_stage(*args, **kwargs)
            tl.run('terraform show'.split(), cwd=self.path)
        except Exception as e:
            logging.error("Error while showing: {}".format(e))
            raise
        finally:
            self.cleanup()

    def destroy(self, *args, **kwargs):
        # TODO: Handle force flag correctly.
        logging.debug("args {}".format(args))
        logging.debug("kwargs {}".format(kwargs))

        try:
            self.check_stage(*args, **kwargs)

            cmd = "terraform destroy".split()
            args = self._global_terraform_args
            args += ['-var', 'environment_name={}'.format(self.environment)]
            if kwargs.get('force'):
                args += ['-force']
            tl.run(cmd, args, self.path,
                   log_only = any([kwargs.get('verbose'), kwargs.get('debug')]))
        except Exception as e:
            logging.error("Error while destroying: {}".format(e))
            raise
        finally:
            self.cleanup()
