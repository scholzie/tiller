![tiller](http://i.imgur.com/TB3W2EU.jpg)

# Synopsis
`tiller` is a logical progression from `poutine` - it's a python wrapper for packer and terraform which extends `poutine` to allow for resource dependencies, passing inputs to a dependant resource from the outputs of its dependencies, and extensibility by anyone who can write packer or terraform files.

The initial reason for its creation was to allow for easy deployment of staging and development environments to match production by any engineer into his or her own AWS account.

## Contents
| Directory | Description |
| --- | --- |
| `resources` | Contains tiller _resources_. See README.md in that directory for more information on how to write a resource. |
| `tillerlib` | tiller support files | 
| `tiller.py` | The application itself | 
| `poutine` | a wrapper for terraform. Still works - use it until tiller is done. See README.old.md for its proper use. |

# Requirements

To run these tools you will need a few things:
### Installed software:
- [Terraform](https://www.terraform.io/downloads.html), if you want to build cloud infrastructure
- [Packer](https://www.packer.io/downloads.html), if you want to build images
- [direnv](http://direnv.net/) (Optional, but helpful): Allows you to export/unset/edit environment variables per directory. Create a `.envrc` file with the envvars below, and it will only have an effect when you are in the project directory after running `direnv allow`

### An (_emptyish..._) AWS account
Although **tiller** only interacts with your account when it can create or find valid state files, you should not use it with an account that contains anything you would be devastated to see accidentally destroyed until it's out of alpha.

- This tool may be create tons of resources, especially if you are building the `terraform/awsbase` resource for the first time. Chances are, unless you have
  previously taken steps to avoid it, you will hit resource limits by running
  this against an account that is not already empty.
- Set up a non-root user with administrative privileges. Note the access key ID
  and secret access key.
- Set up a role which is connected to the policy `AmazonEC2ContainerServiceforEC2Role` if you plan on using ECS and Docker.

### A bucket for secrets. A "secret bucket".
Create an S3 bucket (with versioning, preferably) to store secrets in. 

These secrets will include: 
- the active tfstate, to maintain state between terraform runs by different people
- a backup of tfstate, tagged with the user who created it, environment, and
  date. This is nice to have if the world explodes and the aforementioned tfstate can't
  be trusted to be the truth anymore.
- Chef's validation.pem file

_**NB:** Because of the sensitive nature of this data, access to this bucket should be
tighly controlled._ Open it for use to the user you created for this tool.

### A good sense of humor
Because it probably won't work the first time.

# Use
Clone the `tiller` repo and checkout `develop`:
```
$ git clone git@github.com:blueapron/tiller.git
$ git checkout develop
```
You also need `docopt` until I package everything up properly:
`$ pip install docopt`

Familiarize yourself with the CLI:
`./tiller.py --help`

You will need to set some environment variables or pass in `--var="key=value"` pairs at the command line. Get started with the ones below. You don't need all of them for all things, but until the templating system is worked out I don't really have a great list of which ones you need for any particular run. _I'm working on it..._

Consider doing this with direnv (see Requirements section).
```
export AWS_ACCESS_KEY_ID="<your key id>"
export AWS_SECRET_ACCESS_KEY="<your secret access key>"
export AWS_REGION=us-east-1
export TILLER_SECRET_BUCKET="<your secret bucket>"
export PACKER_ACCESS_KEY="${AWS_ACCESS_KEY_ID}"
export PACKER_SECRET_KEY="${AWS_SECRET_ACCESS_KEY}"
export PACKER_BUCKET_ACCESS_KEY="${AWS_ACCESS_KEY_ID}"
export PACKER_BUCKET_SECRET_KEY="${AWS_SECRET_ACCESS_KEY}"
export PACKER_REGION="${AWS_REGION}"
export AWS_DEFAULT_REGION="${AWS_REGION}"
export PACKER_VPC_ID="<your vpc>"
export PACKER_SUBNET_ID="<your subnet>"
export PACKER_SECRET_BUCKET="${TILLER_SECRET_BUCKET}"
export IAM_INSTANCE_PROFILE="AmazonECSContainerInstanceRole"
```

### See what resources are available:
`tiller.py list`

### To describe what a resource is and what its depencendies are:
`tiller.py describe <resource>`

### To plan a build:
`tiller.py plan <resource> --env=<environment>`

### To build a resource:
`tiller.py build <resource> --env=<environment>`


## Limitations:
I am not entirely sure that `destroy` works perfectly yet, but it does (apparently) work. 


# Contributing
Please use the `develop` branch for all contributions. All changes should be made in `feature/<feature_name>` or `hotfix/<hotfix_name>` branches. For those of you using `arcanist` (_PLEASE DO_), `arc diff` and `arc push` will automatically reference `origin/develop`. Otherwise, please create your pull requests on `develop` ___and not `master`___

## FIXME (2)
1. poutine/poutine:92           (0) State file correctly tagged, but future runs with different environment names affect previous environments. Not sure why...
2. resources/terraform.py:89    Fake it til you make it

## TODO (20)
1. poutine/poutine:9            Add packer run functionality 
2. poutine/poutine:10           Rename project "tiller", ./poutine -> ./till
3. poutine/poutine:11           Capture output from network creation and pre-fill terraform.tfvars sample for other modules
4. poutine/poutine:12           Add help system (see https://github.com/docopt/docopt)
5. poutine/poutine:106          Make this a little nicer, if you feel like it.
6. poutine/tiller.py:76         Rather than compile all resources and pick one, start by assuming we 
7. poutine/tiller.py:141        update check_deps to wrap a build/plan/etc function to check deps 
8. poutine/tiller.py:192        Finish 'plan'
9. poutine/tiller.py:194        the following pattern is used multiple times.
10. poutine/tiller.py:212       finish 'build'
11. poutine/tiller.py:231       Implement 'show'
12. poutine/tiller.py:245       Implement 'destroy'
13. docker-ecs/main.tf:19       Investigate what SG rules are needed for apps to work
14. docker-ecs/main.tf:85       Figure out subnets automatically. Either use a module, or pre-fill from network output
15. resources/packer.py:132     change this so we can figure out what variables to require.
16. resources/packer.py:192     implement PackerResource.plan()
17. resources/packer.py:197     packer inspect packerfile.json
18. resources/terraform.py:39   if config.tiller has a state_key_ext or state_key_var field, add the ext (literal string)
19. resources/terraform.py:184  implement TerraformResource.show()
20. resources/terraform.py:194  Handle force flag correctly. (I think this is done...)
21. Explain how to set up resources by hand.
22. Make it so you don't gotta do that^^
23. Generate keypairs
24. Configurable ami in base packer image. Ideally, find this based on region