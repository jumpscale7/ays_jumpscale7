from JumpScale import j

machines = [
            {'ip': '192.168.0.165',
            'port': 22,
            'name': 'sonyLaptop',
            'login': 'root',
            'password': 'kds007kds'
            },
        ]

def installNodes(install=False):
    nodes = {}

    data = {}
    data['instance.key.priv'] = ""
    keyInstance = j.atyourservice.new(name='sshkey', instance="laptopSony", args=data)
    keyInstance.init()
    keyInstance.install()

    for machine in machines:
        data = {}
        data["instance.ip"] = machine['ip']
        data["instance.ssh.port"] = machine['port']
        data['instance.sshkey'] = keyInstance.instance
        data['instance.login'] = machine['login']
        data['instance.password'] = machine['password']
        node = j.atyourservice.new(name='node.ssh', args=data, instance=machine['name'])
        node.init()
        if install:
            node.install()
        nodes[machine['name']] = node

    return nodes

def installKVM(nodes):
    for node in nodes:
        kvm = j.atyourservice.new(name='kvm', instance=node.instance, parent=node)
        kvm.consume('node', kvm.instance)
        kvm.install()

if __name__ == '__main__':
    from JumpScale.baselib import cmdutils
    parser = cmdutils.ArgumentParser()
    commands = ['install', 'list', 'kvm']
    parser.add_argument("action", choices=commands, help='Command to perform\n')
    args = parser.parse_args()

    if args.action == "install":
        installNodes(True)

    if args.action == "list":
        nodes = installNodes(False)
        for n in nodes.values():
            print n

    if args.action == "kvm":
        nodes = installNodes(False)
        installKVM(nodes.values())