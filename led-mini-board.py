#!/usr/bin/env python3

# Python script to change the messages of "LED Mini Board 5.03"
# Models: B1236, B1248 
# The USB-to-serial chip is PL2303, make sure to have the right permissions.
#
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


import struct
import serial
import sys


SIZES = [0x00, 0x01, 0x03, 0x07, 0x0f, 0x1f, 0x3f, 0x7f, 0xff] # Enable flags for each message

def encode_msg(messages):
    data = b'TABCDE\x00' # Magic header
    message_offset = 0x0600
    for line in messages:
        position = message_offset
        message = line.encode()
        payload = b'\x35\x31\x42' # Modes
        payload += bytes([len(message)]) + message
        payload += b'\x00' * (64*4 - len(payload)) # Padding
        for i in range(0, len(payload), 64):
            frame = b'\x31'
            frame += struct.pack('>h', position) + payload[i:i+64]
            checksum = sum([c for c in frame]) & 0xFF
            data += b'\x02' + frame + bytes([checksum]) # Header and checksum
            position += 0x40 # Add frame len
        message_offset += 0x0100 # Separate message
    data += b'\x02\x33'
    data += bytes([SIZES[len(messages)]])
    
    print(''.join(['%02x ' % c for c in data]))
    return data


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: %s /dev/ttyUSB* <message1> ..." % sys.argv[0])
    else:
        data = encode_msg(sys.argv[2:])

        ser = serial.Serial(sys.argv[1], 38400)
        ser.write(data)
        print("Done.")
