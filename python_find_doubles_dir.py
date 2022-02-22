import os
import datetime
import hashlib

BUF_SIZE = 65536

basepath = 'D:/Documents/Programmation'
basepath = 'D:/Documents/Recettes'
basepath = 'D:\Documents\Ref_Docs'
##basepath = 'D:\Pictures'
basepath = 'D:/'

# list containing all files (with following indexes for each file: 
# 0: file name
# 1: path (including name)
# 2: size
# 3: date last modified
# 4: checksum (optional, for potential doubles)
all_files=[] 

log_f = open("D:/name_doubles.txt", "w")
print('list all files...')
for subdir, dirs, files in os.walk(basepath):
    for file in files:
        filepath = subdir + os.sep + file
        f_stat=os.stat(filepath)
        f_mtime = f_stat.st_mtime
        mtime_str = datetime.datetime.fromtimestamp(f_mtime).strftime('%Y-%m-%d-%H:%M')        
        f_size = f_stat.st_size
        all_files.append([file,filepath,f_size,f_mtime]);
print('done')

# sort list by name
   
print('sort by name...')
all_files.sort()
print('done')

print('list doubles by name...')
f_prev=['','',0,0]
same_list=[]
for f in all_files:
    if (f[0]==f_prev[0]):
        if len(same_list)==0:
            same_list.append(f_prev)
        same_list.append(f)
    elif len(same_list)>0:
        f_same_prev=['','',0,0]
        flag_new=True
        for f_same in same_list:
            if f_same_prev[0]==f_same[0] :
                if flag_new:
                    log_f.write('\n')
                    log_f.write(f_same_prev[1]+'\n')
                    flag_new=False
                log_f.write(f_same[1]+'\n')
            else:
                flag_new=True
            f_same_prev=f_same
        same_list=[]
    f_prev=f
log_f.close()
print('done')



# sort by size and date
def sort_func(file_item):
    return (file_item[2],file_item[3])

log_f = open("D:/true_doubles.txt", "w")
print('sort by size and date')
all_files.sort(key=sort_func)
print('done')
print('list doubles by size and date with same checksum')

f_prev=['','',0,0]
same_list=[]
for f in all_files:
    if (f[2]==f_prev[2]) & (f[3]==f_prev[3]) :
        if len(same_list)==0:
            same_list.append(f_prev)
        same_list.append(f)
    elif len(same_list)>0:
        for f_same in same_list:
            m = hashlib.md5()
            with open(f_same[1], 'rb') as fo: 
                while True:
                    data = fo.read(BUF_SIZE)
                    if not data:
                        break
                    m.update(data)
            f_checksum=m.hexdigest()
            f_same.append(f_checksum)
        same_list.sort(key=lambda x: x[4])

        f_same_prev=['','',0,0,'']
        flag_new=True
        for f_same in same_list:
            if f_same_prev[4]==f_same[4]:
                if flag_new:
                    log_f.write('\n')
                    log_f.write(f_same_prev[1]+'\n')
                    flag_new=False
                log_f.write(f_same[1]+'\n')
            else:
                flag_new=True
            f_same_prev=f_same
            

        same_list=[]
    f_prev=f
print('done')
log_f.close()


              
