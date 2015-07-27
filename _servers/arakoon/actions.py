from JumpScale import j

ActionsBase = j.atyourservice.getActionsBaseClass()

class Actions(ActionsBase):

    def prepare(self,serviceObj):
        """
        this gets executed before the files are downloaded & installed on approprate spots
        """
        import ipdb; ipdb.set_trace()
        nodes = serviceObj.hrd.getListFromPrefix('instance.nodes')
        settings = serviceObj.hrd.get('instance.cfg')
        nodename = serviceObj.hrd.get('instance.nodename')
        settingsdir = j.system.fs.getDirName(settings)
        j.system.fs.createDir(settingsdir)
        def askNodeInfo():
            nodeinfo = {}
            nodeinfo['name'] = j.console.askString("Enter node name", "node1")
            nodeinfo['ip'] = j.console.askString("Enter node IP")
            nodeinfo['client_port'] = j.console.askInteger("Enter node client port", 7080)
            nodeinfo['messaging_port'] = j.console.askInteger("Enter node client port", 10000)
            nodeinfo['home'] = j.console.askString("Enter node home dir", "/opt/arakoon/data/")
            if nodeinfo['name'] == nodename:
                j.system.fs.createDir(nodeinfo['home'])
            return nodeinfo

        if not nodes and not j.system.fs.exists(settings):
            clusterid = j.console.askString('Enter cluster id', 'grid')
            while True:
                nodes.append(askNodeInfo())
                if not j.console.askYesNo("Add another node"):
                    break
            config = j.tools.inifile.open(settings)
            config.addSection('global')
            config.addParam('global', 'cluster_id', clusterid)
            config.addParam('global', 'cluster', ', '. join(node['name'] for node in nodes))
            config.addSection('default_log_config')
            config.addParam('default_log_config', 'client_protocol', 'info')
            config.addParam('default_log_config', 'paxos', 'info')
            config.addParam('default_log_config', 'tcp_messaging', 'info')
            for node in nodes:
                config.addSection(node['name'])
                for key, value in node.iteritems():
                    if key == 'name':
                        continue
                    config.addParam(node['name'], key, value)
                config.addParam(node['name'], 'log_dir', node['home'])
                config.addParam(node['name'], 'log_level', 'info')
                config.addParam(node['name'], 'log_config', 'default_log_config')
            config.write()


        if j.do.TYPE.lower().startswith("ubuntu64"):
            j.system.platform.ubuntu.downloadInstallDebPkg("http://apt-ovs.cloudfounders.com/alpha/arakoon_1.8.6_amd64.deb",minspeed=50)


        return True

