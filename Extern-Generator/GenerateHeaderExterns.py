#!/usr/bin/env python

# Created by Tyrone Trevorrow on 10/03/12.
# Copyright (c) 2012 Sudeium. All rights reserved.

# Given a C/Obj-C file, finds all the top level constants
# and generates a header file with all these constants as externs.
# Requires libclang
import os
import sys
import ctypes
import shutil
import filecmp
import shelve

# Globals
me = os.path.basename(__file__)
header_externs_begin = "#pragma GenerateHeaderExterns Begin".lower()
header_externs_end = "#pragma GenerateHeaderExterns End".lower()

if "--debug" in sys.argv:
	debug = True
else:
	debug = False

def dprint(str):
	if debug:
		print ("%s: " % me) + str

try:
	from clang import cindex
except:
	print "%s: couldn't import clang.  Probably a version conflict with Xcode." % me
	exit(1)
			
def print_nodes_recursive(node, depth):
	print ('\t' * depth), node.kind, node.spelling
	for child in node.get_children():
		print_nodes_recursive(child, depth+1)

type_kind_names = {
	cindex.TypeKind.BOOL: "bool",
	cindex.TypeKind.CHAR_U: "char",
	cindex.TypeKind.UCHAR: "unsigned char",
	cindex.TypeKind.CHAR16: "short",
	cindex.TypeKind.CHAR32: "int",
	cindex.TypeKind.USHORT: "unsigned short",
	cindex.TypeKind.UINT: "unsigned int",
	cindex.TypeKind.ULONG: "unsigned long",
	cindex.TypeKind.ULONGLONG: "unsigned long long",
	cindex.TypeKind.UINT128: "__uint128_t",
	cindex.TypeKind.CHAR_S: "char",
	cindex.TypeKind.SCHAR: "char",
	cindex.TypeKind.WCHAR: "char",
	cindex.TypeKind.SHORT: "short",
	cindex.TypeKind.INT: "int",
	cindex.TypeKind.LONG: "long",
	cindex.TypeKind.LONGLONG: "long long",
	cindex.TypeKind.INT128: "__int128_t",
	cindex.TypeKind.FLOAT: "float",
	cindex.TypeKind.DOUBLE: "double",
	cindex.TypeKind.LONGDOUBLE: "long double",
	cindex.TypeKind.OBJCID: "id",
	cindex.TypeKind.OBJCCLASS: "Class",
	cindex.TypeKind.OBJCSEL: "SEL"
}

def typename_for_symbol(node):
	return type_kind_names[node.type.kind]

def emit_extern_for_symbol(node):
	typedef = "extern "
	nodetype = node.type
	if (node.type.kind == cindex.TypeKind.POINTER) or (node.type.kind == cindex.TypeKind.OBJCOBJECTPOINTER):
		# Emit the type and a *
		decl = nodetype.get_pointee().get_declaration()
		typedef = typedef + decl.spelling + "* "
	else:
		# Dealing with all the other types is gonna be a suck
		decl = nodetype.get_declaration()
		if (decl.kind == cindex.CursorKind.NO_DECL_FOUND):
			# Primitive type: These are annoying
			typedef = typedef + typename_for_symbol(node) + " "
		else:
			typedef = typedef + decl.spelling + " "
	if nodetype.is_const_qualified():
		typedef = typedef + "const "
	typedef = typedef + node.displayname + ';'
	return typedef

def node_is_constant(node):
	if (node.type.is_const_qualified):
		return True
	elif (node.type.kind == TypeKind.CONSTANTARRAY):
		return True
	else:
		return False

def insert_externs_into_header(headerfile, externs):
	tmpfile = headerfile + ".tmp"
	try:
		readfile = open(headerfile)
		writefile = open(tmpfile, 'w')
	except:
		print "%s: warning: couldn't open header file '%s'." % me, headerfile
		return
	insideblock = False
	for line in readfile:
		if not insideblock:
			writefile.write(line)
		if line.strip().lower() == header_externs_begin:
			if debug and not insideblock:
				dprint("found %s" % header_externs_begin)
			insideblock = True
			writefile.write('\n'.join(externs))
			writefile.write('\n')
		elif line.strip().lower() == header_externs_end:
			if debug and insideblock:
				dprint("found %s" % header_externs_end)
			insideblock = False
			writefile.write(line)
	readfile.close()
	writefile.close()
	if not filecmp.cmp(headerfile, tmpfile, shallow=False):
		try:
			os.remove(headerfile)
			shutil.move(tmpfile, headerfile)
		except:
			print "%s: error: couldn't remove headerfile to make way for new one.  Aborting." % me
			os.remove(tmpfile)
			exit(1)
	else:
		try:
			os.remove(tmpfile)
		except:
			print "%s: error: couldn't remove temp file.  You may have litter in your repository." % me
			exit(1)


def extract_symbols_for_file(filename):
	dprint("opened: %s" % filename)
	externs = []
	clang_indexer = cindex.Index.create()
	tu = clang_indexer.parse(filename, ["-framework=Foundation"])
	for node in tu.cursor.get_children():
		if node.kind == cindex.CursorKind.VAR_DECL:
			if (node.location.file.name == filename) and node.type.is_const_qualified():
				externs.append(emit_extern_for_symbol(node))
	filename, fileExt = os.path.splitext(filename)
	dprint("externs for %s: \n%s" % (filename, " ".join(externs)))
	insert_externs_into_header(filename + ".h", externs)

def has_file_updated(filename, db):
	if not filename in db:
		db[filename] = os.path.getmtime(filename)
		return True
	elif os.path.getmtime(filename) > db[filename]:
		db[filename] = os.path.getmtime(filename)
		return True
	else:
		return False

def main():
	if not "PROJECT_DIR" in os.environ:
		print "%s: error: please run from Xcode." % me

	temp_dir = os.environ["TARGET_TEMP_DIR"]
	db = shelve.open(temp_dir + "/generateheaderexterns")
	dprint("opened database %s" % temp_dir + "/generateheaderexterns")
	filelist = filter(lambda s: s and not s.startswith("--"), sys.argv[1:])
	for filename in filelist:
		if has_file_updated(filename, db):
			extract_symbols_for_file(filename)
		else:
			dprint("skipping file: %s" % filename)


main()
