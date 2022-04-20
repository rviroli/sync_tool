import os
import datetime
import hashlib
import shutil
import math

flagExecute = False     # Execute all sync actions without asking
FLAG_DBG =    False     # Debug output
FLAG_PRINT =  True     # List all sync actions 

BUF_SIZE = 65536


## sync_mode = '<>' # contribute (copy and update) both ways
## sync_mode = '>'  # contribute (copy and update) src to dest
## sync_mode = '<'  # contribute (copy and update) dest to src
## sync_mode = '>>' # mirror (copy and update/revert and delete) src to dest
## sync_mode = '<<' # mirror (copy and update/revert and delete) dest to src

##pairs=[
##       ['D:\\Pictures\\2022' , 'F:\\photos\\2022' , '<>'],
##       ['D:\\Pictures\\2021' , 'F:\\photos\\2021' , '<>'],
##       ['D:\\Documents\\Ref_Docs','F:\\Fichiers\\Ref_Docs','>'],
##       ['D:\\Documents\\tmp' , 'F:\\\Fichiers\\_Unsorted' , '>'],
##       ['D:\\Downloads' , 'F:\\\Fichiers\\_Unsorted' , '>'],
##       ['D:\\Documents\\papiers' , 'F:\\\Fichiers\\papiers' , '>'],
##       ['D:\\Documents\\DIY' , 'F:\\\Fichiers\\DIY' , '>'],
##       ['D:\\Documents\\magazines' , 'F:\\books\\magazines' , '>'],
##       ['D:\\Documents\\MAO' , 'F:\\Fichiers\\MAO' , '>'],
##       ['D:\\Documents\\Programmation' , 'F:\\Fichiers\\Programmation' , '>'],
##       ['D:\\Documents\\Recettes' , 'F:\\Fichiers\\recettes' , '>'],
##      ]

pairs=[
       ['F:\\books' , 'E:\\books' , '>>'],
       ['F:\\Fichiers' , 'E:\\Fichiers' , '>>'],
##       ['F:\\Logiciels' , 'E:\\Logiciels' , '>>'],
       ['F:\\photos' , 'E:\\photos' , '>>'],
##       ['F:\\music' , 'E:\\music' , '>>'],
      ]

##pairs=[
##       ['F:\\Fichiers' , 'E:\\Fichiers' , '>>'],
##      ]

##pairs=[
##
##       ['D:\\Documents\\Ref_Docs','F:\\Fichiers\\Ref_Docs','<'],
##       ['D:\\Documents\\papiers' , 'F:\\\Fichiers\\papiers' , '<>'],
##       ['D:\\Documents\\Recettes' , 'F:\\Fichiers\\recettes' , '<>'],
##      ]

ignore_str=['SyncToy' , '_ignored'] # ignore files/path containing this string




for folder_pair in pairs:
    sumCopyL2R=0
    sumCopyR2L=0
    sumUpdtL2R=0
    sumUpdtR2L=0
    sumDeleteL=0
    sumDeleteR=0

    sizeCopyL2R=0
    sizeCopyR2L=0
    sizeUpdtL2R=0
    sizeUpdtR2L=0
    sizeDeleteL=0
    sizeDeleteR=0
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
    # 5: checksum (optional, for potential doubles)
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
            ## mtime_str = datetime.datetime.fromtimestamp(f_mtime).strftime('%Y-%m-%d-%H:%M')        
            f_size = f_stat.st_size
            src_files.append([file,rel_path,filepath,f_size,int(f_mtime)]);

    print('- List all files in destination: '+dest_path)
    for subdir, dirs, files in os.walk(dest_path):
        for file in files:
            rel_path = os.path.relpath(subdir, dest_path) + os.sep + file
            if rel_path[0:2]=='.\\' :
                rel_path=rel_path[2:]    
            filepath = os.path.join(subdir , file)
            f_stat=os.stat(filepath)
            f_mtime = f_stat.st_mtime
            ## mtime_str = datetime.datetime.fromtimestamp(f_mtime).strftime('%Y-%m-%d-%H:%M')        
            f_size = f_stat.st_size
            dest_files.append([file,rel_path,filepath,f_size,int(f_mtime)]);
    
    # sort list by path/name

    print('- Sort by name...')
    src_files.sort(key=lambda x: x[1])
    dest_files.sort(key=lambda x: x[1])

    print('- Compare...')

    src_only_files=[]
    dest_only_files=[]
    both_files=[]
    while True:
        if any(strI in src_files[-1][0] for strI in ignore_str):
            src_files.pop()
        elif any(strI in dest_files[-1][0] for strI in ignore_str):
            dest_files.pop()
        elif (dest_files[-1][1]==src_files[-1][1]):
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

    # Perform sync:

    flagGoOn=True # flag to run the synchronization loop, first run only print, if applicable second run executes the sync
    flagExecute=False

    while flagGoOn:
        flagGoOn=False # if no changes to by synced, the question whether to execute will not be asked
        # Files that are in both folder with same name, same location:
        for f in both_files:
            if (f[0][3]==f[1][3]) & (f[0][4]==f[1][4]):
                if FLAG_DBG:
                    print('== '+f[0][1])
            else:
                if   (sync_mode=='>>') | ((f[0][4]>f[1][4]) &  ((sync_mode=='<>') | (sync_mode=='>'))) :
                    flagGoOn=True # mark that there are changes pending
                    sumUpdtL2R += 1
                    sizeUpdtL2R += f[0][3]
                    if FLAG_PRINT:
                        if (f[0][4]>f[1][4]):
                            dateComparison=' > '
                            dateComment=' (use newer)'
                        else:
                            dateComparison=' < '
                            dateComment=' (use older)'
                        print('>> '+f[0][1]+'\t'+
                            datetime.datetime.fromtimestamp(f[0][4]).strftime('%Y-%m-%d-%H:%M')+dateComparison+
                            datetime.datetime.fromtimestamp(f[1][4]).strftime('%Y-%m-%d-%H:%M')+dateComment)
                    if flagExecute:
                        try:
                            shutil.copy2(f[0][2], f[1][2])
                        except OSError as e:
                            if (f[0][4]>f[1][4]):
                                dateComparison=' > '
                                dateComment=' (use newer)'
                            else:
                                dateComparison=' < '
                                dateComment=' (use older)'
                            print('>> '+f[0][1]+'\t'+
                                datetime.datetime.fromtimestamp(f[0][4]).strftime('%Y-%m-%d-%H:%M')+dateComparison+
                                datetime.datetime.fromtimestamp(f[1][4]).strftime('%Y-%m-%d-%H:%M')+dateComment)
                            print("Error : %s" %  e.strerror)
                elif (sync_mode=='<<') | ((f[0][4]<f[1][4]) & ((sync_mode=='<>') | (sync_mode=='<'))):
                    flagGoOn=True # mark that there are changes pending
                    sumUpdtR2L += 1
                    sizeUpdtR2L += f[1][3]
                    if FLAG_PRINT:
                        if (f[0][4]>f[1][4]):
                            dateComparison=' > '
                            dateComment=' (use older)'
                        else:
                            dateComparison=' < '
                            dateComment=' (use newer)'
                        print('<< '+f[0][1]+'\t'+str(f[0][4])+'\t'+
                            datetime.datetime.fromtimestamp(f[0][4]).strftime('%Y-%m-%d-%H:%M')+dateComparison+
                            datetime.datetime.fromtimestamp(f[1][4]).strftime('%Y-%m-%d-%H:%M')+dateComment)
                    if flagExecute:
                        try:
                            shutil.copy2(f[1][2], f[0][2])
                        except OSError as e:
                            if (f[0][4]>f[1][4]):
                                dateComparison=' > '
                                dateComment=' (use older)'
                            else:
                                dateComparison=' < '
                                dateComment=' (use newer)'
                            print('<< '+f[0][1]+'\t'+str(f[0][4])+'\t'+
                                datetime.datetime.fromtimestamp(f[0][4]).strftime('%Y-%m-%d-%H:%M')+dateComparison+
                                datetime.datetime.fromtimestamp(f[1][4]).strftime('%Y-%m-%d-%H:%M')+dateComment)
                            print("Error : %s" %  e.strerror)

        # Files in destination folder only
        for f in dest_only_files:
            dest=os.path.join(src_path, f[1])
            if (sync_mode=='<>') | (sync_mode=='<') | (sync_mode=='<<'):
                flagGoOn=True # mark that there are changes pending
                sumCopyR2L += 1
                sizeCopyR2L += f[3]
                if FLAG_PRINT:
                    print('<+ '+f[1])
                if flagExecute:
                    try:
                        os.makedirs(os.path.dirname(dest), exist_ok=True)
                        shutil.copy2(f[2], dest)
                    except OSError as e:
                        print('<+ '+f[1])
                        print("Error : %s" %  e.strerror)
            if (sync_mode=='>>') :
                flagGoOn=True # mark that there are changes pending
                sumDeleteR += 1
                sizeDeleteR += f[3]
                if FLAG_PRINT:
                    print('xx '+f[2])
                if flagExecute:
                    try:
                        os.remove(f[2])
                    except OSError as e:
                        print('xx '+f[2])
                        print("Error: %s" % e.strerror)
                        
        # Files in source folder only
        for f in src_only_files:
            dest=os.path.join(dest_path, f[1])
            if (sync_mode=='<>') | (sync_mode=='>') | (sync_mode=='>>'):
                flagGoOn=True # mark that there are changes pending
                sumCopyL2R += 1
                sizeCopyL2R += f[3]
                if FLAG_PRINT:
                    print('+> '+f[1])
                if flagExecute:
                    try:
                        os.makedirs(os.path.dirname(dest), exist_ok=True)
                        shutil.copy2(f[2], dest)
                    except OSError as e:
                        print('+> '+f[1])
                        print("Error : %s" %  e.strerror)
            if (sync_mode=='<<') :
                flagGoOn=True # mark that there are changes pending
                sumDeleteL += 1
                sizeDeleteL += f[3]
                if FLAG_PRINT:
                    print('xx '+f[2])
                if flagExecute:
                    try:
                        os.remove(f[2])
                    except OSError as e:
                        print('xx '+f[2])
                        print("Error: %s : %s" % e.strerror)

        if flagExecute: # sync has just been executed, leave the loop
            flagGoOn=False
            print('- Sync completed\n')
        elif flagGoOn: # some changes are pending
            if sumDeleteL>0:
                print("xx delete left: "+str(sumDeleteL)+" ("+str(math.ceil(sizeDeleteL/1000)/1000)+" MB)")
            if sumDeleteR>0:
                print("xx delete right: "+str(sumDeleteR)+" ("+str(math.ceil(sizeDeleteR/1000)/1000)+" MB)")
            if sumCopyL2R>0:
                print("+> copy from left to right: " + str(sumCopyL2R)+" ("+str(math.ceil(sizeCopyL2R/1000)/1000)+" MB)")
            if sumCopyR2L>0:            
                print("<+ copy from right to left: " + str(sumCopyR2L)+" ("+str(math.ceil(sizeCopyR2L/1000)/1000)+" MB)")
            if sumUpdtL2R>0:
                print(">> update from left to right: "+str(sumUpdtL2R)+" ("+str(math.ceil(sizeUpdtL2R/1000)/1000)+" MB)")
            if sumUpdtR2L>0:
                print("<< update from right to left: "+str(sumUpdtR2L)+" ("+str(math.ceil(sizeUpdtR2L/1000)/1000)+" MB)")
            response=input("Execute synchronization? (yes/no)")
            if response=="yes":
                flagGoOn=True
                flagExecute=True
            else:
                flagGoOn=False
        else:
            print('- Folders are in sync\n')

