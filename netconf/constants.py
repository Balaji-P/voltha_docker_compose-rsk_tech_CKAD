#!/usr/bin/env python
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

class Constants:

	SSH_SUBSYSTEM = "netconf"

	# Secure credentials directories
	# TODO:  In a production environment these locations require better
	# protection.  For now the user_passwords file is just a plain text file.
	KEYS_DIRECTORY = 'security/keys'
	CERTS_DIRECTORY = 'security/certificates'
	CLIENT_CRED_DIRECTORY = 'security/client_credentials'

	# Datastores
	RUNNING = "running"
	CANDIDATE = "candidate"
	STARTUP = "startup"

	# RPC - base netconf
	GET = "get"
	GET_CONFIG = "get-config"
	COPY_CONFIG = "copy-config"
	EDIT_CONFIG = "edit-config"
	DELETE_CONFIG = "delete-config"
	LOCK = "lock"
	UNLOCK = "unlock"
	CLOSE_SESSION = "close-session"
	KILL_SESSION = "kill-session"

	# Operations
	OPERATION = "operation"
	DEFAULT_OPERATION = "default-operation"
	MERGE = "merge"
	REPLACE = "replace"
	CREATE = "create"
	DELETE = "delete"
	NONE = "none"

    # Netconf namespaces
	NETCONF_BASE_10 = "urn:ietf:params:netconf:base:1.0"
	NETCONF_BASE_11 = "urn:ietf:params:netconf:base:1.1"
	NETCONF_MONITORING = "urn:ietf:params:xml:ns:yang:ietf-netconf-monitoring"

	# XML
	XML_HEADER = """<?xml version="1.0" encoding="utf-8"?>"""

	# Capability xpath
	CAPABILITY_XPATH = "//nc:hello/nc:capabilities/nc:capability"
	RPC_XPATH = "/nc:rpc"

	NC_SOURCE="nc:source"
	SOURCE = "source"
	TARGET = "target"
	CONFIG = "config"
	

	TEST_OPTION = "test-option"
	TEST_THEN_SET = "test-then-set"
	SET = "set"

	ERROR_OPTION = "error-option"
	STOP_ON_ERROR = "stop-on-error"
	CONTINUE_ON_ERROR = "continue-on-error"
	ROLLBACK_ON_ERROR = "rollback-on-error"

	#tags
	NC = "nc"
	RPC = "rpc"
	RPC_REPLY = "rpc-reply"
	RPC_ERROR = "rpc-error"
	CAPABILITY = "capability"
	CAPABILITIES = "capabilities"
	HELLO = "hello"
	URL = "url"
	NC_FILTER="nc:filter"
	FILTER = "filter"
	SUBTREE = "subtree"
	XPATH = "xpath"
	OK = "ok"
	SESSION_ID = "session-id"
	MESSAGE_ID = "message-id"
	XMLNS = "xmlns"
	DELIMITER = "]]>]]>"
