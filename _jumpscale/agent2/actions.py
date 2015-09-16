import contoml

from JumpScale import j

ActionsBase = j.atyourservice.getActionsBaseClass()


class Actions(ActionsBase):
    def build(self, service_obj):
        raise Exception('Please use the jenkins build on ci.codescalers.com')

    def configure(self, service_obj):
        agentcontroller = service_obj.hrd.get('instance.agentcontroller')
        cfg_path = j.system.fs.joinPaths(j.dirs.baseDir, 'apps/agent2/agent2.toml')
        cfg = contoml.load(cfg_path)
        cfg['controllers']['main']['url'] = agentcontroller
        cfg['main']['gid'] = int(service_obj.hrd.get('instance.gid'))
        cfg['main']['nid'] = int(service_obj.hrd.get('instance.nid'))

        cfg.dump(cfg_path)
