log_level        :info
log_location     STDOUT
chef_server_url  'https://api.chef.io/organizations/blueapron'
validation_client_name 'blueapron-validator'
validation_key  '/etc/chef/validator.pem'
environment     'ba-packer-base'
node_name       "packer-ecs"
