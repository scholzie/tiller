# See http://docs.chef.io/config_rb_knife.html for more information on knife configuration options

current_dir = File.dirname(__FILE__)
log_level                :info
log_location             STDOUT
node_name                "scholzie"
client_key               "#{current_dir}/scholzie.pem"
validation_client_name   "blueapron-validator"
validation_key           "#{current_dir}/blueapron-validator.pem"
chef_server_url          "https://api.chef.io/organizations/blueapron"
cookbook_path            ["#{current_dir}/../cookbooks"]
