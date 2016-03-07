default[:apt][:compile_time_update] = true

default[:authorization][:sudo][:groups] = [:sysadmin, :ubuntu]
default[:authorization][:sudo][:passwordless] = true

default[:ntp][:servers] = ['0.amazon.pool.ntp.org',
                           '1.amazon.pool.ntp.org',
                           '2.amazon.pool.ntp.org',
                           '3.amazon.pool.ntp.org']
