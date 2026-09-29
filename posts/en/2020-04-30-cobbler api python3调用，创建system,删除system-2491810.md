---
title: "Calling the Cobbler API with Python 3 to Create and Delete Systems"
date: "2020-04-30 14:32:11"
category: "python"
source: "https://blog.51cto.com/hequan/2491810"
lang: "en"
---
> **About this post**
>
> Automate creating, configuring, and deleting provisioned systems via Cobbler's XML-RPC API with Python 3: specify the MAC address, IP, gateway, and subnet mask, bind a profile, and finally trigger `sync` to apply the changes. The comments also collect many commonly used query and maintenance interfaces, making this a handy reference for Cobbler ops scripts.

> **Technical notes**
>
> The examples were written against the Cobbler 2.x XML-RPC interface on CentOS 7; starting with Cobbler 3.x, the configuration directories, CLI, and some API behaviors have changed, so verify version compatibility before using this in production.

---

### Calling the Cobbler API with Python 3 to Create and Delete Systems

> You can call the API with a MAC address to create an install task, and delete the task once the installation is done.

```python
#!/usr/bin/python3.6

import xmlrpc.client

server = 'http://192.168.100.52/cobbler_api'
user = 'admin'
password = '123456'

if __name__ == '__main__':

    try:
        remote_server = xmlrpc.client.Server(server)
        token = remote_server.login(user, password)

        print(remote_server.ping())  # check cobbler server status

        print(remote_server.find_distro())
        print(remote_server.find_system())

        # create
        system_id = remote_server.new_system(token)
        remote_server.modify_system(system_id, "name", "web1", token)
        remote_server.modify_system(system_id, "hostname", "web1", token)
        remote_server.modify_system(system_id, 'modify_interface', {
            "macaddress-eth0": "00:0C:29:e1:8a:5b",
            "ipaddress-eth0": "192.168.100.150",
            "Gateway-eth0": "192.168.100.2",
            "subnet-eth0": "255.255.255.0",
            "static-eth0": 1,
            "dnsname-eth0": "192.168.100.2"
        }, token)
        remote_server.modify_system(system_id, "profile", "CentOS-7.4-x86_64", token)
        remote_server.save_system(system_id, token)
        remote_server.sync(token)

        print(remote_server.get_systems())

        ## delete
        remote_server.remove_system("web1", token)
        remote_server.sync(token)
        print(remote_server.find_system())

    except Exception as e:
        exit('URL:%s no access' % server)

    # print(remote_server.get_user_from_token(token))  # returns the cobbler login account
    # print(remote_server.get_item('distro','Centos6.9-x86_64')) # get info of the specified distro
    # print('-------------------------')
    # print(remote_server.get_distro('Centos6.9-x86_64'))  # returns detailed info of the distro with the given name
    # print('-------------------------')
    # print(remote_server.get_profile('CT6.8_PHY_db_high'))  # returns detailed info of the profile with the given name
    # print('-------------------------')
    # print(remote_server.get_distros())   # returns all existing distros
    # print('-------------------------')
    # print(remote_server.get_profiles())  # returns all existing profiles
    # print('-------------------------')
    # print(remote_server.find_system())  # returns all system names as a list
    # print('-------------------------')
    # print(remote_server.find_distro())  # returns all distro names as a list
    # print('-------------------------')
    # print(remote_server.find_profile())  # returns all profile names as a list
    # print('-------------------------')
    # print(remote_server.has_item('distro','Centos6.9-x86_64'))  # checks whether the given name exists in the specified distro
    # print('-------------------------')
    # print(remote_server.get_distro_handle('Centos6.9-x86_64',token))  # not very useful
    # print(remote_server.remove_profile('test111',token))  # removes the specified profile
    # print('-------------------------')
    # print(remote_server.remove_system('hostname121',token)) # removes the specified system
    # print('-------------------------')
    # prof_id = remote_server.new_profile(token)  # create a new profile and save it
    # print('profile new id:%s' % prof_id)
    # print('-------------------------')
    # remote_server.modify_profile(prof_id,'name','vm_test1',token) # modify the name of the profile specified by prof_id
    # remote_server.modify_profile(prof_id,'distro','centos6.8-x86_64',token)  # also modifies the info of prof_id
    # remote_server.modify_profile(prof_id,'kickstart','/var/lib/cobbler/kickstarts/txt111',token)
    # remote_server.save_profile(prof_id,token) # save
    # remote_server.sync(token) # sync the modified info; this is a must after any operation
    # print('-------------------------')
    # print(remote_server.get_kickstart_templates())  # get paths of all kickstart template files
    # print('-------------------------')
    # print(remote_server.get_snippets())  # get paths of all snippet files
    # print('-------------------------')
    # print(remote_server.is_kickstart_in_use('/var/lib/cobbler/kickstarts/CT6.8_PHY_db_middle.ks')) # check whether the ks file is in use
    # print('-------------------------')
    # print(remote_server.generate_kickstart('CT6.8_PHY_web_high')) # print the ks file content for the profile
    # print('-------------------------')
    # print(remote_server.generate_kickstart('vm_test1','t1'))# print the ks file content for the profile
    # print('-------------------------')
    # print(remote_server.generate_gpxe('vm_test1')) # boot related; useless
    # print('-------------------------')
    # print(remote_server.generate_bootcfg('vm_test1'))
    # print('-------------------------')
    # print(remote_server.get_blended_data('vm_test1')) # get detailed info of the profile
    # print('-------------------------')
    # print(remote_server.get_settings())  # not very useful
    # print('-------------------------')
    # print(remote_server.get_signatures())  # no idea what it outputs
    # print('-------------------------')
    # print(remote_server.get_valid_breeds())  # gets the breed (type) of each operating system
    # output: ['debian', 'freebsd', 'generic', 'nexenta', 'redhat', 'suse', 'ubuntu', 'unix', 'vmware', 'windows', 'xen']
    # print('-------------------------')
    # print(remote_server.get_valid_os_versions())  # not very useful
    # print('-------------------------')
    # print(remote_server.get_repo_config_for_profile('vm_test1'))
    # print('-------------------------')
    # print(remote_server.get_repo_config_for_system('t1'))
    # print('-------------------------')
    # print(remote_server.version())  # returns the cobbler version; not very useful
    # print('-------------------------')
    # print(remote_server.extended_version())  # returns detailed cobbler version info; not very useful
    # print('-------------------------')
    # print(remote_server.logout(token))  # log out of the current cobbler connection
    # print('-------------------------')
    # print(remote_server.token_check(token))  # check the current token status and whether it has expired
    # print('-------------------------')
    # print(remote_server.sync_dhcp(token)  # sync DHCP
    # print('-------------------------')
    # print(remote_server.sync(token))  # perform a sync update
    # print('-------------------------')
    # print(remote_server.read_or_write_kickstart_template('ks file path in cobbler','false means writable','content to replace the ks file',token))  # note: if the replacement string is -1, this ks file will be deleted, provided it is no longer referenced
    # print(remote_server.read_or_write_kickstart_template('/var/lib/cobbler/kickstarts/hostname106.ks',False,-1,token))
    # print('-------------------------')
    # print(remote_server.get_config_data('zhaoyong'))  # not very useful
    # print('-------------------------')
    # x  = remote_server.test_xmlrpc_ro()
    # print(x.distro)
    # print(remote_server.read_or_write_snippet('/var/lib/cobbler/snippets/test1',False,'zhaoyong_test',token)) # create a script file under snippets
    # distro_obj = cbl_distro.cobbler_distro(remote_server,token)
    # # distro queries
    # out = distro_obj.find_distro_name()
    # print(out)
    # out = distro_obj.find_distro_info('Centos6.9-x86_64')
    # print(out)
    #
    # profile_obj = cbl_profile.cobbler_profiles(remote_server,token)
    #  profile queries
    # pro_name_list = profile_obj.find_profile_name()
    # print(out)
    # out = profile_obj.find_profile_info('CT6.8_VM_web_custom')
    # print(out)
    #
    # system_obj = cbl_system.cobbler_system(remote_server,token)
    # # system queries
    # out_all = system_obj.find_system_name()
    # print(out_all)
    # out = system_obj.system_name_info('tttttt')
    # print(out)
    # del system
```
