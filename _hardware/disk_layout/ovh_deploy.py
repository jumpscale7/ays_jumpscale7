from JumpScale import j

machines = [
            {'ip': '94.23.35.227',
            'port': 22,
            'name': 'ovh3',
            'login': 'root',
            'password': 'rooter'
            },
            {'ip': '94.23.38.89',
            'port': 22,
            'name': 'ovh4',
            'login': 'root',
            'password': 'rooter'
            }
        ]

def installNodes(install=False):
    nodes = {}

    location = "OVH"
    data = {}
    data["instance.name"] = location
    data["instance.description"] = 'OVH'
    location = j.atyourservice.new(name="location", instance=location.lower(), args=data)
    location.init()


    data = {}
    data['instance.key.priv'] = """-----BEGIN DSA PRIVATE KEY-----
    MIIBvAIBAAKBgQDKHJxOO1gEI/O17fACIjneNs/s80/UShBRtilqwZmprs0nUFjY+yNCsHPiN8WQBLDMuCnZfTGE7LvEgPYKIfrfoeiy0tCm0GjWgT9jlRqjC6Lsp59vr8OOh8bY1kZEeJ4Mb6swxlgb653IG4QyvOfVA2cYKB35pygIwtzcyWavjQIVAMAide9GZqde5j+3l23Q/eiA55W/AoGBAMY63nu5JhM7llXyXmb08Ka9oY0PO/ryZW7Y9Q5io9y1JC7GeATl/tUfq5diSeYukBvQrZagzuoVfuNeg+o3QaJ+5AMXZpK0iQwAxyDPgvrif9eGgagk7/eo9hqJSJE0LOB9NzojozstUsetjiYtkFYtvmidpDz8w8hirYAQkRBfAoGACddG65Ft11tBO9FV4aTOwWtHjxVU9kafcdJTEAlWOdR6/D1GSz1koL+OcfjIXfpUqlzNZVCbF0UukhGupz/ocFohmicGL+iP+cRGOrCFjmfNQNhzqHDIksgkI67MEdM2IvbHfLfvcLyDkg5HW+wBYnygnVJdSpz6YhaFKMRpF7ECFQCuYOzEBx9hdLUgRaYbKUedrjeXIQ==
    -----END DSA PRIVATE KEY-----"""
    keyInstance = j.atyourservice.new(name='sshkey', instance="ovh", args=data, parent=location)
    keyInstance.init()
    keyInstance.install()

    for machine in machines:
        data = {}
        data["instance.ip"] = machine['ip']
        data["instance.ssh.port"] = machine['port']
        data['instance.sshkey'] = keyInstance.instance
        data['instance.login'] = machine['login']
        data['instance.password'] = machine['password']
        node = j.atyourservice.new(name='node.ssh', args=data, instance=machine['name'], parent=location)
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

def layoutDisk(nodes):
    for node in nodes:
        dl = j.atyourservice.new(name='layoutdisk', instance=node.instance, parent=node)
        dl.consume('node', node.instance)
        dl.init()

if __name__ == '__main__':
    from JumpScale.baselib import cmdutils
    parser = cmdutils.ArgumentParser()
    commands = ['install', 'list', 'kvm', 'layout']
    parser.add_argument("action", choices=commands, help='Command to perform\n')
    args = parser.parse_args()

    if args.action == "install":
        installNodes(True)

    if args.action == "list":
        nodes = installNodes(False)
        for n in nodes.values():
            print n

    if args.action == "layout":
        nodes = installNodes(False)
        layoutDisk(nodes.values())

    if args.action == "layout":
        nodes = installNodes(False)
        installKVM(nodes.values())