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

"""
Tibit ONU device adapter
"""

import json

from uuid import uuid4

import structlog
from zope.interface import implementer

from scapy.layers.inet import ICMP, IP
from scapy.layers.l2 import Ether
from twisted.internet.defer import DeferredQueue, inlineCallbacks
from twisted.internet import reactor

from voltha.core.flow_decomposer import *
from voltha.core.logical_device_agent import mac_str_to_tuple

from voltha.adapters.interface import IAdapterInterface
from voltha.protos.adapter_pb2 import Adapter, AdapterConfig
from voltha.protos.device_pb2 import Port
from voltha.protos.device_pb2 import DeviceType, DeviceTypes
from voltha.protos.health_pb2 import HealthStatus
from voltha.protos.common_pb2 import LogLevel, ConnectStatus
from voltha.protos.common_pb2 import OperStatus, AdminState

from voltha.protos.logical_device_pb2 import LogicalDevice, LogicalPort
from voltha.protos.openflow_13_pb2 import ofp_desc, ofp_port, OFPPF_10GB_FD, \
    OFPPF_FIBER, OFPPS_LIVE, ofp_switch_features, OFPC_PORT_STATS, \
    OFPC_GROUP_STATS, OFPC_TABLE_STATS, OFPC_FLOW_STATS

from scapy.packet import Packet, bind_layers
from scapy.fields import StrField

log = structlog.get_logger()

from voltha.extensions.eoam.EOAM_TLV import AddStaticMacAddress, DeleteStaticMacAddress
from voltha.extensions.eoam.EOAM_TLV import ClearStaticMacTable
from voltha.extensions.eoam.EOAM_TLV import DeviceId
from voltha.extensions.eoam.EOAM import EOAMPayload, CablelabsOUI
from voltha.extensions.eoam.EOAM import DPoEOpcode_GetRequest, DPoEOpcode_SetRequest

@implementer(IAdapterInterface)
class TibitOnuAdapter(object):

    name = 'tibit_onu'

    supported_device_types = [
        DeviceType(
            id='tibit_onu',
            adapter=name,
            accepts_bulk_flow_update=True
        )
    ]

    def __init__(self, adapter_agent, config):
        self.adapter_agent = adapter_agent
        self.config = config
        self.descriptor = Adapter(
            id=self.name,
            vendor='Tibit Communications Inc.',
            version='0.1',
            config=AdapterConfig(log_level=LogLevel.INFO)
        )
        self.incoming_messages = DeferredQueue()

    def start(self):
        log.debug('starting')
        log.info('started')

    def stop(self):
        log.debug('stopping')
        log.info('stopped')

    def adapter_descriptor(self):
        return self.descriptor

    def device_types(self):
        return DeviceTypes(items=self.supported_device_types)

    def health(self):
        return HealthStatus(state=HealthStatus.HealthState.HEALTHY)

    def change_master_state(self, master):
        raise NotImplementedError()

    def adopt_device(self, device):
        log.info('adopt-device', device=device)
        reactor.callLater(0.1, self._onu_device_activation, device)
        return device

    @inlineCallbacks
    def _onu_device_activation(self, device):
        # first we verify that we got parent reference and proxy info
        assert device.parent_id
        assert device.proxy_address.device_id
        assert device.proxy_address.channel_id

        # TODO: For now, pretend that we were able to contact the device and obtain
        # additional information about it.  Should add real message.
        device.vendor = 'Tibit Communications, Inc.'
        device.model = '10G GPON ONU'
        device.hardware_version = 'fa161020'
        device.firmware_version = '16.10.01'
        device.software_version = '1.0'
        device.serial_number = uuid4().hex
        device.connect_status = ConnectStatus.REACHABLE
        self.adapter_agent.update_device(device)

        # then shortly after we create some ports for the device
        uni_port = Port(
            port_no=2,
            label='UNI facing Ethernet port',
            type=Port.ETHERNET_UNI,
            admin_state=AdminState.ENABLED,
            oper_status=OperStatus.ACTIVE
        )
        self.adapter_agent.add_port(device.id, uni_port)
        self.adapter_agent.add_port(device.id, Port(
            port_no=1,
            label='PON port',
            type=Port.PON_ONU,
            admin_state=AdminState.ENABLED,
            oper_status=OperStatus.ACTIVE,
            peers=[
                Port.PeerPort(
                    device_id=device.parent_id,
                    port_no=device.parent_port_no
                )
            ]
        ))

        # TODO adding vports to the logical device shall be done by agent?
        # then we create the logical device port that corresponds to the UNI
        # port of the device

        # obtain logical device id
        parent_device = self.adapter_agent.get_device(device.parent_id)
        logical_device_id = parent_device.parent_id
        assert logical_device_id

        # we are going to use the proxy_address.channel_id as unique number
        # and name for the virtual ports, as this is guaranteed to be unique
        # in the context of the OLT port, so it is also unique in the context
        # of the logical device
        port_no = device.proxy_address.channel_id
        cap = OFPPF_10GB_FD | OFPPF_FIBER
        self.adapter_agent.add_logical_port(logical_device_id, LogicalPort(
            id=str(port_no),
            ofp_port=ofp_port(
                port_no=port_no,
                hw_addr=mac_str_to_tuple(device.mac_address),
                name='uni-{}'.format(port_no),
                config=0,
                state=OFPPS_LIVE,
                curr=cap,
                advertised=cap,
                peer=cap,
                curr_speed=OFPPF_10GB_FD,
                max_speed=OFPPF_10GB_FD
            ),
            device_id=device.id,
            device_port_no=uni_port.port_no
        ))

        # simulate a proxied message sending and receving a reply
        reply = yield self._message_exchange(device)

        # and finally update to "ACTIVE"
        device = self.adapter_agent.get_device(device.id)
        device.oper_status = OperStatus.ACTIVE
        self.adapter_agent.update_device(device)

    def abandon_device(self, device):
        raise NotImplementedError(0
                                  )
    def deactivate_device(self, device):
        raise NotImplementedError()

    def update_flows_bulk(self, device, flows, groups):
        log.debug('bulk-flow-update', device_id=device.id,
                  flows=flows, groups=groups)

        # sample code that analyzes the incoming flow table
        assert len(groups.items) == 0, "Cannot yet deal with groups"

        for flow in flows.items:
            in_port = get_in_port(flow)
            assert in_port is not None

            if in_port == 2:

                # Downstream rule

                for field in get_ofb_fields(flow):
                    if field.type == ETH_TYPE:
                        _type = field.eth_type
                        pass  # construct ether type based condition here

                    elif field.type == IP_PROTO:
                        _proto = field.ip_proto
                        pass  # construct ip_proto based condition here

                    elif field.type == IN_PORT:
                        _port = field.port
                        pass  # construct in_port based condition here

                    elif field.type == VLAN_VID:
                        _vlan_vid = field.vlan_vid
                        pass  # construct VLAN ID based filter condition here

                    elif field.type == VLAN_PCP:
                        _vlan_pcp = field.vlan_pcp
                        pass  # construct VLAN PCP based filter condition here

                    # TODO
                    else:
                        raise NotImplementedError('field.type={}'.format(
                            field.type))

                for action in get_actions(flow):

                    if action.type == OUTPUT:
                        pass  # construct packet emit rule here

                    elif action.type == PUSH_VLAN:
                        if action.push.ethertype != 0x8100:
                            log.error('unhandled-ether-type',
                                      ethertype=action.push.ethertype)
                        pass  # construct vlan push command here

                    elif action.type == POP_VLAN:
                        pass  # construct vlan pop command here

                    elif action.type == SET_FIELD:
                        assert (action.set_field.field.oxm_class ==
                                ofp.OFPXMC_OPENFLOW_BASIC)
                        field = action.set_field.field.ofb_field
                        if field.type == VLAN_VID:
                            pass  # construct vlan_id set command here
                        else:
                            log.error('unsupported-action-set-field-type',
                                      field_type=field.type)

                    else:
                        log.error('unsupported-action-type',
                                  action_type=action.type)

                # final assembly of low level device flow rule and pushing it
                # down to device
                pass

            elif in_port == 1:

                # Upstream rule

                for field in get_ofb_fields(flow):
                    if field.type == ETH_TYPE:
                        _type = field.eth_type
                        pass  # construct ether type based condition here

                    elif field.type == IP_PROTO:
                        _proto = field.ip_proto
                        pass  # construct ip_proto based condition here

                    elif field.type == IN_PORT:
                        _port = field.port
                        pass  # construct in_port based condition here

                    elif field.type == VLAN_VID:
                        _vlan_vid = field.vlan_vid
                        pass  # construct VLAN ID based filter condition here

                    elif field.type == VLAN_PCP:
                        _vlan_pcp = field.vlan_pcp
                        pass  # construct VLAN PCP based filter condition here

                    elif field.type == IPV4_DST:
                        _ipv4_dst = field.ipv4_dst
                        pass  # construct IPv4 DST address based condition

                    elif field.type == UDP_DST:
                        _udp_dst = field.udp_dst
                        pass  # construct UDP SDT based filter here

                    # TODO
                    else:
                        raise NotImplementedError('field.type={}'.format(
                            field.type))

                for action in get_actions(flow):

                    if action.type == OUTPUT:
                        pass  # construct packet emit rule here

                    elif action.type == PUSH_VLAN:
                        if action.push.ethertype != 0x8100:
                            log.error('unhandled-ether-type',
                                      ethertype=action.push.ethertype)
                        pass  # construct vlan push command here

                    elif action.type == SET_FIELD:
                        assert (action.set_field.field.oxm_class ==
                                ofp.OFPXMC_OPENFLOW_BASIC)
                        field = action.set_field.field.ofb_field
                        if field.type == VLAN_VID:
                            pass  # construct vlan_id set command here
                        else:
                            log.error('unsupported-action-set-field-type',
                                      field_type=field.type)

                    else:
                        log.error('unsupported-action-type',
                                  action_type=action.type)

                # final assembly of low level device flow rule and pushing it
                # down to device
                pass

            else:
                raise Exception('Port should be 1 or 2 by our convention')

    def update_flows_incrementally(self, device, flow_changes, group_changes):
        raise NotImplementedError()

    def send_proxied_message(self, proxy_address, msg):
        raise NotImplementedError()

    def receive_proxied_message(self, proxy_address, msg):
        log.debug('receive-proxied-message',
                  proxy_address=proxy_address, msg=msg)
        self.incoming_messages.put(msg)

    @inlineCallbacks
    def _message_exchange(self, device):

        # register for receiving async messages
        self.adapter_agent.register_for_proxied_messages(device.proxy_address)

        # reset incoming message queue
        while self.incoming_messages.pending:
            _ = yield self.incoming_messages.get()

        # construct message
        msg = EOAMPayload(body=CablelabsOUI() /
                          DPoEOpcode_GetRequest() /
                          DeviceId()
                          )

        # send message
        log.info('ONU-send-proxied-message')
        self.adapter_agent.send_proxied_message(device.proxy_address, msg)

        log.info('ONU-log incoming messages BEFORE')
        # wait till we detect incoming message
        yield self.incoming_messages.get()
        log.info('ONU-log incoming messages AFTER')

        # by returning we allow the device to be shown as active, which
        # indirectly verified that message passing works

    def receive_packet_out(self, logical_device_id, egress_port_no, msg):
        log.info('packet-out', logical_device_id=logical_device_id,
                 egress_port_no=egress_port_no, msg_len=len(msg))
