from JumpScale import j
ActionsBase = j.atyourservice.getActionsBaseClass()


class Actions(ActionsBase):

    def configure(self, serviceObj):
        """
        will install create a docker container
        """

        def createContainer():
            j.tools.docker.create(name="$(instance.param.name)",
                                  base="$(instance.param.image)",
                                  ports="$(instance.param.portsforwards)",
                                  vols="$(instance.param.volumes)")

        j.actions.start(name="create container",
                        description='create a docker container',
                        action=createContainer,
                        stdOutput=True,
                        serviceObj=serviceObj)

        def installJumpscale():
            self.execute(self, "curl https://raw.githubusercontent.com/jumpscale7\
                                /jumpscale_core7/master/install/install_python_web.sh\
                                >/tmp/js7.sh && bash /tmp/js7.sh")

        if serviceObj.hrd.getBool('instance.jumpscale', False):
            j.actions.start(name="install jumpscale",
                            description='install Jumpscale',
                            action=installJumpscale,
                            stdOutput=True,
                            serviceObj=serviceObj)

        def updateHRD():
            import time
            # container need to run to get info
            j.tools.docker.restart('$(instance.param.name)')

            # wait for the container to restart
            cl = j.tools.docker.getSSH('$(instance.param.name)')
            user = cl.user()
            keyloc = "/root/.ssh/id_dsa"
            if user != 'root':
                keyloc = '/home/%s/.ssh/id_dsa' % user
            cl.fabric.api.env['key_filename'] = keyloc
            attempt = 0
            while attempt < 5:
                try:
                    cl.run('ls')  # force connection
                    break
                except:
                    attempt += 1
                    time.sleep(1)

            _, ip = j.system.net.getDefaultIPConfig()
            port = j.tools.docker.getPubPortForInternalPort('$(instance.param.name)', 22)
            passwd = self.generatePassword()
            cl.run('echo -e "%s\n%s" | passwd %s' % (passwd, passwd, user))

            serviceObj.hrd.set('instance.ip', ip)
            serviceObj.hrd.set('instance.ssh.port', port)
            serviceObj.hrd.set('instance.login', user)
            serviceObj.hrd.set('instance.password', passwd)
            serviceObj.hrd.save()
        j.actions.start(name="update HRD",
                        description='update HRD with new values',
                        action=updateHRD,
                        stdOutput=True,
                        serviceObj=serviceObj)

    def start(self, servicesObj):
        j.tools.docker.restart('$(instance.param.name)')

    def stop(self, servicesObj):
        j.tools.docker.stop('$(instance.param.name)')

    def generatePassword(self):
        import os, random, string
        length = 25
        chars = string.ascii_letters + string.digits
        random.seed = (os.urandom(1024))
        return ''.join(random.choice(chars) for i in range(length))

    # def execute(self,serviceObj,cmd):
    #     cl = self._getSSHClient(serviceObj)
    #     cl.sudo(cmd)

    # def upload(self, serviceObj,source,dest):
    #     sshkey = self._getSSHKey(serviceObj)

    #     ip = serviceObj.hrd.get("instance.ip")
    #     port = serviceObj.hrd.get("instance.ssh.port")
    #     rdest = "%s:%s" % (ip,dest)
    #     login = serviceObj.hrd.get('instance.login', default='') or None
    #     if login:
    #         cl = self._getSSHClient(serviceObj)
    #         chowndir = dest
    #         while not cl.file_exists(chowndir):
    #             chowndir = j.system.fs.getParent(chowndir)
    #         cl.sudo("chown -R %s %s" % (login, chowndir))
    #     self._rsync(source,rdest,sshkey,port, login)

    # def download(self, serviceObj,source,dest):
    #     sshkey = self._getSSHKey(serviceObj)

    #     ip = serviceObj.hrd.get("instance.ip")
    #     port = serviceObj.hrd.get("instance.ssh.port")
    #     rsource = "%s:%s" % (ip,source)
    #     login = serviceObj.hrd.get('instance.login', default='') or None
    #     if login:
    #         cl = self._getSSHClient(serviceObj)
    #         chowndir = rsource
    #         while not cl.file_exists(chowndir):
    #             chowndir = j.system.fs.getParent(chowndir)
    #         cl.sudo("chown -R %s %s" % (login, chowndir))
    #     self._rsync(rsource, dest, sshkey, port)

    # def _getSSHClient(self,serviceObj):
    #     c = j.remote.cuisine

    #     ip = serviceObj.hrd.get('instance.ip')
    #     port = serviceObj.hrd.get('instance.ssh.port')
    #     login = serviceObj.hrd.get('instance.login', default='')
    #     password = serviceObj.hrd.get('instance.password', default='')
    #     key = self._getSSHKey(serviceObj)
    #     if key:
    #         c.fabric.env["key"] = key

    #     if password == "" and key == None:
    #         raise RuntimeError("can't connect to the node, should provide or password or a key to connect")
    #     connection = c.connect(ip, port, passwd=password)
    #     if login != '':
    #         connection.fabric.api.env['user'] = login
    #     return connection

    # def _getSSHKey(self,serviceObj):
    #     return serviceObj.hrd.get("instance.sshkey")

    # def _rsync(self, source, dest, key, port=22, login=None):
    #     """
    #     helper method that can be used by services implementation for upload/download actions
    #     """
    #     def generateUniq(name):
    #         import time
    #         epoch = int(time.time())
    #         return "%s__%s" % (epoch,name)

    #     print("copy %s %s" % (source,dest))
    #     # if not j.do.exists(source):
    #         # raise RuntimeError("copytree:Cannot find source:%s"%source)

    #     if dest.find(":") != -1:
    #         # it's an upload
    #         if j.do.isDir(source):
    #             if dest[-1]!="/":
    #                 dest+="/"
    #             if source[-1]!="/":
    #                 source+="/"
    #     if source.find(":") != -1:
    #         # it's a download
    #         if j.do.isDir(dest):
    #             if dest[-1]!="/":
    #                 dest+="/"
    #             if source[-1]!="/":
    #                 source+="/"

    #     keyloc = "/tmp/%s" % generateUniq('id_dsa')
    #     j.system.fs.writeFile(keyloc, key)
    #     j.system.fs.chmod(keyloc, 0o600)
    #     login = login or 'root'
    #     ssh = "-e 'ssh -o StrictHostKeyChecking=no -i %s -p %s -l %s'" % (keyloc, port, login)

    #     destPath = dest
    #     if dest.find(":") != -1:
    #         destPath = dest.split(':')[1]

    #     verbose = "-q"
    #     if j.application.debug:
    #         verbose = "-v"
    #     cmd = "rsync -a --rsync-path=\"mkdir -p %s && rsync\" %s %s %s %s" % (destPath, verbose, ssh, source, dest)
    #     print cmd
    #     j.do.execute(cmd)
    #     j.system.fs.remove(keyloc)
