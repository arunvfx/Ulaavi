import clique
import os
import sys
import time

st = time.time()

collections, remainder = clique.assemble(os.listdir('C:/Users/arunv/OneDrive/Desktop/footages/image_seq'),
                                         case_sensitive=sys.platform not in ('win32', 'darwin'))

for c in collections:
    print(c)

print(remainder)
print(remainder)

print(time.time() - st)