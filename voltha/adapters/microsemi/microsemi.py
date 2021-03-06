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
Microsemi/Celestica Ruby vOLTHA adapter.
"""
from common.frameio.frameio import BpfProgramFilter, FrameIOManager
from scapy.layers.l2 import Dot3
import structlog
from twisted.internet import reactor



from voltha.adapters.interface import IAdapterInterface
from voltha.adapters.microsemi.ActivationWatcher import ActivationWatcher
from voltha.adapters.microsemi.DeviceManager import DeviceManager
from voltha.adapters.microsemi.OltStateMachine import OltStateMachine
from voltha.adapters.microsemi.PAS5211_comm import PAS5211Communication
from voltha.protos import third_party
from voltha.protos.adapter_pb2 import Adapter, AdapterConfig
from voltha.protos.common_pb2 import LogLevel
from voltha.protos.device_pb2 import DeviceTypes, DeviceType
from voltha.protos.health_pb2 import HealthStatus
from voltha.registry import registry

from zope.interface import implementer

log = structlog.get_logger()
_ = third_party


@implementer(IAdapterInterface)
class RubyAdapter(object):

    name = "microsemi"

    supported_device_types = [
        DeviceType(
            id='microsemi',
            adapter=name,
            accepts_bulk_flow_update=True
        )
    ]

    def __init__(self, adaptor_agent, config):
        self.adaptor_agent = adaptor_agent
        self.config = config
        self.descriptor = Adapter(
            id=self.name,
            vendor='Microsemi / Celestica',
            version='0.1',
            config=AdapterConfig(log_level=LogLevel.INFO)
        )

        self.interface = registry('main').get_args().interface

    def start(self):
        log.info('starting')
        log.info('started')
        return self

    def stop(self):
        log.debug('stopping')
        # TODO Stop all OLTs
        log.info('stopped')
        return self

    def adapter_descriptor(self):
        return self.descriptor

    def device_types(self):
        return DeviceTypes(items=self.supported_device_types)

    def health(self):
        return HealthStatus(state=HealthStatus.HealthState.HEALTHY)

    def change_master_state(self, master):
        raise NotImplementedError()

    def adopt_device(self, device):
        device_manager = DeviceManager(device, self.adaptor_agent)
        target = device.mac_address
        comm = PAS5211Communication(dst_mac=target, iface=self.interface)
        olt = OltStateMachine(iface=self.interface, comm=comm,
                              target=target, device=device_manager)
        activation = ActivationWatcher(iface=self.interface, comm=comm,
                                       target=target, device=device_manager)
        reactor.callLater(0, self.__init_olt, olt, activation)

        log.info('adopted-device', device=device)
        # TODO store olt elements

    def abandon_device(self, device):
        raise NotImplementedError(0)

    def deactivate_device(self, device):
        raise NotImplementedError()

    def update_flows_bulk(self, device, flows, groups):
        log.debug('bulk-flow-update', device_id=device.id,
                  flows=flows, groups=groups)

    def send_proxied_message(self, proxy_address, msg):
        log.info('send-proxied-message', proxy_address=proxy_address, msg=msg)

    def receive_proxied_message(self, proxy_address, msg):
        raise NotImplementedError()

    def update_flows_incrementally(self, device, flow_changes, group_changes):
        raise NotImplementedError()

    def receive_packet_out(self, logical_device_id, egress_port_no, msg):
        log.info('packet-out', logical_device_id=logical_device_id,
                 egress_port_no=egress_port_no, msg_len=len(msg))

    ##
    # Private methods
    ##
    def __init_olt(self, olt, activation_watch):
        olt.runbg()
        activation_watch.runbg()






