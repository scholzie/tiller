log_level        :info
log_location     STDOUT
chef_server_url  'https://api.chef.io/organizations/<ORG>'
validation_client_name 'validator'
validation_key  '/etc/chef/validator.pem'
environment     'packer-base'
node_name       "packer-ecs"
