import salt.client

"""
WARNING - This is only a prototype, not for production use!

Depends on Salt, to install via pip::
 
 pip install salt

In order for pip to complete Salt, we need require the following::

 apt-get install swig python-dev gcc build-essential
"""


def main(data):
    """main plugin entrypoint"""
    checks, function, targets = data.split()
    return REACTIONS[function](targets)


def cmd_run_all(targets, command):
    """DO NOT GIVE USERS DIRECT ACCESS TO THIS FUNCTION"""
    local = salt.client.LocalClient()
    return local.cmd(targets, ["cmd.run_all"], [[command]])


def uptime(targets):
    """Return the uptime for all targets"""
    output = []
    result = cmd_run_all(targets, "uptime")
    
    for minion_id, minion_result in result.items():
        # Check if the result is valid (not False)
        if minion_result and isinstance(minion_result, dict) and "cmd.run_all" in minion_result:
            output.append(f"{minion_id}: {minion_result['cmd.run_all']['stdout']}")
        else:
            output.append(f"{minion_id}: Command failed or minion unreachable")
    
    return "\n".join(output)


def procs(targets):
    """Check procs. Return stdout for targets considered in Warning or Critical"""
    output = []
    result = cmd_run_all(targets, "/usr/lib/nagios/plugins/check_procs -w 150 -c 200")
    
    for minion_id, minion_result in result.items():
        # Check if the result is valid (not False)
        if minion_result and isinstance(minion_result, dict) and "cmd.run_all" in minion_result:
            if minion_result["cmd.run_all"]["retcode"] != 0:
                output.append(f"{minion_id}: {minion_result['cmd.run_all']['stdout']}")
        else:
            output.append(f"{minion_id}: Command failed or minion unreachable")
    
    return "\n".join(output)


def disks(targets):
    """Check disk usage. Return stdout for targets considered in Warning or Critical"""
    output = []
    result = cmd_run_all(
        targets, '/usr/lib/nagios/plugins/check_disk -w 20% -c 10% -A -i ".gvfs"'
    )
    
    for minion_id, minion_result in result.items():
        # Check if the result is valid (not False)
        if minion_result and isinstance(minion_result, dict) and "cmd.run_all" in minion_result:
            if minion_result["cmd.run_all"]["retcode"] != 0:
                output.append(f"{minion_id}: {minion_result['cmd.run_all']['stdout']}")
        else:
            output.append(f"{minion_id}: Command failed or minion unreachable")
    
    return "\n".join(output)


REACTIONS = {
    "uptime": uptime,
    "procs": procs,
    "disks": disks,
}

if __name__ == "__main__":
    # example usage
    print(main("checks uptime *"))
    print(main("checks procs *"))
    print(main("checks disks *"))
