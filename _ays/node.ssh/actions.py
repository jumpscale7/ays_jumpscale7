from JumpScale import j
ActionsBase=j.atyourservice.getActionsBaseClass()


import JumpScale.baselib.remote.cuisine

class Actions(ActionsBase):

    def configure(self,serviceObj):
        """
        will install a node over ssh
        """

        cl = self._getSSHClient(serviceObj)
        def pushkey():
            """
            will install the key on the node if not already present
            """
            priv,pub = self._getSSHKey(serviceObj)
            if priv and pub:
                try:
                    cl.run('')  # force connection
                    result = cl.run('cat ~/.ssh/authorized_keys | grep "%s" '%pub)
                except:
                    result = ""
                if result == "":
                    # the key is not present yet, push it
                    cl.run('mkdir -p ~/.ssh')
                    cl.run("echo '%s' >> ~/.ssh/authorized_keys" % pub)

        j.actions.start(name="pushkey",description='pushkey', action=pushkey, stdOutput=True, serviceObj=serviceObj)


        def update():
            cl.sudo("apt-get update")
            # j.do.execute("apt-get update")
        j.actions.start(name="update",description='update', action=update, stdOutput=True, serviceObj=serviceObj)

        def upgrade():
            cl.sudo("apt-get upgrade -y")
            # j.do.execute("apt-get upgrade -y")
        j.actions.start( name="upgrade",description='upgrade', action=upgrade, stdOutput=True, serviceObj=serviceObj)
        def extra():
            cl.sudo("apt-get install byobu curl -y")
            # j.do.execute("apt-get install byobu curl -y")
        j.actions.start(name="extra",description='extra', action=extra, stdOutput=True, serviceObj=serviceObj)

        def jumpscale():
            cl.sudo("curl https://raw.githubusercontent.com/Jumpscale/jumpscale_core7/master/install/install_python_web.sh > /tmp/installjs.sh")
            cl.sudo("sh /tmp/installjs.sh")
            # j.do.execute("curl https://raw.githubusercontent.com/Jumpscale/jumpscale_core7/master/install/install_python_web.sh > /tmp/installjs.sh")
            # j.do.execute("sh /tmp/installjs.sh")
        j.actions.start(name="jumpscale",description='install jumpscale', action=jumpscale, stdOutput=True, serviceObj=serviceObj)

        return True


    def removedata(self,serviceObj):
        """
        delete vmachine
        """
        self.execute(serviceObj, "killall tmux;killall python;echo")
        # j.do.execute("rm -rf /opt")
        return True

    def execute(self,serviceObj,cmd):
        cl = self._getSSHClient(serviceObj)
        cl.sudo(cmd)


    def upload(self, serviceObj,source,dest):
        sshkey,_ = self._getSSHKey(serviceObj)

        ip = serviceObj.hrd.get("instance.ip")
        port = serviceObj.hrd.get("instance.ssh.port")
        rdest = "%s:%s" % (ip,dest)
        login = serviceObj.hrd.get('instance.login', default='') or None
        if login:
            cl = self._getSSHClient(serviceObj)
            chowndir = dest
            while not cl.file_exists(chowndir):
                chowndir = j.system.fs.getParent(chowndir)
            cl.sudo("chown -R %s %s" % (login, chowndir))
        self._rsync(source,rdest,sshkey,port, login)

    def download(self, serviceObj,source,dest):
        sshkey,_ = self._getSSHKey(serviceObj)

        ip = serviceObj.hrd.get("instance.ip")
        port = serviceObj.hrd.get("instance.ssh.port")
        source = "%s:%s" % (ip,source)
        self._rsync(source,dest,sshkey,port)

    def _getSSHKey(self,serviceObj):
        keyname = serviceObj.hrd.get("instance.sshkey")
        if keyname != "":
            sshkeyHRD = j.application.getAppInstanceHRD("sshkey",keyname)
            return (sshkeyHRD.get("instance.key.priv"),sshkeyHRD.get("instance.key.pub"))
        else:
            return (None,None)

    def _getSSHClient(self,serviceObj):
        c = j.remote.cuisine

        ip = serviceObj.hrd.get('instance.ip')
        port = serviceObj.hrd.get('instance.ssh.port')
        login = serviceObj.hrd.get('instance.login', default='')
        password = serviceObj.hrd.get('instance.password', default='')
        priv,_ = self._getSSHKey(serviceObj)
        if priv:
            c.fabric.env["key"] = priv

        if password == "" and priv == None:
            raise RuntimeError("can't connect to the node, should provide or password or a key to connect")
        connection = c.connect(ip, port, passwd=password)
        if login != '':
            connection.fabric.api.env['user'] = login
        return connection
