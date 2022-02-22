import os
import datetime
import hashlib
import shutil


BUF_SIZE = 65536

##src_path = 'D:/Documents/Programmation'
src_path = 'D:/Documents/Recettes/'
##src_path = 'D:\Documents\Ref_Docs'
##src_path = 'D:\Pictures'
##src_path = 'D:/'

dest_path = 'D:/Documents/Recettes_BU/'




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


##print('Load previous...')
##old_backup = []
##with open("D:/old_src.txt", "r", encoding='utf-8') as old_f:
##    for line in old_f:
##        s_line=line.split(";")
##        old_backup.append([s_line[0],int(s_line[1])])
####for f in old_backup:
####    print(f[0]+'\t'+str(f[1]))
##print('done')


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
        print('== '+f[0][1])
    else:
        flag_found=False
##        for old in [x for x in old_backup if x[0]==f[0][1] ]:
##            if (f[0][4]>old[1]) & (f[1][4]>old[1]):
##                print('<> '+f[0][1]+'\t'+str(old[1])+'\t'+str(f[0][4])+'\t'+str(f[1][4]))
##                flag_found=True
##                break
        if not flag_found:
            if f[0][4]>f[1][4] :
                print('>> '+f[0][1]+'\t'+str(f[0][4])+'\t'+str(f[1][4]))
                shutil.copy2(f[0][2], f[1][2])
            else:
                print('<< '+f[0][1]+'\t'+str(f[0][4])+'\t'+str(f[1][4]))
                shutil.copy2(f[1][2], f[0][2])

            


# Files in source folder only
for f in src_only_files:
    dest=os.path.join(dest_path, f[1])
    print(f[2]+' -> '+dest)
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    shutil.copy2(f[2], dest)


# Files in destination folder only
for f in dest_only_files:
    dest=os.path.join(src_path, f[1])
    print(f[2]+' -> '+dest)
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    shutil.copy2(f[2], dest)



### search for moved files with same name, different location/different content
##src_only_files.sort(key=lambda x: x[0])
##dest_only_files.sort(key=lambda x: x[0])
##
##i_s=0
##i_d=0
##i_d_s=0
##potential_moved_name=[]
##while (i_s<len(src_only_files)) & (i_d<len(dest_only_files)):
##    if src_only_files[i_s][0]==dest_only_files[i_d][0]:
##        potential_moved_name.append([src_only_files[i_s],dest_only_files[i_d]])
##        i_d+=1
##    elif src_only_files[i_s][0]>dest_only_files[i_d][0]:
##        i_d+=1
##        i_d_s=i_d
##    else:
##        i_s+=1
##        i_d=i_d_s
##
##for f in potential_moved_name:
##    print('moved (name): \n'+str(f[0])+'\n'+str(f[1]))
##
### search for moved/renamed files with same content, different location
##src_only_files.sort(key=lambda x: (x[3],x[4]))
##dest_only_files.sort(key=lambda x: (x[3],x[4]))
##
##i_s=0
##i_d=0
##i_d_s=0
##potential_moved_cont=[]
##while (i_s<len(src_only_files)) & (i_d<len(dest_only_files)):
##    if (src_only_files[i_s][3]==dest_only_files[i_d][3]): #& (src_only_files[i_s][4]==dest_only_files[i_d][4]):
##        if len(src_only_files[i_s])<6:
##            m = hashlib.md5()
##            with open(src_only_files[i_s][2], 'rb') as fo: 
##                while True:
##                    data = fo.read(BUF_SIZE)
##                    if not data:
##                        break
##                    m.update(data)
##            f_checksum=m.hexdigest()
##            src_only_files[i_s].append(f_checksum)
##        if len(dest_only_files[i_d])<6:
##            m = hashlib.md5()
##            with open(dest_only_files[i_d][2], 'rb') as fo: 
##                while True:
##                    data = fo.read(BUF_SIZE)
##                    if not data:
##                        break
##                    m.update(data)
##            f_checksum=m.hexdigest()
##            dest_only_files[i_d].append(f_checksum)
##
##        potential_moved_cont.append([src_only_files[i_s],dest_only_files[i_d]])
##        i_d+=1
##    elif (src_only_files[i_s][3]>dest_only_files[i_d][3]): #| (src_only_files[i_s][4]>dest_only_files[i_d][4]):
##        i_d+=1
##        i_d_s=i_d
##    else:
##        i_s+=1
##        i_d=i_d_s
##
##for f in potential_moved_cont:
##    if f[0][5]==f[1][5]:
##        print('moved (cont): \n'+str(f[0])+'\n'+str(f[1]))
##    else:
##        print('not moved (cont): \n'+str(f[0])+'\n'+str(f[1]))







##################################################################################################










    
            




##
##
##
### sort list by name
##   
##print('sort by name...')
##src_files.sort()
##dest_files.sort()
##print('done')
##
##print('list doubles by name...')
##f_prev=['','',0,0]
##same_list=[]
##for f in src_files:
##    if (f[0]==f_prev[0]):
##        if len(same_list)==0:
##            same_list.append(f_prev)
##        same_list.append(f)
##    elif len(same_list)>0:
##        f_same_prev=['','',0,0]
##        flag_new=True
##        for f_same in same_list:
##            if f_same_prev[0]==f_same[0] :
##                if flag_new:
##                    log_f.write('\n')
##                    log_f.write(f_same_prev[1]+'\n')
##                    flag_new=False
##                log_f.write(f_same[1]+'\n')
##            else:
##                flag_new=True
##            f_same_prev=f_same
##        same_list=[]
##    f_prev=f
##print('done')
##
##
##
### sort by size and date
##def sort_func(file_item):
##    return (file_item[2],file_item[3])
##
##print('sort by size and date')
##src_files.sort(key=sort_func)
##print('done')
##print('list doubles by size and date with same checksum')
##
##f_prev=['','',0,0]
##same_list=[]
##for f in src_files:
##    if (f[2]==f_prev[2]) & (f[3]==f_prev[3]) :
##        if len(same_list)==0:
##            same_list.append(f_prev)
##        same_list.append(f)
##    elif len(same_list)>0:
##        for f_same in same_list:
##            m = hashlib.md5()
##            with open(f_same[1], 'rb') as fo: 
##                while True:
##                    data = fo.read(BUF_SIZE)
##                    if not data:
##                        break
##                    m.update(data)
##            f_checksum=m.hexdigest()
##            f_same.append(f_checksum)
##        same_list.sort(key=lambda x: x[4])
##
##        f_same_prev=['','',0,0,'']
##        flag_new=True
##        for f_same in same_list:
##            if f_same_prev[4]==f_same[4]:
##                if flag_new:
##                    log_f.write('\n')
##                    log_f.write(f_same_prev[1]+'\n')
##                    flag_new=False
##                log_f.write(f_same[1]+'\n')
##            else:
##                flag_new=True
##            f_same_prev=f_same
##            
##
##        same_list=[]
##    f_prev=f
##print('done')
##log_f.close()
##

              
