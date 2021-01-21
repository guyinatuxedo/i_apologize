import paramiko

hostname = ""
port = 22
username = ""
password = ""

modules = [
            [b"vmw_balloon", b"vmw_balloon.ko"], 
            #[b"vmw_vsock_virtio_transport_common", b"vmw_vsock_virtio_transport_common.ko"],
            [b"vmw_vsock_vmci_transport", b"vmw_vsock_vmci_transport.ko"]]

cmds = []

def run_cmd(cmd):
    client = paramiko.Transport((hostname, port))
    client.connect(username=username, password=password)
    s = client.open_channel(kind='session')
    s.exec_command(cmd)
    output = b""
    receiving = False
    c = b""
    while True:
        c = s.recv(1)
        if c == b'':
            if receiving:
                break
            else:
                continue
        output += c
        receiving = True
    return output.strip(b"\n")
        #if s.exit_status_ready():
        #    break

class load_modules(gdb.Command):
    def __init__(self):
        super(load_modules, self).__init__("load_modules", gdb.COMMAND_DATA)

    def invoke(self, arg, from_tty):
        print("And so he spoke")
        for module in modules:
            print(b"\n\nModule: " + module[0] + b"\n\n")
            text = run_cmd(b"cat /sys/module/" + module[0] + b"/sections/.text")
            data = run_cmd(b"cat /sys/module/" + module[0] + b"/sections/.data")
            bss = run_cmd(b"cat /sys/module/" + module[0] + b"/sections/.bss")
            cmd = b"add-symbol-file " + module[1] + b" " + text + b" -s .data " + data + b" -s .bss " + bss
            cmds.append(cmd.decode())

        print("\n\nsetting things\n\n")
        gdb.execute("set architecture i386:x86-64")
        gdb.execute("target remote localhost:8864")

        print("\n\nrunning cms\n\n")
        for exec_cmd in cmds:
            gdb.execute(exec_cmd)


class load_symbols(gdb.Command):
    def __init__(self):
        super(load_symbols, self).__init__("load_symbols", gdb.COMMAND_DATA)

    def invoke(self, arg, from_tty):
        print("just to wake up")
        for cmd in cmds:
            gdb.execute(str(cmd))




load_modules()
load_symbols()
