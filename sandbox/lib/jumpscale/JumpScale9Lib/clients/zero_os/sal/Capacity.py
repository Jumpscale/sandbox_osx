import re as _re
import io
import json

_handle_re = _re.compile("^Handle\\s+(.+),\\s+DMI\\s+type\\s+(\\d+),\\s+(\\d+)\\s+bytes$")
_in_block_re = _re.compile("^\\t\\t(.+)$")
_record_re = _re.compile("\\t(.+):\\s+(.+)$")
_record2_re = _re.compile("\\t(.+):$")

GIB = 1024 * 1024 * 1024
GB = 1000 * 1000 * 1000


class Capacity:

    def __init__(self, node):
        self._node = node
        self._hw_info = None
        self._disk_info = None

    @property
    def hw_info(self):
        if self._hw_info is None:
            out = io.StringIO()

            def cb(level, msg, flag):
                out.write(msg)
                out.write('\n')
            self._node.client.system('dmidecode', stream=True).stream(cb)
            self._hw_info = _parse_dmi(out.getvalue())
        return self._hw_info

    @property
    def disk_info(self):
        if self._disk_info is None:
            self._disk_info = {}
            for disk in self._node.disks.list():
                out = io.StringIO()

                def cb(level, msg, flag):
                    out.write(msg)
                    out.write('\n')
                self._node.client.system('smartctl -i %s' % disk.devicename, stream=True).stream(cb)
                self._disk_info[disk.devicename] = _parse_smarctl(out.getvalue())
                self._disk_info[disk.devicename]['size'] = disk.size
                self._disk_info[disk.devicename]['type'] = disk.type.name
        return self._disk_info

    def report(self):
        """
        create a report of the hardware capacity for
        processor, memory, motherboard and disks
        """
        return Report(self._node, self.hw_info, self.disk_info)


class Report:

    def __init__(self, node, hw_info, disk_info):
        self._node = node
        self.processor = _cpu_info(hw_info)
        self.memory = _memory_info(hw_info)
        self.motherboard = _mobo_info(hw_info)
        self.disk = _disks_info(disk_info)

    @property
    def CRU(self):
        """
        return the number of core units
        """
        unit = 0
        for cpu in self.processor:
            unit += int(cpu.get('thread_nr', 0))
        return unit

    @property
    def MRU(self):
        """
        return the number of memory units in GB
        """
        size = (self._node.client.info.mem()['total'] / GIB)
        return round(size, 2)

    @property
    def HRU(self):
        """
        return the number of hd units in GB
        """
        unit = 0
        for disk in self.disk:
            if disk['type'] in ['hdd', 'archive']:
                unit += disk['size'] / GIB
        return round(unit, 2)

    @property
    def SRU(self):
        """
        return the number of ssd units in GB
        """
        unit = 0
        for disk in self.disk:
            if disk['type'] in ['ssd', 'nvme']:
                unit += disk['size'] / GIB
        return round(unit, 2)

    def __repr__(self):
        return json.dumps({
            "processor": self.processor,
            "memory": self.memory,
            "motherboard": self.motherboard,
            "disk": self.disk,
        })

    def __str__(self):
        return repr(self)


def _cpu_info(data):
    result = []
    for entry in data.values():
        if entry['DMIType'] == 4:
            info = {
                'speed': entry.get('Current Speed'),
                'core_nr': entry.get('Core Enabled'),
                'thread_nr': entry.get('Thread Count'),
                'serial': entry.get('Serial Number'),
                'manufacturer': entry.get('Manufacturer'),
                'version': entry.get('Version'),
                'id': entry.get('ID')
            }
            result.append(info)
    return result


def _memory_info(data):
    result = []
    for entry in data.values():
        if entry['DMIType'] == 17:
            info = {
                'speed': entry.get('Speed'),
                'size': entry.get('Size'),
                'width': entry.get('Total Width'),
                'serial': entry.get('Serial Number'),
                'manufacturer': entry.get('Manufacturer'),
                'asset_tag': entry.get('Asset Tag'),
            }
            result.append(info)
    return result


def _mobo_info(data):
    result = []
    for entry in data.values():
        if entry['DMIType'] == 2:
            info = {
                'name': entry.get('Produce Name'),
                'version': entry.get('Version'),
                'serial': entry.get('Serial Number'),
                'manufacturer': entry.get('Manufacturer'),
                'asset_tag': entry.get('Asset Tag'),
            }
            result.append(info)
    return result


def _disks_info(data):
    result = []
    for device_name, entry in data.items():
        info = {
            'name': device_name,
            'model': entry.get("Device Model"),
            'firmware_version': entry.get("Firmware Version"),
            'form_factor': entry.get('Firmware Version'),
            'device_id': entry.get('LU WWN Device Id'),
            'rotation_state': entry.get('Rotation Rate'),
            'serial': entry.get('Serial Number'),
            'user_capacity': entry.get('User Capacity'),
            'sector_size': entry.get('Sector Sizes'),
            'size': entry.get('size'),
            'type': entry.get('type'),
        }
        result.append(info)
    return result


def _parse_smarctl(buffer):
    result = {}
    for line in buffer.splitlines()[4:]:
        if not line:
            continue
        ss = line.split(":", 1)
        if len(ss) != 2:
            continue
        result[ss[0].strip()] = ss[1].strip()
    return result


def _parse_dmi(buffer):
    output_data = {}
    #  Each record is separated by double newlines
    split_output = buffer.split('\n\n')

    for record in split_output:
        record_element = record.splitlines()

        #  Entries with less than 3 lines are incomplete / inactive; skip them
        if len(record_element) < 3:
            continue

        handle_data = _handle_re.findall(record_element[0])

        if not handle_data:
            continue
        handle_data = handle_data[0]

        dmi_handle = handle_data[0]

        output_data[dmi_handle] = {}
        output_data[dmi_handle]["DMIType"] = int(handle_data[1])
        output_data[dmi_handle]["DMISize"] = int(handle_data[2])

        #  Okay, we know 2nd line == name
        output_data[dmi_handle]["DMIName"] = record_element[1]

        in_block_elemet = ""
        in_block_list = ""

        #  Loop over the rest of the record, gathering values
        for i in range(2, len(record_element), 1):
            if i >= len(record_element):
                break
            #  Check whether we are inside a \t\t block
            if in_block_elemet != "":

                in_block_data = _in_block_re.findall(record_element[1])

                if in_block_data:
                    if not in_block_list:
                        in_block_list = in_block_data[0][0]
                    else:
                        in_block_list = in_block_list + "\t\t" + in_block_data[0][1]

                    output_data[dmi_handle][in_block_elemet] = in_block_list
                    continue
                else:
                    # We are out of the \t\t block; reset it again, and let
                    # the parsing continue
                    in_block_elemet = ""

            record_data = _record_re.findall(record_element[i])

            #  Is this the line containing handle identifier, type, size?
            if record_data:
                output_data[dmi_handle][record_data[0][0]] = record_data[0][1]
                continue

            #  Didn't findall regular entry, maybe an array of data?

            record_data2 = _record2_re.findall(record_element[i])

            if record_data2:
                #  This is an array of data - let the loop know we are inside
                #  an array block
                in_block_elemet = record_data2[0][0]
                continue

    if not output_data:
        raise RuntimeError("Unable to parse 'dmidecode' output")

    return output_data
