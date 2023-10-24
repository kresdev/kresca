from binascii import hexlify
import sys

import numpy as np
import estraces
from rainbow.generics import rainbow_arm
from rainbow import TraceConfig, HammingWeight
from tqdm import tqdm

e = rainbow_arm(trace_config=TraceConfig(register=HammingWeight()))
e.load("aes.elf", typ=".elf")
e.setup()

def aes_encrypt(key, plaintext):
    e.reset()
    
    key_addr = 0xDEAD0000
    e[key_addr] = key.tobytes()

    # AES_128_keyschedule(key)
    e["r0"] = key_addr
    e.start(e.functions["AES128_ECB_indp_setkey"] | 1, 0)

    buf_in = 0xDEAD2000
    buf_out = 0xDEAD3000
    e[buf_in] = plaintext.tobytes()
    e[buf_out] = b"\x00" * 16  # Need to do this so this buffer is mapped into unicorn

    # AES_128_encrypt(rk, buf_in, buf_out)
    e["r0"] = buf_in
    e["r1"] = buf_out
    # e.trace_reset()
    e.start(e.functions["AES128_ECB_indp_crypto"] | 1, 0)

    # Hamming weight + noise to pretend we're on a real target
    trace = np.array([event["register"] for event in e.trace]) + np.random.normal(
        0, 1.0, (len(e.trace))
    )
    return trace, np.frombuffer(e[buf_out:buf_out+16], dtype='uint8')

outfile = estraces.ETSWriter('../../../Traces/ETS/TinyAES_1k.ets', overwrite=True)

total = 1000

key = np.array([0x00, 0x11, 0x22, 0x33, 0x44, 0x55, 0x66, 0x77, 0x88, 0x99, 0xaa, 0xbb, 0xcc, 0xdd, 0xee, 0xff], dtype='uint8')

for i in tqdm(range(total)):
    plaintext = np.random.randint(0, 256, (16,), np.uint8)
    trace, ciphertext = aes_encrypt(key, plaintext)
    outfile.write_samples(trace, index=i)
    outfile.write_meta('plaintext', plaintext, index=i)
    outfile.write_meta('key', key, index=i)
    outfile.write_meta('ciphertext', ciphertext, index=i)
    
outfile.close()