from JumpScale import j

ActionsBase = j.atyourservice.getActionsBaseClass()

CONFIG="""
reporting-disabled = false

[meta]
  dir = "$vardir/influxdb/meta"
  hostname = "localhost"
  bind-address = ":8088"
  retention-autocreate = true
  election-timeout = "1s"
  heartbeat-timeout = "1s"
  leader-lease-timeout = "500ms"
  commit-timeout = "50ms"

[data]
  dir = "$vardir/influxdb/data"
  max-wal-size = 104857600
  wal-flush-interval = "10m0s"
  wal-partition-flush-delay = "2s"
  retention-auto-create = true
  retention-check-enabled = true
  retention-check-period = "10m0s"
  retention-create-period = "45m0s"

[cluster]
  shard-writer-timeout = "5s"

[retention]
  enabled = true
  check-interval = "10m0s"

[shard-precreation]
  enabled = true
  check-interval = "10m0s"
  advance-period = "30m0s"

[admin]
  enabled = true
  bind-address = ":8083"

[http]
  enabled = true
  bind-address = ":8086"
  auth-enabled = false
  log-enabled = true
  write-tracing = false
  pprof-enabled = false

[[graphite]]
  bind-address = ":2003"
  database = "graphite"
  enabled = false
  protocol = "tcp"
  batch-size = 0
  batch-timeout = "0"
  consistency-level = "one"
  separator = "."

[collectd]
  enabled = false
  bind-address = ":25826"
  database = "collectd"
  retention-policy = ""
  batch-size = 5000
  batch-timeout = "10s"
  typesdb = "$vardir/influxdb/types.db"

[opentsdb]
  enabled = false
  bind-address = ":4242"
  database = "opentsdb"
  retention-policy = ""
  consistency-level = "one"

[udp]
  enabled = false
  bind-address = ""
  database = ""
  batch-size = 0
  batch-timeout = "0"

[monitoring]
  enabled = false
  write-interval = "1m0s"

[continuous_queries]
  enabled = true
  recompute-previous-n = 2
  recompute-no-older-than = "10m0s"
  compute-runs-per-interval = 10
  compute-no-more-than = "2m0s"

[hinted-handoff]
  enabled = false
  dir = "$vardir/influxdb/hh"
  max-size = 1073741824
  max-age = "168h0m0s"
  retry-rate-limit = 0
  retry-interval = "1s"

"""
class Actions(ActionsBase):

    def prepare(self,serviceObj):
        """
        this gets executed before the files are downloaded & installed on approprate spots
        """



        if j.do.TYPE.lower().startswith("osx"):
            res=j.do.execute("brew install influxdb")
            res=j.do.execute("brew list influxdb")
            for line in res[1].split("\n"):
                if line.strip()=="":
                    continue
                if j.do.exists(line.strip()) and line.find("bin/")!=-1:
                    destpart=line.split("bin/")[-1]
                    dest="/opt/influxdb/%s"%destpart
                    j.system.fs.createDir(j.system.fs.getDirName(dest))
                    j.do.copyFile(line,dest)
                    j.do.chmod(dest, 0o770) 

        if j.do.TYPE.lower().startswith("ubuntu64"):
            j.system.platform.ubuntu.downloadInstallDebPkg("https://s3.amazonaws.com/influxdb/influxdb_0.9.2-rc1_amd64.deb")
            for path in j.system.platform.ubuntu.listFilesPkg("influxdb",regex=".*\/versions\/.*\/infl.*"):
                #find the files which have been installed
                from IPython import embed
                print "DEBUG NOW id"
                embed()
                p
                
            

        return True

    def configure(self, service):
        cfg = j.dirs.replaceTxtDirVars(CONFIG, additionalArgs={})
        j.system.fs.writeFile(fname, cfg)

    def build(self,serviceObj):

        #to reset the state use jpackage reset -n ...

        j.system.platform.ubuntu.check()
        #@todo