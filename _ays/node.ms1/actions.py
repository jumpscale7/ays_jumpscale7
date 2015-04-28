from JumpScale import j

ActionsBase=j.atyourservice.getActionsBaseClass()

import JumpScale.lib.ms1
import JumpScale.baselib.remote.cuisine

class Actions(ActionsBase):

    def configure(self,serviceobj):
        """
        will install a node
        """

        ms1client_hrd=j.application.getAppInstanceHRD("ms1_client","$(instance.param.ms1.connection)")

        spacesecret=ms1client_hrd.get("instance.param.secret")

        def createmachine():

            machineid,ip,port=j.tools.ms1.createMachine(spacesecret, "$(instance.param.name)", memsize="$(instance.param.memsize)", \
                ssdsize=$(instance.param.ssdsize), vsansize=0, description='',imagename="$(instance.param.imagename)",delete=False)

            serviceobj.hrd.set("instance.param.machine.id",machineid)
            serviceobj.hrd.set("instance.param.machine.ssh.ip",ip)
            serviceobj.hrd.set("instance.param.machine.ssh.port",port)


        j.actions.start(retry=1, name="createmachine",description='createmachine', cmds='', action=createmachine, \
            actionRecover=None, actionArgs={}, errorMessage='', die=True, stdOutput=True, serviceObj=serviceobj)


        def update():
            serviceobj.args['cmd'] = "apt-get update"
            self.execute()
        j.actions.start(retry=1, name="update",description='update', action=update, stdOutput=True, serviceObj=serviceobj)

        def upgrade():
            serviceobj.args['cmd'] = "apt-get upgrade -y"
            self.execute()
        j.actions.start(retry=1, name="upgrade",description='upgrade', action=upgrade, stdOutput=True, serviceObj=serviceobj)

        def jumpscale():
            serviceobj.args['cmd'] = "curl https://raw.githubusercontent.com/Jumpscale/jumpscale_core7/master/install/install_python_web.sh > /tmp/installjs.sh; sh /tmp/installjs.sh"
            self.execute(cmd="")
        j.actions.start(retry=1, name="jumpscale",description='install jumpscale', action=jumpscale, stdOutput=True, serviceObj=serviceobj)

        return True


    def removedata(self,serviceobj):
        """
        delete vmachine
        """
        ms1client_hrd=j.application.getAppInstanceHRD("ms1_client","$(instance.param.ms1.connection)")
        spacesecret=ms1client_hrd.get("instance.param.secret")
        j.tools.ms1.deleteMachine(spacesecret, "$(instance.param.name)")

        return True

    def execute(self,serviceobj):
        """
        execute over ssh something onto the machine
        """

        if "cmd" not in serviceObj.args:
            raise RuntimeError("cmd need to be in args, example usage:jpackage execute -n node.ssh.key -i ovh5 --data=\"cmd:'ls /'\"")

        cl = j.packages.remote.sshPython(serviceObj=serviceObj,node=serviceObj.instance)
        cmd = serviceobj.args['cmd']
        cl.connection.run(cmd)

        return True
