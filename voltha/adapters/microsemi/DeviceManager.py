#
# Copyright 2016 the original author or authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
from uuid import uuid4
from ofagent.utils import mac_str_to_tuple
import structlog
from voltha.protos.common_pb2 import ConnectStatus, OperStatus
from voltha.protos.logical_device_pb2 import LogicalDevice, LogicalPort
from voltha.protos.openflow_13_pb2 import ofp_desc, ofp_switch_features, OFPC_FLOW_STATS, OFPC_TABLE_STATS, \
    OFPC_PORT_STATS, OFPC_GROUP_STATS, ofp_port, OFPPS_LIVE, OFPPF_10GB_FD, OFPPF_FIBER

log = structlog.get_logger()

class DeviceManager(object):

    def __init__(self, device, adapter_agent):
        self.device = device
        self.adapter_agent = adapter_agent
        self.logical_device = None

    def update_device(self, pkt):

        self.device.root = True
        self.device.vendor = 'Celestica Inc.'
        self.device.model = 'Ruby'
        self.device.hardware_version = \
            '{}.{}'.format(hex(pkt.major_hardware_version),
                           pkt.minor_hardware_version)
        self.device.firmware_version = '{}.{}.{}'.format(pkt.major_firmware_version,
                                                         pkt.minor_firmware_version,
                                                         pkt.build_firmware_version)
        self.device.software_version = '0.0.1'
        self.device.serial_number = self.device.mac_address
        self.device.connect_status = ConnectStatus.REACHABLE
        self.adapter_agent.update_device(self.device)

    def create_logical_device(self):
        log.info('create-logical-device')
        # then shortly after we create the logical device with one port
        # that will correspond to the NNI port
        logical_device_id = uuid4().hex[:12]
        ld = LogicalDevice(
            id=logical_device_id,
            datapath_id=int('0x' + logical_device_id[:8], 16), # from id
            desc=ofp_desc(
                mfr_desc=self.device.vendor,
                hw_desc=self.device.hardware_version,
                sw_desc=self.device.firmware_version,
                serial_num=uuid4().hex,
                dp_desc='n/a'
            ),
            switch_features=ofp_switch_features(
                n_buffers=256,  # TODO fake for now
                n_tables=2,  # TODO ditto
                capabilities=(  # TODO and ditto
                    OFPC_FLOW_STATS
                    | OFPC_TABLE_STATS
                    | OFPC_PORT_STATS
                    | OFPC_GROUP_STATS
                )
            ),
            root_device_id=self.device.id
        )
        self.adapter_agent.create_logical_device(ld)
        self.logical_device = ld

    def add_port(self, port):
        self.adapter_agent.add_port(self.device.id, port)

        cap = OFPPF_10GB_FD | OFPPF_FIBER
        logical_port = LogicalPort(
            id='uni',
            ofp_port=ofp_port(
                port_no=port.port_no,
                hw_addr=mac_str_to_tuple(self.device.mac_address),
                name='{}-{}'.format(port.label, port.port_no),
                config=0,
                state=OFPPS_LIVE,
                curr=cap,
                advertised=cap,
                peer=cap,
                curr_speed=OFPPF_10GB_FD,
                max_speed=OFPPF_10GB_FD
            )
        )
        self.adapter_agent.add_logical_port(self.logical_device.id,
                                            logical_port)

    def activate(self):
        self.device.parent_id = self.logical_device.id
        self.device.oper_status = OperStatus.ACTIVE
        self.adapter_agent.update_device(self.device)
