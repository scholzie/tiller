#! /usr/bin/env bash
# Bootstraps a host to run its first chef run

set -e
[[ $DEBUG_PROVISION_SCRIPT ]] && set -x

CHEF_SERVER=${CHEF_SERVER:-https://api.chef.io}
CHEF_VALIDATOR_CLIENT=${CHEF_VALIDATOR_CLIENT:-validator}
LOGPATH=/tmp/provision.$(date +%s).log

function help {
	echo "USAGE: ${0} <aws_region> <s3_bucket>"
	echo ""
	echo "This script is meant to run from packer. Please don't run it directly."
	echo "Additionally, AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY environment variables must be set appropriately."
	echo ""
	exit 1
}

function teestamp {
	while IFS= read -r line; do
	    DATETIME=`date '+%b %d %H:%M:%S'`
    	echo "${DATETIME} BOOTSTRAP: ${line}"
    done | tee -a $LOGPATH
}

env

# if [[ $# -ne 1 ]]; then
# 	echo "Expecting one argument: secret bucket."
# 	help
# else
# 	PACKER_SECRET_BUCKET="$1"
# fi

# Access/Secret keys come from instance metadata - should exist.
if [[ -z "$AWS_ACCESS_KEY_ID" ]]; then
    echo "\$AWS_ACCESS_KEY_ID is not set. Bailing." | teestamp
    exit 1
elif [[ -z "$AWS_SECRET_ACCESS_KEY" ]]; then
    echo "\$AWS_SECRET_ACCESS_KEY is not set. Bailing." | teestamp
    exit 1
elif [[ -z "$PACKER_SECRET_BUCKET" ]]; then
    echo "\$SECRET_BUCKET is not set. Bailing." | teestamp
    exit 1
fi

echo "=== Starting Provisioning ===" | teestamp
echo "Writing log to $LOGPATH." | teestamp

echo "Creating /etc/chef..." | teestamp
sudo mkdir -p /etc/chef | teestamp
#sudo mkdir -p /etc/chef/ohai/hints | teestamp
#sudo touch /etc/chef/ohai/hints/ec2.json | teestamp
#sudo touch /etc/chef/ohai/hints/iam.json | teestamp

echo "apt-get update..." | teestamp
sudo apt-get update -y 2>&1 | teestamp

echo "Installing python-pip..." | teestamp
# about half the time apt-get fails to install python-pip, so we will do it
# with the install script
#sudo apt-get install python-pip -y 2>&1 | teestamp
pushd /tmp
curl "https://bootstrap.pypa.io/get-pip.py" -o "get-pip.py"
sudo python get-pip.py
rm /tmp/get-pip.py
popd

echo "Installing awscli..." | teestamp
sudo pip install awscli 2>&1 | teestamp

=======
echo "Writing client.rb..." | teestamp
cat << EOF > /tmp/base-client.rb
log_level        :info
log_location     STDOUT
chef_server_url  '${CHEF_SERVER}'
validation_client_name '${CHEF_VALIDATOR_CLIENT}'
validation_key  '/etc/chef/validation.pem'
environment     'base'
EOF
sudo cp /tmp/base-client.rb /etc/chef/client.rb 2>&1 | teestamp

echo "Retrieving chef credentials from ${PACKER_SECRET_BUCKET}..." | teestamp
aws s3 cp s3://${PACKER_SECRET_BUCKET}/validator.pem /tmp/validator.pem 2>&1 | teestamp
sudo cp /tmp/validator.pem /etc/chef/validation.pem 2>&1 | teestamp

echo "=== Finished ===" | teestamp
sudo mv "$LOGPATH" /root/
