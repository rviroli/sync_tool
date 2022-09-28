import os
import datetime
import hashlib
import shutil
import math

FLAG_DBG =    False     # Debug output
FLAG_PRINT =  True      # List all sync actions 
FLAG_MATCH =  True      # Search for moved/renamed files
BUF_SIZE = 65536


## sync_mode = '<>' # contribute (copy and update) both ways
## sync_mode = '>'  # contribute (copy and update) src to dest
## sync_mode = '<'  # contribute (copy and update) dest to src
## sync_mode = '>>' # mirror (copy and update/revert and delete) src to dest
## sync_mode = '<<' # mirror (copy and update/revert and delete) dest to src

pairs=[
       ['D:\\Pictures\\2022' , 'F:\\photos\\2022' , '>'],
##       ['D:\\Pictures\\2021' , 'F:\\photos\\2021' , '<>'],
       ['D:\\Documents\\Ref_Docs','F:\\Fichiers\\Ref_Docs','<>'],
##       ['D:\\Documents\\tmp' , 'F:\\\Fichiers\\_Unsorted' , '>'],
##       ['D:\\Downloads' , 'F:\\\Fichiers\\_Unsorted' , '>'],
       ['D:\\Documents\\papiers' , 'F:\\\Fichiers\\papiers' , '<>'],
       ['D:\\Documents\\DIY' , 'F:\\\Fichiers\\DIY' , '>'],
##       ['D:\\Documents\\magazines' , 'F:\\books\\magazines' , '>'],
       ['D:\\Documents\\MAO' , 'F:\\Fichiers\\MAO' , '>'],
       ['D:\\Documents\\Programmation' , 'F:\\Fichiers\\Programmation' , '>'],
##       ['D:\\Documents\\Recettes' , 'F:\\Fichiers\\recettes' , '>'],
      ]
##pairs=[
##       ['F:\\Fichiers\\Ref_Docs','F:\\_Ref_Docs_arch','<>'],
##    ]
##pairs=[
##       ['F:\\books' , 'E:\\books' , '>>'],
##       ['F:\\Fichiers' , 'E:\\Fichiers' , '>>'],
##       ['F:\\Logiciels' , 'E:\\Logiciels' , '>>'],
##       ['F:\\photos' , 'E:\\photos' , '>>'],
##       ['F:\\music' , 'E:\\music' , '>>'],
##      ]

##pairs=[
##       ['F:\\Fichiers\\Ref_Docs' , 'E:\\Fichiers\\Ref_Docs' , '>>'],
##      ]

##pairs=[
##
##       ['D:\\Documents\\Ref_Docs','F:\\Fichiers\\Ref_Docs','<'],
##       ['D:\\Documents\\papiers' , 'F:\\\Fichiers\\papiers' , '<>'],
##       ['D:\\Documents\\Recettes' , 'F:\\Fichiers\\recettes' , '<>'],
##      ]

##BU_path='G:\\MemoryZone\\Backup\\'
##pairs=[
##       [BU_path+'Photos\\WhatsApp\\Media\\WhatsApp Images' , 'F:\\photos\\Mobile\\WhatsApp Images' , '>'],
##      ]


#pairs=[
 #       ['F:\\Fichiers\\Ref_Docs_w2022\\Aerospace' , 'D:\\Documents\\Ref_Docs\\Engineering\\Aerospace' , '>'],
        #['F:\\Fichiers\\Ref_Docs_w2022\\General_eng' , 'D:\\Documents\\Ref_Docs\\Engineering\\General_eng' , '>'],
        #['F:\\Fichiers\\Ref_Docs_w2022\\math' , 'D:\\Documents\\Ref_Docs\\Engineering\\math' , '>'],
 #     ]

ignore_str=['SyncToy' , '_ignored'] # ignore files/path containing this string




sum_copy_L2R=0
sum_copy_R2L=0
sum_update_L2R=0
sum_update_R2L=0
sum_delete_L=0
sum_delete_R=0
sum_move_L=0
sum_move_R=0

size_copy_L2R=0
size_copy_R2L=0
size_update_L2R=0
size_update_R2L=0
size_delete_L=0
size_delete_R=0
size_move_L=0
size_move_R=0

execute_copy=[]   # List of files to copy: 0=source, 1=destination, 2=sync comment
execute_move=[]   # List of files to move: 0=source, 1=destination, 2=sync comment
execute_remove=[] # List of files to remove: 0=source, 1=sync comment

for folder_pair in pairs:
    src_path = folder_pair[0]
    dest_path = folder_pair[1]
    sync_mode = folder_pair[2]

    src_path=src_path.replace('/','\\')
    dest_path=dest_path.replace('/','\\')

    # list containing all files (with following indexes for each file: 
    # 0: file name
    # 1: relative path (including name)
    # 2: absolute path (including name)
    # 3: size
    # 4: date last modified
    # 5: date change
    # 6: checksum (optional, for potential doubles)
    src_files=[]
    dest_files=[] 

    print('- List all files in source: '+src_path)
    for subdir, dirs, files in os.walk(src_path):
        for file in files:
            rel_path = os.path.relpath(subdir, src_path) + os.sep + file
            if rel_path[0:2]=='.\\' :
                rel_path=rel_path[2:]        
            filepath = os.path.join(subdir , file)
            f_stat=os.stat(filepath)
            f_mtime = f_stat.st_mtime
            f_ctime = f_stat.st_ctime
            ## mtime_str = datetime.datetime.fromtimestamp(f_mtime).strftime('%Y-%m-%d-%H:%M')        
            f_size = f_stat.st_size
            src_files.append([file,rel_path,filepath,f_size,int(f_mtime),int(f_ctime)]);

    print('- List all files in destination: '+dest_path)
    for subdir, dirs, files in os.walk(dest_path):
        for file in files:
            rel_path = os.path.relpath(subdir, dest_path) + os.sep + file
            if rel_path[0:2]=='.\\' :
                rel_path=rel_path[2:]    
            filepath = os.path.join(subdir , file)
            f_stat=os.stat(filepath)
            f_mtime = f_stat.st_mtime
            f_ctime = f_stat.st_ctime
            ## mtime_str = datetime.datetime.fromtimestamp(f_mtime).strftime('%Y-%m-%d-%H:%M')        
            f_size = f_stat.st_size
            dest_files.append([file,rel_path,filepath,f_size,int(f_mtime),int(f_ctime)]);
    
    # sort list by path/name

    print('- Sort by name...')
    src_files.sort(key=lambda x: x[1])
    dest_files.sort(key=lambda x: x[1])

    print('- Compare...')

    src_only_files=[]
    dest_only_files=[]
    both_files=[]
    
    while True:
        if any(ign_str in src_files[-1][1] for ign_str in ignore_str):
            src_files.pop()
        elif any(ign_str in dest_files[-1][1] for ign_str in ignore_str):
            dest_files.pop()
        elif (dest_files[-1][1]==src_files[-1][1]):
    ##        print('A and B: '+dest_files[-1][1])
            both_files.append([src_files[-1] , dest_files[-1] ])
            dest_files.pop()
            src_files.pop()
        elif (dest_files[-1][1]>=src_files[-1][1]):
##            print('B only: '+dest_files[-1][1])
            dest_only_files.append(dest_files[-1])
            dest_files.pop()
        else:
##            print('A only: '+src_files[-1][1])
            src_only_files.append(src_files[-1])
            src_files.pop()
            
        if (len(src_files)<1):
            while len(dest_files)>0:
                if any(ign_str in dest_files[-1][1] for ign_str in ignore_str):
                    dest_files.pop()
                else:
##                print('B only: '+dest_files[-1][1])
                    dest_only_files.append(dest_files[-1])
                    dest_files.pop()
            break
        elif (len(dest_files)<1):
            while len(src_files)>0:
                if any(ign_str in src_files[-1][1] for ign_str in ignore_str):
                    src_files.pop()
                else:
##                print('A only: '+src_files[-1][1])
                    src_only_files.append(src_files[-1])
                    src_files.pop()
            break


        
    # try to find matching files (with different names/locations) but same content
    if FLAG_MATCH: # @todo: Add flag
        print('- Finding matching files...')
        src_only_files.sort(key=lambda x: x[3], reverse=True)
        dest_only_files.sort(key=lambda x: x[3], reverse=False)

        moved_files=[]
        left_only_files=[]
        right_only_files=[]
        if len(dest_only_files)>0:
            while True:
                if ((len(src_only_files)<1) | (len(dest_only_files)<1)):
                    src_only_files=left_only_files + src_only_files
                    dest_only_files=right_only_files + dest_only_files
                    break
                f=src_only_files[-1]
    ##            print('f '+f[0]+' '+str(f[3]))
                j_min=-1
                for j, g in enumerate(dest_only_files):
    ##                print('g '+g[0]+' '+str(g[3]))
                    if (f[3] > g[3]):
                        j_min=j
                    elif (f[3] == g[3]):
    ##                    print('double candidate: \n'+f[2]+' '+str(f[4])+' '+str(f[5])+'\n'+g[2]+' '+str(g[4])+' '+str(g[5]))
                        if (True | (f[4] == g[4])): # @todo: Add flag
                            if len(f)<7:
                                m = hashlib.md5()
                                with open(f[2], 'rb') as fo: 
                                    while True:
                                        data = fo.read(BUF_SIZE)
                                        if not data:
                                            break
                                        m.update(data)
                                f_checksum=m.hexdigest()
                                f.append(f_checksum)
                            if len(g)<7:
                                m = hashlib.md5()
                                with open(g[2], 'rb') as fo: 
                                    while True:
                                        data = fo.read(BUF_SIZE)
                                        if not data:
                                            break
                                        m.update(data)
                                g_checksum=m.hexdigest()
                                g.append(g_checksum)
                                dest_only_files[j]=g
                            if (f[6]==g[6]):
    ##                            print('double found: \n'+f[2]+'\n'+g[2])
                                moved_files.append([f,g])
                                src_only_files.pop()
                                del dest_only_files[j]
                                break
                            else:
                                left_only_files.append(f)
                                src_only_files.pop()
                                break
                    elif (f[3] < g[3]):
                        left_only_files.append(f)
                        src_only_files.pop()
                        break
                if j_min>=0:
                    for k in range(0,j_min+1):
                        right_only_files.append(dest_only_files.pop(0))
                        

    
    
    # Perform sync:
    print('- Synchronization')
    # Files that are in both folder with same name, same location:
    for f in both_files:
        if (f[0][3]==f[1][3]) & (f[0][4]==f[1][4]):
            if FLAG_DBG:
                print('== '+f[0][1])
        else:
            if   (sync_mode=='>>') | ((f[0][4]>f[1][4]) &  ((sync_mode=='<>') | (sync_mode=='>'))) :
                sum_update_L2R += 1
                size_update_L2R += f[0][3]
                if (f[0][4]>f[1][4]):
                    dateComparison=' > '
                    dateComment=' (use newer)'
                else:
                    dateComparison=' < '
                    dateComment=' (use older)'
                log_message=('>> '+f[0][2]+'\t'+
                    datetime.datetime.fromtimestamp(f[0][4]).strftime('%Y-%m-%d-%H:%M')+dateComparison+
                    datetime.datetime.fromtimestamp(f[1][4]).strftime('%Y-%m-%d-%H:%M')+dateComment)
                execute_copy.append([f[0][2], f[1][2],log_message])
                if FLAG_PRINT:
                    print(log_message)
            elif (sync_mode=='<<') | ((f[0][4]<f[1][4]) & ((sync_mode=='<>') | (sync_mode=='<'))):
                sum_update_R2L += 1
                size_update_R2L += f[1][3]
                
                if (f[0][4]>f[1][4]):
                    dateComparison=' > '
                    dateComment=' (use older)'
                else:
                    dateComparison=' < '
                    dateComment=' (use newer)'
                log_message=('<< '+f[1][2]+'\t'+str(f[0][4])+'\t'+
                    datetime.datetime.fromtimestamp(f[0][4]).strftime('%Y-%m-%d-%H:%M')+dateComparison+
                    datetime.datetime.fromtimestamp(f[1][4]).strftime('%Y-%m-%d-%H:%M')+dateComment)
                execute_copy.append([f[1][2], f[0][2],log_message])
                if FLAG_PRINT:
                    print(log_message)


    # Files moved/renamed
    for f in moved_files:
        if (sync_mode=='>>') | ((f[0][5]>f[1][5]) &  ((sync_mode=='<>') | (sync_mode=='>'))) :
            sum_move_R += 1
            size_move_R += f[0][3]
            if (f[0][5]>f[1][5]):
                dateComparison=' > '
                dateComment=' (use newer)'
            else:
                dateComparison=' < '
                dateComment=' (use older)'
            root_path=f[1][2][0:(f[1][2].find(f[1][1]))]
            dest=root_path+f[0][1]
            (os.path.dirname(file[1]))
            log_message=('#* '+f[0][2]+'\n## '+f[1][2]+'\n   '+
                datetime.datetime.fromtimestamp(f[0][5]).strftime('%Y-%m-%d-%H:%M')+dateComparison+
                datetime.datetime.fromtimestamp(f[1][5]).strftime('%Y-%m-%d-%H:%M')+dateComment)+'\n > '+dest
            execute_move.append([f[1][2],dest,log_message])
            if FLAG_PRINT:
                print(log_message)
        elif (sync_mode=='<<') | ((f[0][5]<f[1][5]) &  ((sync_mode=='<>') | (sync_mode=='<'))) :
            sum_move_L += 1
            size_move_L += f[0][3]
            if (f[0][5]>f[1][5]):
                dateComparison=' > '
                dateComment=' (use newer)'
            else:
                dateComparison=' < '
                dateComment=' (use older)'
            root_path=f[0][2][0:(f[0][2].find(f[0][1]))]
            dest=root_path+f[1][1]
            log_message=('## '+f[0][2]+'\n#* '+f[1][2]+'\n   '+
                datetime.datetime.fromtimestamp(f[0][5]).strftime('%Y-%m-%d-%H:%M')+dateComparison+
                datetime.datetime.fromtimestamp(f[1][5]).strftime('%Y-%m-%d-%H:%M')+dateComment)+'\n < '+dest
            execute_move.append([f[0][2],dest,log_message])
            if FLAG_PRINT:
                print(log_message)
        else:
            log_message=('Moved file not treated '+f[0][2]+'\t'+f[1][2])
            print(log_message)

    
    # Files in destination folder only
    for f in dest_only_files:
        dest=os.path.join(src_path, f[1])
        if (sync_mode=='<>') | (sync_mode=='<') | (sync_mode=='<<'):
            sum_copy_R2L += 1
            size_copy_R2L += f[3]
            log_message=('<+ '+f[2]+' ('+str(math.ceil(f[3]/1000)/1000)+' MB)')
            execute_copy.append([f[2], dest, log_message])
            if FLAG_PRINT:
                print(log_message)
        if (sync_mode=='>>'):
            sum_delete_R += 1
            size_delete_R += f[3]
            log_message=('xx '+f[2]+' ('+str(math.ceil(f[3]/1000)/1000)+' MB)')
            execute_remove.append([f[2], log_message])
            if FLAG_PRINT:
                print(log_message)
                    
    # Files in source folder only
    for f in src_only_files:
        dest=os.path.join(dest_path, f[1])
        if (sync_mode=='<>') | (sync_mode=='>') | (sync_mode=='>>'):
            sum_copy_L2R += 1
            size_copy_L2R += f[3]
            log_message=('+> '+f[2]+' ('+str(math.ceil(f[3]/1000)/1000)+' MB)')
            execute_copy.append([f[2], dest, log_message])
            if FLAG_PRINT:
                print(log_message)
        if (sync_mode=='<<'):
            sum_delete_L += 1
            size_delete_L += f[3]
            log_message=('xx '+f[2]+' ('+str(math.ceil(f[3]/1000)/1000)+' MB)')
            execute_remove.append([f[2], log_message])
            if FLAG_PRINT:
                print(log_message)

flag_changes=False # flag set when changes are found between source and destination folder pairs
if sum_delete_L>0:
    flag_changes=True
    print('xx delete left: '+str(sum_delete_L)+' ('+str(math.ceil(size_delete_L/1000)/1000)+' MB)')
if sum_delete_R>0:
    flag_changes=True
    print('xx delete right: '+str(sum_delete_R)+' ('+str(math.ceil(size_delete_R/1000)/1000)+' MB)')
if sum_move_L>0:
    flag_changes=True
    print('## move/rename left: '+str(sum_move_L)+' ('+str(math.ceil(size_move_L/1000)/1000)+' MB)')
if sum_move_R>0:
    flag_changes=True
    print('## move/rename right: '+str(sum_move_R)+' ('+str(math.ceil(size_move_R/1000)/1000)+' MB)')
if sum_copy_L2R>0:
    flag_changes=True
    print('+> copy from left to right: ' + str(sum_copy_L2R)+' ('+str(math.ceil(size_copy_L2R/1000)/1000)+' MB)')
if sum_copy_R2L>0:
    flag_changes=True
    print('<+ copy from right to left: ' + str(sum_copy_R2L)+' ('+str(math.ceil(size_copy_R2L/1000)/1000)+' MB)')
if sum_update_L2R>0:
    flag_changes=True
    print('>> update from left to right: '+str(sum_update_L2R)+' ('+str(math.ceil(size_update_L2R/1000)/1000)+' MB)')
if sum_update_R2L>0:
    flag_changes=True
    print('<< update from right to left: '+str(sum_update_R2L)+' ('+str(math.ceil(size_update_R2L/1000)/1000)+' MB)')
    
if flag_changes:
    response=input('- Execute synchronization? (yes/no)')
    if response=='yes':
        print('- Executing synchronization')
        flag_errors=False
        for file in execute_remove:
            try:
                os.remove(file[0])
            except OSError as e:
                flag_errors=True
                print(file[1])
                print('Error: %s' % e.strerror)
        for file in execute_copy:
            try:
                os.makedirs(os.path.dirname(file[1]), exist_ok=True)
                shutil.copy2(file[0], file[1])
            except OSError as e:
                flag_errors=True
                print(file[2])
                print('Error: %s' % e.strerror)
        for file in execute_move:
            try:
                os.makedirs(os.path.dirname(file[1]), exist_ok=True)
                shutil.move(file[0], file[1])
            except OSError as e:
                flag_errors=True
                print(file[2])
                print('Error: %s' % e.strerror)
        if flag_errors:
            print('Synchronization executed, with errors')
        else:
            print('Synchronization successful, folders are in sync')
    else:
        print('Synchronization not executed')
else:
    print('No changes pending, folders are in sync')

