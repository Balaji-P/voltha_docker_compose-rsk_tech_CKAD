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
from enum import Enum
from scapy.fields import PadField
from scapy.packet import Raw


class OmciUninitializedFieldError(Exception): pass


class FixedLenField(PadField):
    """
    This Pad field limits parsing of its content to its size
    """
    def __init__(self, fld, align, padwith='\x00'):
        super(FixedLenField, self).__init__(fld, align, padwith)

    def getfield(self, pkt, s):
        remain, val = self._fld.getfield(pkt, s[:self._align])
        if isinstance(val.payload, Raw) and \
                not val.payload.load.replace(self._padwith, ''):
            # raw payload is just padding
            val.remove_payload()
        return remain + s[self._align:], val


def bitpos_from_mask(mask, lsb_pos=0, increment=1):
    """
    Turn a decimal value (bitmask) into a list of indices where each
    index value corresponds to the bit position of a bit that was set (1)
    in the mask. What numbers are assigned to the bit positions is controlled
    by lsb_pos and increment, as explained below.
    :param mask: a decimal value used as a bit mask
    :param lsb_pos: The decimal value associated with the LSB bit
    :param increment: If this is +i, then the bit next to LSB will take
    the decimal value of lsb_pos + i.
    :return: List of bit positions where the bit was set in mask
    """
    out = []
    while mask:
        if mask & 0x01:
            out.append(lsb_pos)
        lsb_pos += increment
        mask >>= 1
    return sorted(out)


class AttributeAccess(Enum):
    Readable = 1
    R = 1
    Writable = 2
    W = 2
    SetByCreate = 3
    SBC = 3


OmciNullPointer = 0xffff


class EntityOperations(Enum):
    # keep these numbers match msg_type field per OMCI spec
    Create = 4
    CreateComplete = 5
    Delete = 6
    Set = 8
    Get = 9
    GetComplete = 10
    GetAllAlarms = 11
    GetAllAlarmsNext = 12
    MibUpload = 13
    MibUploadNext = 14
    MibReset = 15
    AlarmNotification = 16
    AttributeValueChange = 17
    Test = 18
    StartSoftwareDownload = 19
    DownlaodSection = 20
    EndSoftwareDownload = 21
    ActivateSoftware = 22
    CommitSoftware = 23
    SynchronizeTime = 24
    Reboot = 25
    GetNext = 26
    TestResult = 27
    GetCurrentData = 28


