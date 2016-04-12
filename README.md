# Synopsis
`tiller` is a logical progression from `poutine` - it's a python wrapper for packer and terraform which extends `poutine` to allow for resource dependencies, passing inputs to a dependant resource from the outputs of its dependencies, and extensibility by anyone who can write packer or terraform files.

The initial reason for its creation was to allow for easy deployment of staging and development environments to match production by any engineer into his or her own AWS account.

## Contents
| Directory | Description |
| --- | --- |
| resources | Contains tiller _resources_. See README.md in that directory for more information on how to write a resource. |
| tillerlib | tiller support files | 
| tiller.py | The application itself | 
| poutine | a wrapper for terraform. Still works - use it until tiller is done. See README.old.md for its proper use. |

# Requirements

To run these tools you will need a few things:
### An (_emptyish..._) AWS account
- This tool will be creating tons of resources. Chances are, unless you have
  previously taken steps to avoid it, you will hit resource limits by running
  this against an account that is not already empty.
- Set up a non-root user with administrative privileges. Note the access key ID
  and secret access key.

### A bucket for secrets. A "secret bucket".
Create an S3 bucket (with versioning, preferably) to store secrets in. 

These secrets will include: 
- the active tfstate, to maintain state between terraform runs by different people
- a backup of tfstate, tagged with the user who created it, environment, and
  date. This is nice to have if the world explodes and the aforementioned tfstate can't
  be trusted to be the truth anymore.
- Chef's validation.pem file

*NB: Because of the sensitive nature of this data, access to this bucket should be
tighly controlled.* Open it for use to the user you created for this tool. 

### A good sense of humor
Because it probably won't work the first time.

# Use
For starters, get comfortable with the CLI:
`./tiller.py --help`

You will need to set some environment variables or pass in `--var="key=value"` pairs at the command line. Get started with these. You don't need all of them for all things, but until the templating system is worked out I don't have a great list of which ones you need for any particular run.
```
export AWS_ACCESS_KEY_ID="<your key id>"
export AWS_SECRET_ACCESS_KEY="<your secret access key>"
export AWS_REGION=us-east-1
export PACKER_ACCESS_KEY="${AWS_ACCESS_KEY_ID}"
export PACKER_SECRET_KEY="${AWS_SECRET_ACCESS_KEY}"
export PACKER_BUCKET_ACCESS_KEY="${AWS_ACCESS_KEY_ID}"
export PACKER_BUCKET_SECRET_KEY="${AWS_SECRET_ACCESS_KEY}"
export PACKER_REGION="${AWS_REGION}"
export AWS_DEFAULT_REGION="${AWS_REGION}"
export PACKER_VPC_ID="<your vpc>"
export PACKER_SUBNET_ID="<your subnet>"
export PACKER_SECRET_BUCKET="<your secret bucket>"
export IAM_INSTANCE_PROFILE="AmazonECSContainerInstanceRole"
```

## Limitations:
Currenlty, only `packer` resources actually do anything. `Terraform` resources are much more complicated and I've chosen to implement them last.

The commands that actually do anything useful:
- `./tiller.py list`
- `./tiller.py describe`
- `./tiller.py build`
- `./tiller.py stage`
- `./tiller.py <option> [-v | --verbose]`
- `./tiller.py <command> [-D| --debug]`

# Contributing
Please use the `develop` branch for all contributions. All changes should be made in `feature/<feature_name>` or `hotfix/<hotfix_name>` branches. For those of you using `arcanist` (_PLEASE DO_), `arc diff` and `arc push` will automatically reference `origin/develop`. Otherwise, please create your pull requests on `develop` and not `master`

# Planned Changes
## FIXME (1)
1. poutine/poutine:131       (0) State file correctly tagged, but future runs with different environment names affect previous environments. Not sure why...

## TODO (13)
1. poutine/poutine:9         Add packer run functionality 
2. poutine/poutine:10        Rename project "tiller", ./poutine -> ./till
3. poutine/poutine:11        Capture output from network creation and pre-fill terraform.tfvars sample for other modules
4. poutine/poutine:12        Add help system (see https://github.com/docopt/docopt)
5. poutine/poutine:95        Make this a little nicer, if you feel like it.
6. poutine/tiller.py:73      Rather than compile all resources and pick one, start by assuming we 
7. poutine/tiller.py:145     Implement 'plan'
8. poutine/tiller.py:154     finish build
9. poutine/tiller.py:162     Implement 'show'
10. poutine/tiller.py:176    Implement 'destroy'
11. docker-ecs/main.tf:19    Investigate what SG rules are needed for apps to work
12. docker-ecs/main.tf:85    Figure out subnets automatically. Either use a module, or pre-fill from network output
13. resources/packer.py:121  change this so we can figure out what variables to require.
