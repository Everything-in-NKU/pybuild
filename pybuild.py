#!/usr/bin/env python
# coding:utf-8

import sys, os, re
import distutils.core, py2exe
import optparse
import shutil
import zipfile

manifest_template = '''
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<assembly xmlns="urn:schemas-microsoft-com:asm.v1" manifestVersion="1.0">
<assemblyIdentity
    version="5.0.0.0"
    processorArchitecture="x86"
    name="%(prog)s"
    type="win32"
/>
<description>%(prog)s Program</description>
<dependency>
    <dependentAssembly>
        <assemblyIdentity
            type="win32"
            name="Microsoft.Windows.Common-Controls"
            version="6.0.0.0"
            processorArchitecture="X86"
            publicKeyToken="6595b64144ccf1df"
            language="*"
        />
    </dependentAssembly>
</dependency>
</assembly>
'''

RT_MANIFEST = 24

class Py2exe(py2exe.build_exe.py2exe):
    """A py2exe which archive *.py files to zip"""
    def _find_pyo_path(self, pyo_path):
        """_weakrefset.pyo ->  D:\Python27\Lib\_weakrefset.py"""
        assert pyo_path.endswith(('.pyo', 'pyc'))
        py_base_path = pyo_path[:-1]
        for path in sys.path:
            py_path = os.path.join(path, py_base_path)
            if os.path.isfile(py_path):
                return py_path
    def make_lib_archive(self, zip_filename, base_dir, files,
                         verbose=0, dry_run=0):
        from distutils.dir_util import mkpath
        if not self.skip_archive:
            # Like distutils "make_archive", but we can specify the files
            # to include, and the compression to use - default is
            # ZIP_STORED to keep the runtime performance up.  Also, we
            # don't append '.zip' to the filename.
            mkpath(os.path.dirname(zip_filename), dry_run=dry_run)

            if self.compressed:
                compression = zipfile.ZIP_DEFLATED
            else:
                compression = zipfile.ZIP_STORED

            if not dry_run:
                z = zipfile.ZipFile(zip_filename, "w",
                                    compression=compression)
                for f in files:
                    if f.endswith(('.pyo', '.pyc')):
                        py_path = self._find_pyo_path(f)
                        assert py_path, 'cannot locate in %r in %s' % (f, sys.path)
                        z.write(py_path, f[:-1])
                    else:
                        z.write(os.path.join(base_dir, f), f)
                z.close()

            return zip_filename
        else:
            # Don't really produce an archive, just copy the files.
            from distutils.file_util import copy_file

            destFolder = os.path.dirname(zip_filename)

            for f in files:
                d = os.path.dirname(f)
                if d:
                    mkpath(os.path.join(destFolder, d), verbose=verbose, dry_run=dry_run)
                copy_file(
                          os.path.join(base_dir, f),
                          os.path.join(destFolder, f),
                          preserve_mode=0,
                          verbose=verbose,
                          dry_run=dry_run
                         )
            return '.'

class Py2exeUPX(py2exe.build_exe.py2exe):
    '''from http://www.py2exe.org/index.cgi/BetterCompression'''
    def initialize_options(self):
        # Add a new "upx" option for compression with upx
        py2exe.build_exe.py2exe.initialize_options(self)
        self.upx = 1
    def copy_file(self, *args, **kwargs):
        # Override to UPX copied binaries.
        (fname, copied) = result = py2exe.build_exe.py2exe.copy_file(self, *args, **kwargs)
        basename = os.path.basename(fname)
        if (copied and self.upx and
            (basename[:6]+basename[-4:]).lower() != 'python.dll' and
            fname[-4:].lower() in ('.pyd', '.dll')):
            os.system('upx --best "%s"' % os.path.normpath(fname))
        return result
    def patch_python_dll_winver(self, dll_name, new_winver=None):
        # Override this to first check if the file is upx'd and skip if so
        if not self.dry_run:
            if not os.system('upx -qt "%s" >nul' % dll_name):
                if self.verbose:
                    print "Skipping setting sys.winver for '%s' (UPX'd)" % \
                          dll_name
            else:
                py2exe.build_exe.py2exe.patch_python_dll_winver(self, dll_name, new_winver)
                # We UPX this one file here rather than in copy_file so
                # the version adjustment can be successful
                if self.upx:
                    os.system('upx --best "%s"' % os.path.normpath(dll_name))

def optparse_options_to_dist_options(filename, options):
    basename = os.path.splitext(os.path.basename(filename))[0]

    mode = 'windows' if options.windowed else 'console'
    mode_options = {'script'          : filename,
                    'version'         : options.version or '1.0',
                    'name'            : options.name or basename,
                    'company_name'    : options.company or None,
                    'icon_resources'  : [(1, options.icon)] if options.icon else [],
                    'other_resources' : [(RT_MANIFEST, 1, manifest_template % dict(prog=basename))] if mode == 'windows' else [],
                    }

    py2exe_options = {'dist_dir'     : 'dist',
                      'compressed'   : 1,
                      'optimize'     : 1,
                      'dll_excludes' : ['w9xpopen.exe', 'MSVCP90.dll', 'mswsock.dll', 'powrprof.dll'],
                      'ascii'        : options.ascii or False,
                      'bundle_files' : options.bundle or 1,
                      'excludes'     : options.excludes.split(',') or [],
                     }

    zipfile = options.zipfile
    cmdclass = Py2exeUPX if options.upx else Py2exe

    return { mode      :  [mode_options],
            'zipfile'  :  zipfile,
            'options'  :  {'py2exe' : py2exe_options},
            'cmdclass' :  {'py2exe' : cmdclass},
            }

def finalize(windows=None, console=None, service=None, com_server=None, ctypes_com_server=None, zipfile=None, options=None, cmdclass=None):
    shutil.rmtree('build')
    mode = [x for x in (windows, console, service, com_server, ctypes_com_server) if x is not None][0][0]
    py2exe_options = options['py2exe']
    basename = os.path.splitext(os.path.basename(mode['script']))[0]
    if py2exe_options['bundle_files'] == 1:
        dist_files = ['%s.exe' % basename]
        if zipfile is not None:
            dist_files += [zipfile]
        dist_dir = py2exe_options.get('dist_dir', 'dist')
        for filename in dist_files:
            shutil.move(os.path.join(dist_dir, filename), filename)
        shutil.rmtree(dist_dir)

def main():
    parser = optparse.OptionParser(usage='usage: %prog [options] filename')
    parser.add_option("-w", "--windowed", dest="windowed", action="store_true", default=False, help="Use the Windows subsystem executable.")
    parser.add_option("-a", "--ascii",    dest="ascii",    action="store_true", default=False, help="do not include encodings.")
    parser.add_option("-b", "--bundle",   dest="bundle",   type="int",    metavar="LEVEL",  help="produce a bundle_files deployment.")
    parser.add_option("-v", "--version",  dest="version",  type="string", metavar="number", help="add version number to the executable.")
    parser.add_option("-n", "--name",     dest="name",     type="string", help="add name string to the executable.")
    parser.add_option("-c", "--company",  dest="company",  type="string", help="add company string to the executable.")
    parser.add_option("-i", "--icon"   ,  dest="icon",     type="string", metavar="file.ico", help="add file.ico to the executable's resources.")
    parser.add_option("-z", "--zipfile",  dest="zipfile",  type="string", metavar="file.zip", help="add file.zip to the extra resources.")
    parser.add_option("-X", "--upx"   ,   dest="upx",      action="store_true", default=False, help="if you have UPX installed (detected by Configure), this will use it to compress your executable.")
    parser.add_option("-x", "--excludes", dest="excludes", type="string", default='', help="py2exe excludes packages.")

    options, args = parser.parse_args()
    if len(args) == 0:
        parser.print_help()
        sys.exit(0)
    else:
        print options, args

    filename = args[0]
    dist_options = optparse_options_to_dist_options(filename, options)
    print dist_options

    sys.argv[1:] = ['py2exe', '-q']
    distutils.core.setup(**dist_options)
    finalize(**dist_options)

    if sys.version_info[:2] > (2, 5):
        print "you need vc2008redist['Microsoft.VC90.CRT.manifest', 'msvcr90.dll']"

if __name__ == '__main__':
    main()