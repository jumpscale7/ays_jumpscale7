from JumpScale import j

ActionsBase=j.atyourservice.getActionsBaseClass()

class Actions(ActionsBase):


    def prepare(self,serviceObj):
        """
        this gets executed before the files are downloaded & installed on approprate spots
        """
        import JumpScale.baselib.redis
        j.clients.redis.deleteInstance(serviceObj.instance)

        if j.do.TYPE.lower().startswith("osx"):
            j.do.execute("brew install redis")
            res=j.do.execute("brew list redis")
            for line in res[1].split("\n"):
                if line.strip()=="":
                    continue
                if j.do.exists(line.strip()) and line.find("bin/")!=-1:
                    destpart=line.split("bin/")[-1]
                    dest="$(system.paths.base)/apps/redis/%s"%destpart
                    j.system.fs.createDir(j.system.fs.getDirName(dest))
                    j.do.copyFile(line,dest)
                    j.do.chmod(dest, 0o770)      

        return True
        
    def configure(self,serviceObj):
        """
        this gets executed when files are installed
        this step is used to do configuration steps to the platform
        after this step the system will try to start the ays if anything needs to be started
        """
        import JumpScale.baselib.redis
        appendonly=False
        if "$(instance.param.disk)".lower().strip()=="true" or "$(instance.param.disk)".strip()=="1":
            appendonly=True
        passwd = "$(instance.param.passwd)".strip() or None
        j.clients.redis.configureInstance(serviceObj.instance,ip="$(instance.param.ip)",port="$(instance.param.port)",maxram="$(instance.param.mem)",appendonly=appendonly, passwd=passwd, unixsocket="$(instance.param.unixsocket)")
        return True
