import os
import datetime
import hashlib
import shutil

FLAG_EXECUTE = False
FLAG_DBG = False
FLAG_PRINT = True

SYNC_MODE = '<>' # copy and update both ways
##SYNC_MODE = '>' # copy and update src to dest
##SYNC_MODE = '<' # copy and update dest to src

BUF_SIZE = 65536

##src_path = 'D:\\Documents\\Ref_Docs'
##dest_path = 'F:\\Fichiers\\Ref_Docs'

src_path = 'D:\\Pictures\\2022'
dest_path = 'F:\\photos\\2022'


src_path=src_path.replace('/','\\')
dest_path=dest_path.replace('/','\\')

# list containing all files (with following indexes for each file: 
# 0: file name
# 1: relative path (including name)
# 2: absolute path (including name)
# 3: size
# 4: date last modified
# 5: checksum (optional, for potential doubles)
src_files=[]
dest_files=[] 

log_f = open("D:/sync.txt", "w")
print('list all files in source...')
for subdir, dirs, files in os.walk(src_path):
    for file in files:
        rel_path = os.path.relpath(subdir, src_path) + os.sep + file
        if rel_path[0:2]=='.\\' :
            rel_path=rel_path[2:]        
        filepath = os.path.join(subdir , file)
        f_stat=os.stat(filepath)
        f_mtime = f_stat.st_mtime
        mtime_str = datetime.datetime.fromtimestamp(f_mtime).strftime('%Y-%m-%d-%H:%M')        
        f_size = f_stat.st_size
        src_files.append([file,rel_path,filepath,f_size,int(f_mtime)]);
print('done')

print('list all files in destination...')
for subdir, dirs, files in os.walk(dest_path):
    for file in files:
        rel_path = os.path.relpath(subdir, dest_path) + os.sep + file
        if rel_path[0:2]=='.\\' :
            rel_path=rel_path[2:]    
        filepath = os.path.join(subdir , file)
        f_stat=os.stat(filepath)
        f_mtime = f_stat.st_mtime
        mtime_str = datetime.datetime.fromtimestamp(f_mtime).strftime('%Y-%m-%d-%H:%M')        
        f_size = f_stat.st_size
        dest_files.append([file,rel_path,filepath,f_size,int(f_mtime)]);
print('done')

# sort list by path/name

print('sort by name...')
src_files.sort(key=lambda x: x[1])
dest_files.sort(key=lambda x: x[1])


print('done')
print('Store...')
with open("D:/src.txt", "w", encoding='utf-8') as log_f:
    for f in src_files:
        log_f.write(f[1]+';'+str(f[4])+'\n')
with open("D:/dest.txt", "w", encoding='utf-8') as log_f:
    for f in dest_files:
        log_f.write(f[1]+';'+str(f[4])+'\n')

print('done')


print('Comparing...')

src_only_files=[]
dest_only_files=[]
both_files=[]
while True:
    if (dest_files[-1][1]==src_files[-1][1]):
##        print('A and B: '+dest_files[-1][1])
        both_files.append([src_files[-1] , dest_files[-1] ])
        dest_files.pop()
        src_files.pop()
    elif (dest_files[-1][1]>=src_files[-1][1]):
##        print('B only: '+dest_files[-1][1])
        dest_only_files.append(dest_files[-1])
        dest_files.pop()
    else:
##        print('A only: '+src_files[-1][1])
        src_only_files.append(src_files[-1])
        src_files.pop()
        
    if (len(src_files)<1):
        while len(dest_files)>0:
##            print('B only: '+dest_files[-1][1])
            dest_only_files.append(dest_files[-1])
            dest_files.pop()
        break
    elif (len(dest_files)<1):
        while len(src_files)>0:
##            print('A only: '+src_files[-1][1])
            src_only_files.append(src_files[-1])
            src_files.pop()
        break

print('done')

# Files that are in both folder with same name, same location:

for f in both_files:
    if (f[0][3]==f[1][3]) & (f[0][4]==f[1][4]):
        if FLAG_DBG:
            print('== '+f[0][1])
    else:
        if (f[0][4]>f[1][4]) & ( (SYNC_MODE=='<>') | (SYNC_MODE=='>') ):
            if FLAG_PRINT:
                print('>> '+f[0][1]+'\t'+str(f[0][4])+'\t'+str(f[1][4]))
            if FLAG_EXECUTE:
                shutil.copy2(f[0][2], f[1][2])
        elif (SYNC_MODE=='<>') | (SYNC_MODE=='<'):
            if FLAG_PRINT:
                print('<< '+f[0][1]+'\t'+str(f[0][4])+'\t'+str(f[1][4]))
            if FLAG_EXECUTE:
                shutil.copy2(f[1][2], f[0][2])

            


if (SYNC_MODE=='<>') | (SYNC_MODE=='>'):
# Files in source folder only
    for f in src_only_files:
        dest=os.path.join(dest_path, f[1])
        if FLAG_PRINT:
            print(' -> '+f[1])
        if FLAG_EXECUTE:
            os.makedirs(os.path.dirname(dest), exist_ok=True)
            shutil.copy2(f[2], dest)


if (SYNC_MODE=='<>') | (SYNC_MODE=='<'):
# Files in destination folder only
    for f in dest_only_files:
        dest=os.path.join(src_path, f[1])
        if FLAG_PRINT:
            print(' <- '+f[1])
        if FLAG_EXECUTE:
            os.makedirs(os.path.dirname(dest), exist_ok=True)
            shutil.copy2(f[2], dest)

