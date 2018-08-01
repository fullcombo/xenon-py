import os
import kivy
from os.path import join, exists
from kivy.utils import platform

if platform == 'win':
    from kivy.deps import sdl2, glew
else:
    glew = sdl2 = None


IS_LINUX = os.name == 'posix' and os.uname()[0] == 'Linux'
if IS_LINUX:
    from PyInstaller.depend import dylib
    dylib._unix_excludes.update({
        r'.*nvidia.*': 1,
        r'.*libdrm.*': 1,
        r'.*hashlib.*': 1,
    })

# -*- mode: python -*-

block_cipher = None


a = Analysis(['main.py'],
             pathex=['T:\\User Profile\\My Documents\\PyCharm\\Paranoia'],
             binaries=[],
             datas=[],
             hiddenimports=['sdl2','multiprocessing','pkg_resources','resource','posix','java'],
             excludes=['gstreamer'],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher
             )
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          exclude_binaries=True,
          name='main',
          debug=False,
          strip=False,
          upx=True,
          console=False )
coll = COLLECT(exe, Tree('T:\\User Profile\\My Documents\\PyCharm\\Paranoia', excludes=['xenon.ini','main.spec','.idea']),
               a.binaries,
               a.zipfiles,
               a.datas,
               *([Tree(p) for p in (sdl2.dep_bins + glew.dep_bins)] if sdl2 else []),
               strip=False,
               upx=True,
               name='main',)
