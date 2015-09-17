from JumpScale import j

ActionsBase = j.atyourservice.getActionsBaseClass()


class Actions(ActionsBase):

    def configure(self, serviceObj):
        def askNodeInfo(node):
            nodeinfo = {}
            nodeinfo['name'] = j.console.askString("Enter node name", node)
            nodeinfo['ip'] = j.console.askString("Enter node IP")
            nodeinfo['client_port'] = j.console.askInteger("Enter node client port", 7080)
            nodeinfo['messaging_port'] = j.console.askInteger("Enter messaging port", 10000)
            nodeinfo['home'] = j.console.askString("Enter node home dir", "/opt/arakoon/data/")
            return nodeinfo

        nodes = serviceObj.hrd.getList('instance.cluster')
        for node in nodes:
            if not serviceObj.hrd.exists('instance.%s' % node):
                info = askNodeInfo(node)
                serviceObj.hrd.set('instance.%s' % node, info)