'''
=======================================================================
File manager: archive files X days older than now
Usage:

python file_manager.py [-x] [number] [-s] [path] [-d] [path]

-x = xdays -- the number of days older than now for archiving the files,
              e.g. xdays = 30 means files created and last modified on 30
              days ago. default value is 30.

-s = source_folder -- to specify the folder where are files you want to
                      archive from. default value is where this file
                      located.

-d = destination_folder -- the folder you want to store the archived file
                           to. default value is ./archived_files
-h = help -- show the usage manual
-t = test -- it will create some test files and testing the functions

Adding to crontab jobs of running on first day of every month:
    0 0 1 * * python {your_path_to_this_file}/file_manage.py -x {days}
            -s {source_folder} -d {destination_folder}
=======================================================================
'''
import os, sys, time, zipfile, getopt
from datetime import datetime

'''
file_manager implement the function to archive files.
'''
def file_manager(xdays, source_folder, destination_folder):
    try:
        now = time.time()

        # get the timestamp of xdays ago
        time_of_xdays_ago = (now - xdays * 86400)

        try:
            destination_folder = os.path.abspath(destination_folder)
            if not os.path.exists(destination_folder) and not os.path.isdir(destination_folder):
                os.mkdir(destination_folder)
        except:
            # create new one if folder archived_files is not existed
            if not os.path.exists(os.path.join(os.getcwd(),'archived_files')):
                os.mkdir(os.path.join(os.getcwd(),'archived_files'))
                destination_folder = os.path.join(os.getcwd(),'archived_files')

        # build archived file path, which would be a new file under archived_files folder
        date_str = datetime.fromtimestamp(now).strftime('%Y%m%d')
        archived_file_path = os.path.join(destination_folder, "%s.zip" % date_str)

        mode = 'w' # preset the zipfile writing mode
        while True:
            if os.path.exists(archived_file_path):
                print("Archived file existed, do you want to replace it?(Y/N): ")
                if sys.version_info[0] < 3:
                    answer = raw_input()
                else:    
                    answer = input()
                if answer in ['Y', 'y', 'YES', 'yes']:

                    # remove the existed file
                    os.remove(archived_file_path)

                    break
                else:
                    print("Do you wish to add files to that archived file?(Y/N)")
                    if sys.version_info[0] < 3:
                        answer2 = raw_input()
                    else:    
                        answer2 = input()
                    if answer2 in ['Y', 'y', 'YES', 'yes']:
                        """
                        here the zipfile writing mode change to append if user wish to add
                        files to existed archived file.
                        """
                        mode = 'a'
                        break
                    print("Task aborted!")
                    sys.exit() # quit the program if user do not wish to replace existed archived file
            break # continue to process if archived file is not existed

        # create a new zip file
        zipf = zipfile.ZipFile(archived_file_path, mode, zipfile.ZIP_DEFLATED)

        # open the log file to store records
        logfile = open('archive-file-log-%s.log' % date_str, 'a')

        '''
        get the list of all files in specific_folder including files in sub folders,
        and then archiving files and writing logs
        '''
        source_folder = os.path.abspath(source_folder)
        for root, dirs, files in os.walk(source_folder):
            for file in files:

                # here the file is only getting the filename, so we need reform the absolute path of file
                full_file_path = os.path.join(root,file)

                # omitting folder, only archive files, will create folder accordingly when archiving files
                if os.path.isfile(full_file_path):

                    # get the file stats
                    f_stat = os.stat(full_file_path)

                    # here the st_mtime is recently modified time of the file
                    if f_stat.st_mtime < time_of_xdays_ago:

                        """
                        the second argument is for creating sub folders when archiving files, because some files 
                        are under sub folders.
                        """
                        zipf.write(full_file_path, full_file_path.replace(source_folder,''))

                        """
                        writing record to log file, first column is where the file was, second column is
                        the creation time or recently modified time of file, third colomn is where the file
                        has been archived to.
                        """
                        logfile.write("%s    last modified: %s    added to: %s    archived date:%s\n" %
                                      (full_file_path,
                                       datetime.fromtimestamp(f_stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S'),
                                       archived_file_path,
                                       datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')))

                        print("Archived file: %s" % full_file_path)

                        # remove the file after it has been archived
                        os.remove(full_file_path)

        logfile.close()

    except ValueError as ve:
        # the reason to put ValueError here is because ZIP does not support timestamps before 1980,
        # then catch this error.
        print("Task failed because of: \n %s" % str(ve))
    except Exception as e:
        print("Task failed because of: \n %s" % str(e))

# usage function, print out usage doc.
def usage():
    print("""
    =======================================================================
    File manager: archive files X days older than now
    Usage:

    python file_manager.py [-x] [number] [-s] [path] [-d] [path]

    -x = xdays -- the number of days older than now for archiving the files,
                  e.g. xdays = 30 means files created and last modified on 30
                  days ago. default value is 30.

    -s = source_folder -- to specify the folder where are files you want to
                          archive from. default value is where this file
                          located.

    -d = destination_folder -- the folder you want to store the archived file
                               to. default value is ./archived_files
    -h = help -- show the usage manual
    -t = test -- it will create some test files and testing the functions

    Adding to crontab jobs of running on first day of every month:
        0 0 1 * * python {your_path_to_this_file}/file_manage.py -x {days}
                -s {source_folder} -d {destination_folder}
    =======================================================================
    """)


'''
main function to read arguments from terminal and parse them into file_manager
function
'''
def main(argv):
    # default arguments
    xdays = 30
    source_folder = './'
    destination_folder = './archived_files'

    try:
        opts, args = getopt.getopt(argv, "th:x:s:d:", ['xdays=', 'source_folder=', 'destination_folder='])
        if len(opts) == 0:
            usage()
            sys.exit(2)

    except getopt.GetoptError:
        usage()
        sys.exit(2)
    
    for opt, arg in opts:
        if opt in ['-x', '-xdays']:
            xdays = int(arg)
        elif opt in ['-s', '-source_folder']:
            source_folder = arg
        elif opt in ['-d', '-destination_folder']:
            destination_folder = arg
        elif opt == '-h':
            usage()
            sys.exit(2)
        elif opt == '-t':
            """
                for generating test files purpose only
            """
            create_test_files()



    t1 = time.time()
    file_manager(xdays, source_folder, destination_folder)
    t2 = time.time()
    print("finished with time: %f" % (t2 - t1))



'''
=======================================================================
Testing start from here
=======================================================================
'''

'''
Create new file and write the absolute path to the file for testing.
'''
def create_file(filename, path):
    try:
        if not os.path.exists(path):
            os.makedirs(path)
        completed_file_path = '%s%s' % (path, filename)
        if not os.path.isfile(completed_file_path):
            f = open(completed_file_path, 'w')
            f.write(completed_file_path)
            f.close()
        else:
            print("file exists: %s" % completed_file_path)
        return completed_file_path
    except IOError as ioe:
        print("Unable to create file with error:\n%s" % str(ioe))
        return None


'''
Create a brunch of files with specific date for testing the file_manager
program
'''
def create_test_files():
    now = time.time()

    '''
    1 days = 24 hours = 86400 seconds, so range of 20-7000 in here
    means 20 days to 7000 days, it will return a list of time between
    20 days to 7000 days ago.
    '''
    date_list = [(now - d * 86400) for d in range(20, 7000)]

    for date in date_list:
        # return the path of file when create a new test file
        file = create_file("%s.txt" % datetime.fromtimestamp(date).strftime('%Y%m%d'), '%s/%s/' % (os.getcwd(), 'test_files'))
        if file:
            # change the creation time and modification time of test files
            os.utime(file, (date, date))


if __name__ == '__main__':
    main(sys.argv[1:])

