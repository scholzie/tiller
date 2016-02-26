#! /usr/bin/env bash
# Description: 
#   This script is a wrapper for Terraform, ostensibly to manage tfstate, but
#   mostly just to make your life more difficult.
#
# Maintainer: DevOps Kr3w <devops@blueapron.com>
# Author: Chris Scholz <scholzie@blueapron.com> // Don't blame him

TFVARS="terraform.tfvars"
BUILD_OPTIONS=(global wms demo basic)
HELP=("help" "-h" "--help" "-?")

function help {
    echo "USAGE: ${0} <action> <environment> <build option>"
    echo -n "Valid build options are: "
    local opt 
    for opt in "${ROLES[@]}"; do
        echo -n "$opt"
    done; echo ""
    exit 1
}

function check_element_exists() {
    local elem
    for elem in "${@:2}"; do
        # If the arg is in the array, short circuit with success
        [[ "$elem" == "$1" ]] && return 0
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
[[ "${1}test" == "test" ]] && help
[[ "$#" != "3" ]] && help
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

ACTION="$1"
ENVIRONMENT="$2"
BUILD_OPT="$3"

set -ex

# TODO: Grab tfstate here

# Run Terraform
set +e
terraform $ACTION -var "environment_name=${ENVIRONMENT}"
EXIT_CODE=$?
set -e

# TODO: Upload tfstate here

exit $EXIT_CODE
