#!/usr/bin/env python3

# Turn hideous XML into less-hideous line-by-line XML fragments
# https://wiki.openstreetmap.org/wiki/OSM_XML
# Typical invocation:
# pv ../planet-latest.osm.bz2 | bzcat | ../disassemble-osm.py | split -C1000M -d -a 4 --additional-suffix='.xml' --filter='gzip > $FILE.gz' - osm-planet-


import sys
from lxml import etree


def main(instream, outstream):
    # based on https://stackoverflow.com/a/35309644
    parser = etree.iterparse(instream, events=['start', 'end'], remove_blank_text=True)    
    _, root = next(parser) # consume root element
    record_nesting_level = 0
    root.clear()
    del root
    
    for event, elem in parser:
        if event == 'start': 
            record_nesting_level += 1
        elif event == 'end':
            record_nesting_level -= 1
            if record_nesting_level != 0:
                continue

            xml = etree.tostring(elem).strip()
            assert b'\n' not in xml
            outstream.write(xml)
            outstream.write(b'\n')
            
            # don't leak memory, per https://stackoverflow.com/a/9814580
            elem.clear()
            while elem.getprevious() is not None:
                del elem.getparent()[0]


main(sys.stdin.buffer, sys.stdout.buffer)
