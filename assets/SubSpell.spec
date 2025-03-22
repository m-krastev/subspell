# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['../src/subspell/__main__.py'],
    pathex=[],
    binaries=[],
    datas=[('.', 'assets')],
    hiddenimports=['google.genai', 'pysubs2'],
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
    uac_admin=False,
    # Add metadata to help with false positives
    manifest='app.manifest',
    # Add company name and product name
    company_name='mkrastev',
    product_name='SubSpell',
    # Add file description
    file_description='Subtitle Spelling and Grammar Correction Tool',
    # Add copyright
    copyright='© 2024 mkrastev',
    # Add version
    version_info={
        'FileVersion': (0, 0, 2, 0),
        'ProductVersion': (0, 0, 2, 0),
        'FileDescription': 'Subtitle Spelling and Grammar Correction Tool',
        'CompanyName': 'mkrastev',
        'ProductName': 'SubSpell',
        'LegalCopyright': '© 2024 mkrastev',
        'OriginalFilename': 'SubSpell.exe',
        'InternalName': 'SubSpell',
    }
)

app = BUNDLE(
    exe,
    name='SubSpell.app',
    icon='icon.ico',
    bundle_identifier=None,
)
