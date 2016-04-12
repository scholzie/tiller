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
                logging.debug("creating resource from %s in %s" % (f,root))
                namespace = root.split('/')[1]
                if namespace == 'terraform':
                    r = TerraformResource.from_config(os.path.join(root, f))
                elif namespace == 'packer':
                    logging.debug('creating resource')
                    r = PackerResource.from_config(os.path.join(root,f))
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
# Right now, we just run list_resources() and pull out the correct named one for
# the sake of compatability with the future intent of this function's use.
def resource_by_name(resource_name):
    """return a named resource (namespace/name)"""
    path = os.path.join('resources', os.path.dirname(resource_name))
    resource = os.path.basename(resource_name)
    namespace = path.split('/')[1]
    config = os.path.join(path, "config.tiller")
    logging.debug('resource_name: {}, path: {}, resource_name: {}, '
                  'namespace: {}, config file: {}'.format(
                    resource_name,
                    path,
                    resource,
                    namespace,
                    config))
#     if namespace == 'terraform':
#         r = TerraformResource.from_config(config)
#     elif namespace == 'packer':
#         r = PackerResource.from_config(config)
#     else:
#         r = TillerResource.from_config(config)

    return list_resources()[resource_name]


@tl.logged(logging.DEBUG)
def describe(resource_name):
    """Describe a resource"""
    resource = resource_by_name(resource_name)
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
    elif args['--verbose']:
        logging.basicConfig(level=logging.INFO)
    else:
        logging.basicConfig(level=logging.ERROR)

    if args['plan']:
        # TODO: Implement 'plan'
        logging.info("Planning for {}".format(args['<resource>']))
        plan_args = parse_runtime_args(args['--var'])

        res = list_resources()
        r = res[args['<resource>']]
        r.plan()

    elif args['build']:
        # TODO: finish 'build'
        logging.info("Building {}".format(args['<resource>']))
        build_args = parse_runtime_args(args['--var'])
        logging.debug("build_args: {}".format(build_args))
        r = resource_by_name(args['<resource>'])
        r.build(**build_args)

    elif args['show']:
        # TODO: Implement 'show'
        logging.info("Showing.")

    elif args['describe']:
        resname = args['<resource>']
        logging.info("Describing {}".format(resname))
        try:
            describe(resname)
        except KeyError as err:
            msg = "No valid resource named {}".format(resname)
            logging.error("[Tiller:{}] {}".format(__name__, msg))
            raise tl.TillerException(msg)

    elif args['destroy']:
        # TODO: Implement 'destroy'
        logging.info("Destroying.")

    elif args['list']:
        logging.info("Listing resources.")
        resources = list_resources()
        print('The following resources are availble:')
        for r in resources.values():
            if r.depends_on:
                print('\t{:<16}\t{} (depends on {})'.format(*['/'.join(
                [r.namespace,r.name]), r.description, ', '.join(r.depends_on)]))
            else:
                print('\t{:<16}\t{}'.format(*['/'.join([r.namespace,r.name]), 
                                            r.description]))


        print('\nFor more information see: ./tiller.py describe <resource>')

    elif args['stage']:
        logging.info("Staging for manual run.")
        logging.info("REMINDER: This will leave things in a potentially unclean"
                     " state. Recommended that you clean up afterwards.")
        r = resource_by_name(args['<resource>'])
        r.stage(**parse_runtime_args(args['--var']))


if __name__ == '__main__':
    args = docopt(__doc__, version='%s v%s' % (name, version))

    # fix for repeating values
    if args['--debug']:
        print args
    main(args)
