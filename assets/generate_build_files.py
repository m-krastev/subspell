#!/usr/bin/env python3
import os
import sys
from datetime import datetime

def generate_manifest(script_dir):
    """Generate the app.manifest file with security and compatibility settings."""
    manifest_content = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<assembly xmlns="urn:schemas-microsoft-com:asm.v1" manifestVersion="1.0">
  <assemblyIdentity
    version="1.0.0.0"
    processorArchitecture="X86"
    name="SubSpell"
    type="win32"
  />
  <description>Subtitle Spelling and Grammar Correction Tool</description>
  <trustInfo xmlns="urn:schemas-microsoft-com:asm.v3">
    <security>
      <requestedPrivileges>
        <requestedExecutionLevel level="asInvoker" uiAccess="false"/>
      </requestedPrivileges>
    </security>
  </trustInfo>
  <compatibility xmlns="urn:schemas-microsoft-com:compatibility.v1">
    <application>
      <!-- Windows 10 and Windows 11 -->
      <supportedOS Id="{8e0f7a12-bfb3-4fe8-b9a5-48fd50a15a9a}"/>
    </application>
  </compatibility>
  <application xmlns="urn:schemas-microsoft-com:asm.v3">
    <windowsSettings>
      <dpiAware xmlns="http://schemas.microsoft.com/SMI/2005/WindowsSettings">true</dpiAware>
      <longPathAware xmlns="http://schemas.microsoft.com/SMI/2016/WindowsSettings">true</longPathAware>
    </windowsSettings>
  </application>
</assembly>"""
    
    manifest_path = os.path.join(script_dir, "app.manifest")
    with open(manifest_path, "w", encoding='utf-8') as f:
        f.write(manifest_content)

def generate_version_info(script_dir):
    """Generate the file_version_info.txt file with version information."""
    current_year = datetime.now().year
    version_info = f"""VSVersionInfo(
  ffi=FixedFileInfo(
    filevers=(1, 0, 0, 0),
    prodvers=(1, 0, 0, 0),
    mask=0x3f,
    flags=0x0,
    OS=0x40004,
    fileType=0x1,
    subtype=0x0,
    date=(0, 0)
  ),
  kids=[
    StringFileInfo(
      [
        StringTable(
          u'040904B0',
          [StringStruct(u'CompanyName', u'mkrastev'),
           StringStruct(u'FileDescription', u'Subtitle Spelling and Grammar Correction Tool'),
           StringStruct(u'FileVersion', u'1.0.0'),
           StringStruct(u'InternalName', u'SubSpell'),
           StringStruct(u'LegalCopyright', u'(c) {current_year} mkrastev'),
           StringStruct(u'OriginalFilename', u'SubSpell.exe'),
           StringStruct(u'ProductName', u'SubSpell'),
           StringStruct(u'ProductVersion', u'1.0.0')])
      ]
    ),
    VarFileInfo([VarStruct(u'Translation', [1033, 1200])])
  ]
)"""
    
    version_info_path = os.path.join(script_dir, "file_version_info.txt")
    with open(version_info_path, "w", encoding='utf-8') as f:
        f.write(version_info)

def generate_spec_file(script_dir):
    """Generate the PyInstaller spec file."""
    spec_content = """# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['../src/subspell/__main__.py'],
    pathex=[],
    binaries=[],
    datas=[('.', 'assets')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='SubSpell',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='icon.ico',
    version='file_version_info.txt',
    manifest='app.manifest'
)"""
    
    spec_path = os.path.join(script_dir, "SubSpell.spec")
    with open(spec_path, "w", encoding='utf-8') as f:
        f.write(spec_content)

def main():
    """Generate all build configuration files."""
    # Get the directory where this script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Check for icon.ico in the same directory as this script
    icon_path = os.path.join(script_dir, "icon.ico")
    if not os.path.exists(icon_path):
        print(f"Error: icon.ico not found at {icon_path}. Please run generate_icon.py first.")
        sys.exit(1)
    
    print("Generating build configuration files...")
    generate_manifest(script_dir)
    generate_version_info(script_dir)
    generate_spec_file(script_dir)
    print("Build configuration files generated successfully!")

if __name__ == "__main__":
    main() 