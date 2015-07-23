from JumpScale import j

ActionsBase = j.atyourservice.getActionsBaseClass()


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
            cmd='mkdir -p /opt/influxdb/cfg;curl -k https://git.aydo.com/binary/influxdb/raw/master/cfg/influxdb/influxdb.conf > /opt/influxdb/cfg/influxdb.conf'
            j.do.execute(cmd)
        return True

    def configure(self, service):
        if j.do.TYPE.lower().startswith("osx"):
            fname = '$(service.param.base)/cfg/influxdb.conf'
        else:
            fname = '$(service.param.base)/cfg/config.toml'

        cfg = j.system.fs.fileGetContents(fname)

        cfg = j.dirs.replaceTxtDirVars(cfg, additionalArgs={})
        j.system.fs.writeFile(fname, cfg)

    def build(self,serviceObj):

        #to reset the state use jpackage reset -n ...

        j.system.platform.ubuntu.check()
        #@todo