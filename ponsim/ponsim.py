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
Simple PON Simulator which would not be needed if openvswitch could do
802.1ad (QinQ), which it cannot (the reason is beyond me), or if CPQD could
handle 0-tagged packets (no comment).
"""
import structlog
from scapy.layers.inet import IP, UDP
from scapy.layers.l2 import Ether, Dot1Q
from scapy.packet import Packet

from common.frameio.frameio import hexify
from voltha.protos import third_party
from voltha.core.flow_decomposer import *
_ = third_party


def ipv4int2str(ipv4int):
    return '{}.{}.{}.{}'.format(
        (ipv4int >> 24) & 0xff,
        (ipv4int >> 16) & 0xff,
        (ipv4int >> 8) & 0xff,
        ipv4int & 0xff
    )


class SimDevice(object):

    def __init__(self, name, logical_port_no):
        self.name = name
        self.logical_port_no = logical_port_no
        self.links = dict()
        self.flows = list()
        self.log = structlog.get_logger(name=name,
                                        logical_port_no=logical_port_no)

    def link(self, port, egress_fun):
        self.links.setdefault(port, []).append(egress_fun)

    def ingress(self, port, frame):
        self.log.debug('ingress', ingress_port=port)
        outcome = self.process_frame(port, frame)
        if outcome is not None:
            egress_port, egress_frame = outcome
            forwarded = 0
            links = self.links.get(egress_port)
            if links is not None:
                for fun in links:
                    forwarded += 1
                    self.log.debug('forwarding', egress_port=egress_port)
                    fun(egress_port, egress_frame)
            if not forwarded:
                self.log.debug('no-one-to-forward-to', egress_port=egress_port)
        else:
            self.log.debug('dropped')

    def install_flows(self, flows):
        # store flows in precedence order so we can roll down on frame arrival
        self.flows = sorted(flows, key=lambda fm: fm.priority, reverse=True)

    def process_frame(self, ingress_port, ingress_frame):
        for flow in self.flows:
            if self.is_match(flow, ingress_port, ingress_frame):
                egress_port, egress_frame = self.process_actions(
                    flow, ingress_frame)
                return egress_port, egress_frame
        return None

    @staticmethod
    def is_match(flow, ingress_port, frame):

        def get_non_shim_ether_type(f):
            if f.haslayer(Dot1Q):
                f = f.getlayer(Dot1Q)
            return f.type

        def get_vlan_pcp(f):
            if f.haslayer(Dot1Q):
                return f.getlayer(Dot1Q).prio

        def get_ip_proto(f):
            if f.haslayer(IP):
                return f.getlayer(IP).proto

        def get_ipv4_dst(f):
            if f.haslayer(IP):
                return f.getlayer(IP).dst

        def get_udp_dst(f):
            if f.haslayer(UDP):
                return f.getlayer(UDP).dport

        for field in get_ofb_fields(flow):

            if field.type == IN_PORT:
                if field.port != ingress_port:
                    return False

            elif field.type == ETH_TYPE:
                if field.eth_type != get_non_shim_ether_type(frame):
                    return False

            elif field.type == IP_PROTO:
                if field.ip_proto != get_ip_proto(frame):
                    return False

            elif field.type == VLAN_VID:
                expected_vlan = field.vlan_vid
                tagged = frame.haslayer(Dot1Q)
                if bool(expected_vlan & 4096) != bool(tagged):
                    return False
                if tagged:
                    actual_vid = frame.getlayer(Dot1Q).vlan
                    if actual_vid != expected_vlan & 4095:
                        return False

            elif field.type == VLAN_PCP:
                if field.vlan_pcp != get_vlan_pcp(frame):
                    return False

            elif field.type == IPV4_DST:
                if ipv4int2str(field.ipv4_dst) != get_ipv4_dst(frame):
                    return False

            elif field.type == UDP_DST:
                if field.udsp_dst != get_udp_dst(frame):
                    return False

            else:
                raise NotImplementedError('field.type=%d' % field.type)

        return True

    @staticmethod
    def process_actions(flow, frame):
        egress_port = None
        for action in get_actions(flow):

            if action.type == OUTPUT:
                egress_port = action.output.port

            elif action.type == POP_VLAN:
                if frame.haslayer(Dot1Q):
                    shim = frame.getlayer(Dot1Q)
                    frame = Ether(
                        src=frame.src,
                        dst=frame.dst,
                        type=shim.type) / shim.payload

            elif action.type == PUSH_VLAN:
                frame = (
                    Ether(src=frame.src, dst=frame.dst,
                          type=action.push.ethertype) /
                    Dot1Q(type=frame.type) /
                    frame.payload
                )

            elif action.type == SET_FIELD:
                assert (action.set_field.field.oxm_class ==
                        ofp.OFPXMC_OPENFLOW_BASIC)
                field = action.set_field.field.ofb_field

                if field.type == VLAN_VID:
                    shim = frame.getlayer(Dot1Q)
                    shim.vlan = field.vlan_vid & 4095

                elif field.type == VLAN_PCP:
                    shim = frame.getlayer(Dot1Q)
                    shim.prio = field.vlan_pcp

                else:
                    raise NotImplementedError('set_field.field.type=%d'
                                              % field.type)

            else:
                raise NotImplementedError('action.type=%d' % action.type)

        return egress_port, frame


class PonSim(object):

    def __init__(self, onus, egress_fun):
        self.egress_fun = egress_fun

        # Create OLT and hook NNI port up for egress
        self.olt = SimDevice('olt', 0)
        self.olt.link(2, lambda _, frame: self.egress_fun(0, frame))
        self.devices = dict()
        self.devices[0] = self.olt

        # Create ONUs of the requested number and hook them up with OLT
        # and with egress fun
        def mk_egress_fun(port_no):
            return lambda _, frame: self.egress_fun(port_no, frame)

        def mk_onu_ingress(onu):
            return lambda _, frame: onu.ingress(1, frame)

        for i in range(onus):
            port_no = 128 + i
            onu = SimDevice('onu%d' % i, port_no)
            onu.link(1, lambda _, frame: self.olt.ingress(1, frame))
            onu.link(2, mk_egress_fun(port_no))
            self.olt.link(1, mk_onu_ingress(onu))
            self.devices[port_no] = onu

    def get_ports(self):
        return sorted(self.devices.keys())

    def olt_install_flows(self, flows):
        self.olt.install_flows(flows)

    def onu_install_flows(self, onu_port, flows):
        self.devices[onu_port].install_flows(flows)

    def ingress(self, port, frame):
        if not isinstance(frame, Packet):
            frame = Ether(frame)
        self.devices[port].ingress(2, frame)

