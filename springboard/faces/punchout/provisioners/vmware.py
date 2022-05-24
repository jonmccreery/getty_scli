#!/usr/bin/python


class VmwareHandler(object):
    def __init__(self):
        pass

    def get_vmware_cache(self, session, settings, phoenix_vmware_endpoint):
        headers = {'Content-type': 'application/json'}
        r = session.get(
            settings['phoenix_url'] + phoenix_vmware_endpoint,
            headers=headers
        )
        vmware_data = r.json()

        return vmware_data

    def get_vmware_locations(self, session, settings, phoenix_location_endpoint):
        headers = {'Content-type': 'application/json'}
        r = session.get(
            settings['phoenix_url'] + phoenix_location_endpoint,
            headers=headers
        )
        loc_data = r.json()

        return loc_data

    def check_vmware_vcenter(self, vcenter, vmware_data):
        if vcenter not in vmware_data:
            print('vcenter {} does not exist!').format(vcenter)
            return False
        else:
            return True

    def check_vmware_cluster(self, cluster, vcenter, vmware_data):
        if cluster in vmware_data[vcenter]['clusters']:
            return cluster
        else:
            for i in vmware_data[vcenter]['clusters']:
                if cluster.lower() == i.lower():
                    print("WARN: corrected cluster {} to {}!").format(cluster, i)
                    return i

        return False

    def check_vmware_folder(self, folder, vcenter, vmware_data):
        folder_prefix = folder.split('/')[0]
        if folder_prefix in vmware_data[vcenter]['datacenters']:
            return True
        else:
            return False

    def check_vmware_datastore(self, datastore, vcenter, vmware_data):
        if datastore in vmware_data[vcenter]['datastores']:
            return datastore
        else:
            for i in vmware_data[vcenter]['datastores']:
                if datastore.lower() == i.lower():
                    print("WARN: corrected datastore {} to {}!").format(datastore, i)
                    return i

        return False

    def check_vmware_vlan(self, vlan, vcenter, vmware_data):
        if vlan in vmware_data[vcenter]['networks']:
            return vlan
        else:
            for i in vmware_data[vcenter]['networks']:
                if vlan.lower() == i.lower():
                    print("WARN: corrected vlan {} to {}!").format(vlan, i)
                    return i
