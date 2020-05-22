#!/usr/bin/env python3

import pefile
pe = pefile.PE("test.exe")
features = [('IMAGE_DLLCHARACTERISTICS_HIGH_ENTROPY_VA', 0x0020),
            ('IMAGE_DLLCHARACTERISTICS_DYNAMIC_BASE', 0x0040),
            ('IMAGE_DLLCHARACTERISTICS_FORCE_INTEGRITY', 0x0080),
            ('IMAGE_DLLCHARACTERISTICS_NX_COMPAT', 0x0100),
            ('IMAGE_DLLCHARACTERISTICS_NO_ISOLATION', 0x0200),
            ('IMAGE_DLLCHARACTERISTICS_NO_SEH', 0x0400),
            ('IMAGE_DLLCHARACTERISTICS_NO_BIND', 0x0800),
            ('IMAGE_DLLCHARACTERISTICS_APPCONTAINER', 0x1000),
            ('IMAGE_DLLCHARACTERISTICS_GUARD_CF', 0x4000),
            ]
for s, h in features:
    print("{}: {}".format(s, bool(pe.OPTIONAL_HEADER.DllCharacteristics & h)))
