#!/usr/bin/env python
"""
Usage:
    tiller.py [options] plan <resource> [--destroy] [--var=<key=val>]...
    tiller.py [options] build <resource> [--var=<key=val>]...
    tiller.py [options] show <resource> [--var=<key=val>]...
    tiller.py [options] destroy <resource> [--var=<key=val>]...
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
    --alternate-state-key=KEY   specify an alternate terraform state-key
                                (This is useful if you already have an
                                environment built under a different key name)
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
import textwrap

name = 'tiller'
version = '0.0.1'


@tl.logged(logging.DEBUG)
def list_resources():
    resources = {}
    # Enter resources subdirectory(-ies) and look for config files
    resources_dirname = "resources"
    config_filename = "config.tiller"
    for root, dirs, files in os.walk(resources_dirname):
        for f in files:
            if f == config_filename:
                logging.debug("creating resource from %s in %s" % (f, root))
                namespace = root.split('/')[1]
                if namespace == 'terraform':
                    r = TerraformResource.from_config(os.path.join(root, f))
                elif namespace == 'packer':
                    logging.debug('creating resource')
                    r = PackerResource.from_config(os.path.join(root, f))
                else:
                    r = TillerResource.from_config(os.path.join(root, f))
                # Create a new entry in resource{} with the name of the
                # resource as the value
                if r:
                    rkey = '{}/{}'.format(r.namespace, r.name)
                    resources[rkey] = r

    logging.debug("[Tiller:{}] resources: {}".format(__name__, resources))
    return resources


# TODO: Rather than compile all resources and pick one, start by assuming we
# know the name reach out and grab it, then return the proper
# TillerResource.from_config(). As this stands, this will only work if the name
# of the resource is the same as its directory, which we don't enforce.
# Right now, we just run list_resources() and pull out the correct named one
# for the sake of compatability with the future intent of this function's use.
def resource_by_name(resource_name):
    """return a named resource (namespace/name)"""
    # path = os.path.join('resources', os.path.dirname(resource_name))
    # resource = os.path.basename(resource_name)
    # namespace = path.split('/')[1]
    # config = os.path.join(path, "config.tiller")
    # logging.debug('resource_name: {}, path: {}, resource_name: {}, '
    #               'namespace: {}, config file: {}'.format(
    #                 resource_name,
    #                 path,
    #                 resource,
    #                 namespace,
    #                 config))
    try:
        return list_resources()[resource_name]
    except KeyError:
        logging.error("No resource named {}".format(resource_name))
        exit(1)
    except Exception as e:
        logging.error(e)
        raise


@tl.logged(logging.DEBUG)
def describe(resource_name):
    """Describe a resource"""
    resource = resource_by_name(resource_name)
    print "Resource: ", '/'.join([resource.namespace, resource.name])
    prefix = "Description: "
    description = textwrap.TextWrapper(initial_indent=prefix,
                                       width=64,
                                       subsequent_indent=' ' * len(prefix),
                                       replace_whitespace=False,
                                       expand_tabs=True)
    print description.fill(resource.long_description)
    logging.debug(resource)

    if resource.depends_on:
        prefix = "Depends on: "
        depends_text = textwrap.TextWrapper(initial_indent=prefix,
                                            width=64,
                                            subsequent_indent=' ' * len(prefix),
                                            expand_tabs=True)
        print depends_text.fill("\n".join(resource.depends_on))
    if resource.required_vars:
        prefix = "Required vars: "
        rv_text = textwrap.TextWrapper(initial_indent=prefix,
                                       width=64,
                                       subsequent_indent=' ' * len(prefix),
                                       expand_tabs=True)
        rvs = sorted(resource.required_vars.keys())
        print rv_text.fill('\n'.join(rvs))


@tl.logged(logging.DEBUG)
def parse_runtime_vars(args):
    """
        Given a list of key=value, return a dict of those values
    """
    # split on the first occurrence of '='. this is to allow equals character in the values
    return dict(kv.split('=', 1) for kv in args)


@tl.logged(logging.DEBUG)
def check_deps(resource, **kwargs):
    """Check a resource and return the number out outstanding dependencies"""

    # TODO: update check_deps to wrap a build/plan/etc function to check deps
    # before doing anythingm, then just run it. This removes the need to use
    # the same patten in each step in main()

    print "Checking dependencies for {}...".format(resource)
    deps_outstanding = 0
    if not resource.depends_on:
        return 0
    try:
        for dep in resource.depends_on:
            print "Processing dependency {}".format(dep)
            dep_r = resource_by_name(dep)
            dep_r.environment = resource.environment
            logging.debug("Planning kwargs: {}".format(kwargs))
            if dep_r.plan(output=False, **kwargs):
                print "{} exists. Continuing.".format(dep)
            else:
                print("{}::{} does not yet exist. "
                      "Please build it first.".format(dep_r.environment, dep))
                deps_outstanding += 1
    except Exception as e:
        logging.error("Error while checking dependencies: {}".format(e))

    return deps_outstanding

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


def main(args):

    runtime_vars = dict()

    if args['--debug']:
        logging.basicConfig(level=logging.DEBUG)
        runtime_vars['debug'] = True
    elif args['--verbose']:
        logging.basicConfig(level=logging.INFO)
        runtime_vars['verbose'] = True
    else:
        logging.basicConfig(level=logging.ERROR)

    if args['--env']:
        env = ''.join(args['--env'].split())  # nowhitespaceplease
    else:
        env = None

    if args['--var']:
        runtime_vars = parse_runtime_vars(args['--var'])

    if args['--alternate-state-key']:
        runtime_vars['alternate_state_key'] = args['--alternate-state-key']

    if args['--force']:
        runtime_vars['force'] = args['--force']

    if any([args['plan'], args['build'], args['destroy'], args['show']]):
        try:
            userinfo = tl.get_account_info()
            infostring = "Working within account {}, User: {}".format(
                userinfo['arn'], userinfo['username'])
            border = '=' * len(infostring)
            print('\n{}\n{}\n{}'.format(border, infostring, border))
            if not args['--force']:
                warning = '!' * 5 + ' '
                warning += "If this is not correct, "
                warning += "press Ctrl-C to bail out now"
                warning += ' ' + '!' * 5
                border = '=' * len(warning)
                print("{}\n{}\n{}".format(border, warning, border))
                raw_input("Press Enter to continue.")
        except KeyboardInterrupt as ki:
            logging.debug(ki)
            exit(1)

    if args['plan']:
        # TODO: Finish 'plan'
        print "Planning {}...".format(args['<resource>'])
        # TODO: the following pattern is used multiple times.
        # Consider using a function to wrap it.
        try:
            r = resource_by_name(args['<resource>'])
            r.environment = env if env else None
            deps = check_deps(r, **runtime_vars)
            if deps == 0:
                r.plan(**runtime_vars)
            else:
                print ("There are {} dependencies outstanding. Will not "
                       "continue planning of {}/{}. Please check output above "
                       "for details.".format(deps, r.namespace, r.name))
        except tl.TillerException as te:
            print te[1]
        except Exception as e:
            logging.error(e)

    elif args['build']:
        # TODO: finish 'build'
        print "Building {}...".format(args['<resource>'])
        logging.debug("build_args: {}".format(runtime_vars))
        try:
            r = resource_by_name(args['<resource>'])
            r.environment = env if env else None
            deps = check_deps(r, **runtime_vars)
            if deps == 0:
                r.build(**runtime_vars)
            else:
                print ("There are {} dependencies outstanding. Will not "
                       "continue building {}/{}. Please check output above "
                       "for details.".format(deps, r.namespace, r.name))
        except tl.TillerException as te:
            print te[1]
        except Exception as e:
            logging.error(e)

    elif args['show']:
        resname = args['<resource>']
        logging.info("Showing details for {}".format(resname))
        logging.debug("Show args: {}".format(runtime_vars))
        r = resource_by_name(resname)
        r.environment = env if env else None
        try:
            r.show(**runtime_vars)
        except tl.TillerException as te:
            print te[1]
        except Exception as e:
            logging.error(e)

    elif args['describe']:
        resname = args['<resource>']
        logging.info("Describing {}".format(resname))
        try:
            describe(resname)
        except KeyError:
            msg = "No valid resource named {}".format(resname)
            logging.error("[Tiller:{}] {}".format(__name__, msg))
            raise tl.TillerException(msg)
    elif args['destroy']:
        logging.info("Destroying {}".format(args['<resource>']))
        logging.debug("destroy_args: {}".format(runtime_vars))
        r = resource_by_name(args['<resource>'])
        r.environment = env if env else None
        try:
            if not args['--force']:
                yorn = raw_input("You are about to DESTROY {} in {}. "
                                 "Are you sure? "
                                 "[yes/NO]: ".format(r.name, r.environment))
                while yorn in 'Y y'.split():
                    yorn = raw_input("Please type 'yes' to continue: ")
                if not re.match("[Yy][Ee][Ss]", yorn):
                    print "Exiting..."
                    exit()
                else:
                    runtime_vars['force_destroy'] = True
            else:
                runtime_vars['force_destroy'] = True

            r.destroy(**runtime_vars)
        except tl.TillerException as te:
            print te[1]
        except KeyboardInterrupt as ki:
            logging.debug(ki)
            exit()
        except Exception as e:
            logging.error(e)

    elif args['list']:
        logging.info("Listing resources.")
        resources = list_resources()
        print('The following resources are availble:')
        for r in resources.values():
            if r.depends_on:
                print('\t{:<16}\t{} (depends on {})'.format(*['/'.join(
                    [r.namespace, r.name]),
                    r.description,
                    ', '.join(r.depends_on)]))
            else:
                print('\t{:<16}\t{}'.format(*['/'.join([r.namespace, r.name]),
                                            r.description]))
        print('\nFor more information see: ./tiller.py describe <resource>')

    elif args['stage']:
        logging.info("Staging for manual run.")
        logging.info("NOTE: This will leave things in a potentially unclean "
                     "state. Recommended that you clean up afterwards.")
        r = resource_by_name(args['<resource>'])
        r.environment = env if env else None
        try:
            if r.stage(**runtime_vars):
                logging.info("Successfully staged {}".format(r.name))
        except tl.TillerException as te:
            print te[1]
        except Exception as e:
            logging.error(e)


if __name__ == '__main__':
    args = docopt(__doc__, version='%s v%s' % (name, version))

    # fix for repeating values
    if args['--debug']:
        print args
    main(args)
