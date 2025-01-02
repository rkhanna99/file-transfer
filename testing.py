import rawpy

with rawpy.imread('/Volumes/NO NAME/RAFs/DSCF1539.RAF') as raw:
    print(raw.metadata.datetime)  # Check if metadata contains a date
