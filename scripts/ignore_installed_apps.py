#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import print_function

"""
Ignore installed apps with aeios
"""

__author__ = 'Sam Forester'
__email__ = 'sam.forester@utah.edu'
__copyright__ = 'Copyright (c) 2019 University of Utah, Marriott Library'
__license__ = 'MIT'
__version__ = "1.0.0"

import os
import sys
import subprocess

import aeios
from aeios.apps import App, AppList


def usage(msg=''):
	"""
	:returns: usage string
	"""
	msg += ("{0}: [--help|--reset|--show]".format(os.path.basename(__file__)),
			"   --help     print this help message",
			"   --reset    clear all currently ignored apps",
			"   --show     print currently ignored app names")
	return "\n".join(msg)	


def aeios_is_running():
	"""
	Check if aeios automation is currently running
	:returns: True if running, else False
	"""
	try:
		cmd = ['/bin/launchctl', 'list', 'edu.utah.mlib.aeios']
		subprocess.check_call(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		is_running = True
	except subprocess.CalledProcessError as e:
		is_running = False
	return is_running


def show_ignored_apps(manager):
	"""
	:returns: ignored app string
	"""
	try:
		result = u"Ignored apps:"
		for name in sorted(manager.apps.record['Ignored']):
			result += u'\n  "{0!s}"'.format(name)
	except KeyError:
		result = "no apps ignored"
	return result


def main(arg):
	"""
	Gets all currently installed apps on all connected devices and add them to Ignored
	group
	"""
	
	# check for running automation
	if aeios_is_running():
		err = "aeios is currently running. run `aeiosutil stop` and try again."
		raise SystemExit(err)

	manager = aeios.DeviceManager()
	
	# check for unknown args
	if arg and arg not in ('--help', '--reset', '--show'):
		raise SystemExit(usage("unknown flag: {0!r}\n".format(arg)))

	# simple arg parsing
	if arg == '--help':
		raise SystemExit(usage())
	elif arg == '--reset':
		# clear out existing MDM key (if any)
		try:
			manager.apps.config.delete('Ignored')
		except KeyError:
			pass
		raise SystemExit("ignored apps reset")
	elif arg == '--show':
		# show currently ignored apps and exit
		raise SystemExit(show_ignored_apps(manager))

	# DeviceList of all currently available devices
	devices = manager.available()
	if not devices:
		raise SystemExit("no devices available")

	# get all apps installed on all devices as AppList
	all_app_info = manager.apps.installedapps(devices)
	apps = AppList([App(i) for i in all_app_info])
	
	# add all apps currently installed apps to 'MDM' group
	manager.apps.add('Ignored', sorted(set(apps.names)))

	print(show_ignored_apps(manager), file=sys.stderr)


if __name__ == '__main__':
	try:
		arg = sys.argv[1]
	except IndexError:
		arg = None

	main(arg)
