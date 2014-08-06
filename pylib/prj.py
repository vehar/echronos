import os
import sys
import ice
import signal
import zipfile
from .utils import get_host_platform_name, top_path, chdir, base_path


def prj_build(args):
    """
    Build a standalone version of the 'prj' tool in the directory
    prj_build_<host>. This tool is bundled with the release in the
    build-release step.
    """
    host = get_host_platform_name()

    prj_build_path = top_path(args.topdir, 'prj_build_{}'.format(host))
    os.makedirs(prj_build_path, exist_ok=True)

    if sys.platform == 'win32':
        _prj_build_win32(prj_build_path)
    else:
        _prj_build_unix(prj_build_path, host)


def _prj_build_unix(output_dir, host):
    if sys.platform == 'darwin':
        extras = ['-framework', 'CoreFoundation', '-lz']
    elif sys.platform == 'linux':
        extras = ['-lz', '-lm', '-lpthread', '-lrt', '-ldl', '-lcrypt', '-lutil']
    else:
        print("Building prj currently unsupported on {}".format(sys.platform))
        return 1

    with chdir(output_dir):
        ice.create_lib('prj', '../prj/app', main='prj')
        ice.create_lib('prjlib', '../prj/app/lib')
        ice.create_lib('pystache', '../prj/app/pystache',
                       excluded=['setup', 'pystache.tests', 'pystache.commands'])
        ice.create_lib('ply', '../prj/app/ply', excluded=['setup'])
        ice.create_stdlib()
        ice.create_app(['stdlib', 'prj', 'prjlib', 'pystache', 'ply'])

        cmd = ['gcc', '*.c', '-o', 'prj', '-I../tools/include/python3.3m/',
               '-I../tools/{}/include/python3.3m/'.format(host),
               '-L../tools/{}/lib/python3.3/config-3.3m'.format(host),
               '-lpython3.3m']
        cmd += extras

        cmd = ' '.join(cmd)
        r = os.system(cmd)
        if r != 0:
            print("Error building {}. cmd={}. ".format(_show_exit(r), cmd))


def _show_exit(exit_code):
    sig_num = exit_code & 0xff
    exit_status = exit_code >> 8
    if sig_num == 0:
        return "exit: {}".format(exit_status)
    else:
        _SIG_NAMES = {k: v for v, k in signal.__dict__.items() if v.startswith('SIG')}
        return "signal: {}".format(_SIG_NAMES.get(sig_num, 'Unknown signal {}'.format(sig_num)))


def _prj_build_win32(output_dir):
    """Create a distributable version of prj.py.

    We currently do not have the infrastructure in place to statically compile and link prj.py and its dependencies
    against the complete python interpreter.

    However, it is still desirable to create only a single resource that can stand alone given an installed python
    interpreter.
    Therefore, collect prj and its dependencies in a zip file that is executable by the python interpreter.

    """
    with zipfile.ZipFile(os.path.join(output_dir, 'prj'), mode='w') as zip_file:
        top = os.path.abspath(base_path('prj', 'app'))
        for dir_path, _, file_names in os.walk(top):
            archive_dir_path = os.path.relpath(dir_path, top)
            for file_name in file_names:
                file_path = os.path.join(dir_path, file_name)
                if dir_path == top and file_name == 'prj.py':
                    # The python interpreter expects to be informed about the main file in the zip file by naming it
                    # __main__.py
                    archive_file_path = os.path.join(archive_dir_path, '__main__.py')
                else:
                    archive_file_path = os.path.join(archive_dir_path, file_name)
                zip_file.write(file_path, archive_file_path)
    with open(os.path.join(output_dir, 'prj.bat'), 'w') as f:
        f.write('@ECHO OFF\npython %~dp0\\prj')