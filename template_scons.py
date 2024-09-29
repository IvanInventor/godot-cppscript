#!/usr/bin/env python3

import sys

if __name__ == '__main__':
    # Ran as configure script

@PY_EMBED_TEMPLATE_FILES@

@PY_CONFIGURE_SCRIPT@

@PY_EMBED_SRC_FILES@

@CPPSCRIPT_PY_MODULE@

