#!/bin/bash

cat <<CHEFCONFIG > /etc/chef/first-boot.json
{
    "policy_name": "${policy_name}",
    "policy_group": "${host_environment}"
}
CHEFCONFIG

chef-client -j /etc/chef/first-boot.json 
