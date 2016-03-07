#
# Cookbook Name:: ba_base-0.1.0
# Recipe:: chef-client
#
# Copyright (c) 2016 The Authors, All Rights Reserved.

template '/etc/chef/client.rb' do
    source 'client.rb.erb'
    owner 'root'
    group 'root'
    mode '0755'
end
