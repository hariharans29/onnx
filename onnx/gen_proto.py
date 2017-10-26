#!/usr/bin/env python
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import os
import re

autogen_header = """\
//
// WARNING: This file is automatically generated!  Please edit onnx.proto.in.
//


"""

IF_ONNX_ML_REGEX = re.compile(r'\s*//\s*#if\s+ONNX-ML\s*$')
ENDIF_ONNX_ML_REGEX = re.compile(r'\s*//\s*#endif\s*$')

def process_ifs(lines, onnx_ml):
    in_if = False
    for line in lines:
        if IF_ONNX_ML_REGEX.match(line):
            assert not in_if
            in_if = True
        elif ENDIF_ONNX_ML_REGEX.match(line):
            assert in_if
            in_if = False
        else:
            if not in_if or (in_if and onnx_ml):
                yield line

PROTO_SYNTAX_REGEX = re.compile(r'(\s*)syntax\s*=\s*"proto2"\s*;\s*$')
OPTIONAL_REGEX = re.compile(r'(\s*)optional(\s.*)$')

def convert_to_proto3(lines):
    for line in lines:
        # Set the syntax specifier
        m = PROTO_SYNTAX_REGEX.match(line)
        if m:
            yield m.group(1) + 'syntax = "proto3";'
            continue

        # Remove optinoal keywords
        m = OPTIONAL_REGEX.match(line)
        if m:
            yield m.group(1) + m.group(2)
            continue

        yield line

def translate(source, proto, onnx_ml):
    lines = source.splitlines()
    lines = process_ifs(lines, onnx_ml=onnx_ml)
    if proto == 3:
        lines = convert_to_proto3(lines)
    else:
        assert proto == 2
    return "\n".join(lines)  # TODO: not Windows friendly

def main():
    onnx_proto_in = os.path.join(os.path.dirname(__file__), "onnx.proto.in")
    onnx_proto = os.path.join(os.path.dirname(__file__), "onnx.proto")
    onnx_ml_proto = os.path.join(os.path.dirname(__file__), "onnx-ml.proto")
    onnx_proto3 = os.path.join(os.path.dirname(__file__), "onnx.proto3")
    onnx_ml_proto3 = os.path.join(os.path.dirname(__file__), "onnx-ml.proto3")
    with open(onnx_proto_in, 'r') as fin:
        source = fin.read()
        with open(onnx_proto, 'w') as fout:
            fout.write(autogen_header)
            fout.write(translate(source, proto=2, onnx_ml=False))
        with open(onnx_ml_proto, 'w') as fout:
            fout.write(autogen_header)
            fout.write(translate(source, proto=2, onnx_ml=True))
        with open(onnx_proto3, 'w') as fout:
            fout.write(autogen_header)
            fout.write(translate(source, proto=3, onnx_ml=False))
        with open(onnx_ml_proto3, 'w') as fout:
            fout.write(autogen_header)
            fout.write(translate(source, proto=3, onnx_ml=True))

if __name__ == '__main__':
    main()
