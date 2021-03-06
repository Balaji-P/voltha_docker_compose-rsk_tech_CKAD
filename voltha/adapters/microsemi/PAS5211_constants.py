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
PAS5211 Constants
"""

# from enum PON_true_false_t
PON_FALSE = 0
PON_TRUE = 1

# from enum PON_enable_disable_t
PON_DISABLE = 0
PON_ENABLE = 1

# from enym PON_mac_t
PON_MII = 0
PON_GMII = 1
PON_TBI = 2

PON_POLARITY_ACTIVE_LOW = 0
PON_POLARITY_ACTIVE_HIGH = 1

PON_OPTICS_VOLTAGE_IF_UNDEFINED = 0
PON_OPTICS_VOLTAGE_IF_CML = 1
PON_OPTICS_VOLTAGE_IF_LVPECL = 2

PON_SD_SOURCE_LASER_SD = 0
PON_SD_SOURCE_BCDR_LOCK = 1
PON_SD_SOURCE_BCDR_SD = 2

PON_RESET_TYPE_DELAY_BASED = 0
PON_RESET_TYPE_SINGLE_RESET = 1
PON_RESET_TYPE_DOUBLE_RESET = 2

PON_RESET_TYPE_NORMAL_START_BURST_BASED = 0
PON_RESET_TYPE_NORMAL_END_BURST_BASED = 1

PON_GPIO_LINE_0 = 0
PON_GPIO_LINE_1 = 1
PON_GPIO_LINE_2 = 2
PON_GPIO_LINE_3 = 3
PON_GPIO_LINE_4 = 4
PON_GPIO_LINE_5 = 5
PON_GPIO_LINE_6 = 6
PON_GPIO_LINE_7 = 7
def PON_EXT_GPIO_LINE(line):
    return line + 8

# from enum PON_alarm_t
PON_ALARM_SOFTWARE_ERROR = 0
PON_ALARM_LOS = 1
PON_ALARM_LOSI = 2
PON_ALARM_DOWI = 3
PON_ALARM_LOFI = 4
PON_ALARM_RDII = 5
PON_ALARM_LOAMI = 6
PON_ALARM_LCDGI = 7
PON_ALARM_LOAI = 8
PON_ALARM_SDI = 9
PON_ALARM_SFI = 10
PON_ALARM_PEE = 11
PON_ALARM_DGI = 12
PON_ALARM_LOKI = 13
PON_ALARM_TIWI = 14
PON_ALARM_TIA = 15
PON_ALARM_VIRTUAL_SCOPE_ONU_LASER_ALWAYS_ON = 16
PON_ALARM_VIRTUAL_SCOPE_ONU_SIGNAL_DEGRADATION = 17
PON_ALARM_VIRTUAL_SCOPE_ONU_EOL = 18
PON_ALARM_VIRTUAL_SCOPE_ONU_EOL_DATABASE_IS_FULL = 19
PON_ALARM_AUTH_FAILED_IN_REGISTRATION_ID_MODE = 20
PON_ALARM_SUFI = 21
PON_ALARM_LAST_ALARM = 22

# from enum PON_general_parameters_type_t
PON_COMBINED_LOSI_LOFI 		            = 1000
PON_TX_ENABLE_DEFAULT 		            = 1001

# Enable or disable False queue full event from DBA
PON_FALSE_Q_FULL_EVENT_MODE             = 1002

# Set PID_AID_MISMATCH min silence period. 0 - disable, Else - period in secs
PON_PID_AID_MISMATCH_MIN_SILENCE_PERIOD = 1003

# Set if FW generate clear alarm. 0 - generate clear alarm, Else - don't
# generate clear alarm
PON_ENABLE_CLEAR_ALARM                  = 1004

# Enable or disabl send assign alloc id ploam. 0 - disable, 1 - enable
PON_ASSIGN_ALLOC_ID_PLOAM               = 1005

# BIP error polling period, 200 - 65000, 0 - Disabled, Recommended: 5000
# (default)
PON_BIP_ERR_POLLING_PERIOD_MS           = 1006

# Ignore SN when decatived 0 - consider SN (deactivate the onu if received
# same SN when activated (default)	1 - Ignore
PON_IGNORE_SN_WHEN_ACTIVE		        = 1007

# 0xffffffff - Disabled (default). Any other value (0 - 0xfffe) indicates
# that PA delay is enabled, with the specified delay value and included in
# the US_OVERHEAD PLOAM
PON_ONU_PRE_ASSIGNED_DELAY		        = 1008

# Enable or disable DS fragmentation, 0 disable, 1 enable
PON_DS_FRAGMENTATION			        = 1009

# Set if fw report rei alarm when errors is 0, 0 disable (default), 1 enable
PON_REI_ERRORS_REPORT_ALL		        = 1010

# Set if igonre sfi deactivation, 0 disable (default), 1 enable
PON_IGNORE_SFI_DEACTIVATION		        = 1011

# Allows to override the allocation overhead set by optic-params
# configuration. This configuration is only allowed when the the pon channel
# is disabled
PON_OVERRIDE_ALLOCATION_OVERHEAD	    = 1012

# Optics timeline offset, -128-127, : this parameter is very sensitive and
# requires coordination with PMC
PON_OPTICS_TIMELINE_OFFSET	            = 1013

# Last general meter
PON_LAST_GENERAL_PARAMETER		        = PON_OPTICS_TIMELINE_OFFSET

# from enum PON_dba_mode_t
PON_DBA_MODE_NOT_LOADED                 = 0
PON_DBA_MODE_LOADED_NOT_RUNNING         = 1
PON_DBA_MODE_RUNNING                    = 2
PON_DBA_MODE_LAST                       = 3

# from enum type typedef enum PON_port_frame_destination_t
PON_PORT_PON = 0
PON_PORT_SYSTEM = 1

# from enum PON_olt_hw_classification_t

PON_OLT_HW_CLASSIFICATION_PAUSE                    = 0
PON_OLT_HW_CLASSIFICATION_LINK_CONSTRAINT          = 1
PON_OLT_HW_CLASSIFICATION_IGMP                     = 2
PON_OLT_HW_CLASSIFICATION_MPCP                     = 3
PON_OLT_HW_CLASSIFICATION_OAM                      = 4
PON_OLT_HW_CLASSIFICATION_802_1X                   = 5
PON_OLT_HW_CLASSIFICATION_PPPOE_DISCOVERY          = 6
PON_OLT_HW_CLASSIFICATION_PPPOE_SESSION            = 7
PON_OLT_HW_CLASSIFICATION_DHCP_V4                  = 8
PON_OLT_HW_CLASSIFICATION_PIM                      = 9
PON_OLT_HW_CLASSIFICATION_DHCP_V6                  = 10
PON_OLT_HW_CLASSIFICATION_ICMP_V4                  = 11
PON_OLT_HW_CLASSIFICATION_MLD                      = 12
PON_OLT_HW_CLASSIFICATION_ARP                      = 13
PON_OLT_HW_CLASSIFICATION_CONF_DA                  = 14
PON_OLT_HW_CLASSIFICATION_CONF_RULE                = 15
PON_OLT_HW_CLASSIFICATION_DA_EQ_SA                 = 16
PON_OLT_HW_CLASSIFICATION_DA_EQ_MAC                = 17
PON_OLT_HW_CLASSIFICATION_DA_EQ_SEC_MAC            = 18
PON_OLT_HW_CLASSIFICATION_SA_EQ_MAC                = 19
PON_OLT_HW_CLASSIFICATION_SA_EQ_SEC_MAC            = 20
PON_OLT_HW_CLASSIFICATION_ETHERNET_MANAGEMENT      = 100
PON_OLT_HW_CLASSIFICATION_IPV4_LOCAL_MULTICAST     = 101
PON_OLT_HW_CLASSIFICATION_IPV4_MANAGEMENT          = 102
PON_OLT_HW_CLASSIFICATION_ALL_IPV4_MULTICAST       = 103
PON_OLT_HW_CLASSIFICATION_IPV6_LOCAL_MULTICAST     = 104
PON_OLT_HW_CLASSIFICATION_IPV6_MANAGEMENT          = 105
PON_OLT_HW_CLASSIFICATION_ALL_IPV6_MULTICAST       = 106
PON_OLT_HW_CLASSIFICATION_OTHER			           = 107
PON_OLT_HW_CLASSIFICATION_LAST_RULE                = 108