#!/usr/bin/env python2

import subprocess, os, fnmatch, sys
from multiprocessing import Pool
import argparse

CPP = "g++"
BINARY = 'onion_test'
DBG_LEVEL = '3'
OPT_LEVEL = '3'
CPPFLAGS = ['-Wall', '-Werror', '-std=c++0x']
BUILDDIR = 'dist'
SOURCEDIR = 'src'
INCLUDES = ['../onion/src', '../onion/src/bindings/cpp']
LIBDIRS = ['../onion/src/onion', '../onion/src/bindings/cpp']
LIBS = ['onion', 'onioncpp']

def compile_worker(cmd, filename):
	print "Compiling " + filename + "..."
	subprocess.check_call(cmd)

def compile():
	pool = Pool()

	objects = []

	for root, dirnames, filenames in os.walk(SOURCEDIR):
		for filename in fnmatch.filter(filenames, '*.cpp'):
			cppfile = os.path.join(root, filename)
			objfile = cppfile[:-4] + '.o'
			cmd = [CPP, '-c', '-g' + DBG_LEVEL, '-O' + OPT_LEVEL] + CPPFLAGS + map(lambda x: '-I' + x, INCLUDES) + ['-o', objfile, cppfile]
			objects.append(objfile)
			pool.apply_async(compile_worker, args = (cmd, objfile, ))

	pool.close()
	pool.join()

	return objects

def link(objects):
	linktarget = BUILDDIR + '/' + BINARY
	cmd = [CPP] + ['-o', linktarget] + map(lambda x: '-L' + x, LIBDIRS) + map(lambda x: '-l' + x, LIBS) + objects
	print "Linking " + linktarget + "..."
	subprocess.check_call(cmd)

parser = argparse.ArgumentParser(description='Onion test build system')
parser.add_argument('action', choices=['build', 'clean', 'launch'], default='build', nargs='?', help='Action to do')

args = parser.parse_args()

if args.action == 'build':
	link(compile())
elif args.action == 'clean':
	for root, dirnames, filenames in os.walk(SOURCEDIR):
		for filename in fnmatch.filter(filenames, '*.o'):
			objfile = os.path.join(root, filename)
			print "Removing " + objfile + "..."
			os.remove(objfile)
	binfile = BUILDDIR + '/' + BINARY
	print "Removing " + binfile + "..."
	os.remove(binfile)
elif args.action == 'launch':
	envs = os.environ
	envs['LD_LIBRARY_PATH'] = ':'.join(LIBDIRS)
	if os.environ['LD_LIBRARY_PATH']:
		envs['LD_LIBRARY_PATH'] += ":" + os.environ['LD_LIBRARY_PATH']
	binfile = BUILDDIR + '/' + BINARY
	os.waitpid(subprocess.Popen(binfile, env=envs, shell=True).pid, 0)