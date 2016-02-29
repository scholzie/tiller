#! /usr/bin/env bash
# Description: 
#   This script is a wrapper for Terraform, ostensibly to manage tfstate, but
#   mostly just to make your life more difficult. Much of it was ripped from 
#   the Mozilla Socorro project here:
#       https://github.com/mozilla/socorro-infra
#
# Maintainer: DevOps Kr3w <devops@blueapron.com>
# Author: Chris Scholz <scholzie@blueapron.com> // Don't blame plz

TFVARS="terraform.tfvars"
BUILD_OPTIONS=(global wms demo standard)
HELP=("help" "-h" "--help" "-?")

function help {
    echo "USAGE: ${0} <action> <environment> <build option>"
    echo -n "Valid build options are: "
    local opt 
    for opt in "${BUILD_OPTIONS[@]}"; do
        echo -n "$opt"
    done; echo ""
    exit 1
}

function check_element_exists() {
    local elem
    for elem in "${@:2}"; do
        # If the arg is in the array, short circuit with success
        if [[ "$elem" == "$1" ]]; then
            return 0
        fi
    done
    # otherwise, bail with error
    return 1
}

if which terraform > /dev/null; then 
    echo "terrraform not found in \$PATH"
    echo ""
    help
fi

# Check for help request, lack of arguments, and valid arguments
check_element_exists "$1" "${HELP[@]}"
if [[ "${1}test" == "test" ]]; then
    help
fi
if [[ "$#" != "3" ]]; then
    help
fi
check_element_exists "$3" "${BUILD_OPTIONS[@]}"
if [ $? -ne 0 ]; then
    echo "${3} is not a valid role."
    help
fi

# Check for presence of Terraform
if which terraform > /dev/null; then # Will only produce output on STDERR
    echo "Terraform not found in \$PATH. Please verify installation."
    exit 1
fi

# Get the bucket name from the TFVARs file
BUCKET=$(grep secret_bucket $TFVARS 2>/dev/null)
if [[ "$?" != "0" ]]; then 
    echo "ERROR: Did not get valid secret_bucket name from $TFVARS"
    exit 1
else
    BUCKET=$(echo "$BUCKET" | awk -F\" '{print $2}')
fi

ACTION="$1"
ENVIRONMENT="$2"
BUILD_OPT="$3"

# Fail on errors and be verbose
set -ex
# change to $BUILD_OPT directory
pushd "$BUILD_OPT"

# TODO: Grab tfstate here
aws s3 sync --exclude="*" --include="terraform.tfstate" "s3://${BUCKET}/tfstate/${ENVIRONMENT}/${BUILD_OPT}/" ./

# Run Terraform, but don't fail if TF fails.
set +e
terraform $ACTION -var "environment_name=${ENVIRONMENT}"
EXIT_CODE=$?
# Fail on errors again.
set -e

# Upload tfstate here
aws s3 sync --exclude="*" --include="terraform.tfstate" ./ "s3://${BUCKET}/tfstate/${ENVIRONMENT}/${BUILD_OPT}/" 

# GTFO
popd

exit $EXIT_CODE
