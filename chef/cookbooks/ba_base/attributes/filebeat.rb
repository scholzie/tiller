default[:filebeat][:config][:output][:logstash] = {
  enabled: true,
  hosts: ["ec2-52-32-51-234.us-west-2.compute.amazonaws.com:5044"],
  loadbalance: false,
  certificate_authorities: ["/tmp/logstash-forwarder.crt"],
}
# I overwrite this, needs to be here so cookbook finishes run
default[:filebeat][:prospectors] = { 
  system_logs: {
    filebeat: {
      prospectors: [
        {
          paths: [
            "/var/log/messages",
            "/var/log/syslog"
          ],
          type: "log",
          fields: {
            type: "system_logs"
          }
        }
      ]
    }
  },
  secure_logs: {
    filebeat: {
      prospectors: [
        {
          paths: [
           "/var/log/secure",
           "/var/log/auth.log"
          ],
          type: "log",
          fields: {
            type: "secure_logs"
          }
        }
      ]
    }
  },
  nginx_logs: {
    filebeat: {
      prospectors: {
        paths: [
          "/var/log/nginx/*.log"
        ],
        type: "log",
        fields: {
          type: "nginx_logs"
        }
      }
    } 
  }
}
# doing this as the current cookbook version grabs 1.0.1 which fails to boot
override[:filebeat][:version] = '1.1.1'
