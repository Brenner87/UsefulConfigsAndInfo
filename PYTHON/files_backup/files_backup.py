import datetime
import logging
import os
import re
import shutil
import time
import zipfile
from pathlib import PurePath, Path

import yaml

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s",
    handlers=[
        logging.FileHandler("{0}/{1}.log".format('.', os.path.basename(__file__))),
        logging.StreamHandler()
    ])

logger = logging.getLogger()


def create_folder():
    cur_date = datetime.datetime.now().strftime("%Y.%m.%d-%H.%M.%S")
    Path(cur_date).mkdir(exist_ok=True)
#exception could occure while folder creation. Should be handled
    logger.info(f'Folder to backup: {cur_date}')
    return Path(cur_date)


def path_to_name(pth: str):
    st = pth.replace(':\\', '_').replace('\\\\', '_').replace('\\', '_')
    if st[-1] == '_': return st[:-1]
    return st


def timer(f):
    def tmp(*args, **kwargs):
        t = time.time()
        res = f(*args, **kwargs)
#not sure if you really need decorators here, but it's up up you
        logger.info(f'Elapsed time: {time.time() - t} s')
        return res

    return tmp


def divider(f):
    def tmp(*args, **kwargs):
        logger.info('-' * 100)
        res = f(*args, **kwargs)
        logger.info('-' * 100)
        return res

    return tmp


class Backup:
    def __init__(self, config_path):
        self._cfg = yaml.load(open(config_path, 'rt'))
#file opeining always can resultin exception. Should be handeled with 'try' or 'with' statement
#also there can be a typo and yaml format can be corrupted. This should be handeled as well
        self._psw = open(self._cfg['psw_file']).readline() if self._cfg['use_psw'] else None
        self._dst = self._cfg['backup_destination']
        self._date_folder = create_folder()
        self._keep_version = self._cfg['keep_versions']

    @divider
#you use loggings your subroutine. I do not see any reason to use decorator here.
    def do_backup(self):
        if self._cfg['type'] == "zip":
            if len(self._cfg['dir_paths']) > 0:
                logger.info(f"Compressing folders... ({len(self._cfg['dir_paths'])})")
                logger.info('-' * 100)
                for folder in self._cfg['dir_paths']:
                    t = time.time()
                    shutil.make_archive(self._date_folder.joinpath(path_to_name(folder)), 'zip', folder)
   #possible exception should be handeled
                    logger.info(f'{folder:79} (ok) time: {(time.time() - t):.2} s')

            if len(self._cfg['file_paths']) > 0:
                logger.info('-' * 100)
                logger.info(f"Compressing files... ({len(self._cfg['file_paths'])})")
                logger.info('-' * 100)
                for file in self._cfg['file_paths']:
                    t = time.time()
                    file_zip = zipfile.ZipFile(str(self._date_folder.joinpath(path_to_name(file))) + '.zip', 'w')
                    try:
                        file_zip.write(file, arcname=PurePath(file).name, compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)
                    except Exception as e:
                        logger.error(f'{file:79} (Er) time: {(time.time() - t):.2} s')
                        logger.info(e)
                    else:
                        logger.info(f'{file:79} (ok) time: {(time.time() - t):.2} s')
                    finally:
                        file_zip.close()
#you are using many keys which should be in the dict, for example _cfg. But you can't be sure that they are really present.
#you shoul use dict.get(key[, default]) instead of your's dict[key], or you have to run try, except each time you are reffering
#to your dict.
#If you do not do any of above, your script can faile in the middle of backup

    def move_backup(self):
        logger.info('Copying files...')
        shutil.move(str(self._date_folder), self._dst)
#you have to ensure: 
#   1. That parameter exist in your config file
#   2. This folder exist on file system
#   3. You are able to clreate this folde if not exist
# Possible exceptions should be handled
        logger.info('Files copied successfully')

    @divider
    def clean_old(self):
        fld_lst = []
        r = re.compile('\d{4}\\.\d\d\\.\d\d-\d\d\\.\d\d\\.\d\d')
        for fld in list(os.walk(self._dst)):
#you do not need this list()
            if r.match(os.path.basename(fld[0])):
                fld_lst.append(fld[0])
# you could use below construction. But your's is good as well.
# fld_lst=[fld[0] for fld in os.walk(self._dst) if r.match(os.path.basename(fld[0]))]
        fld_lst.sort()
        while len(fld_lst) > self._keep_version:
            try:
                fld_to_delete = fld_lst.pop(0)
                shutil.rmtree(fld_to_delete)
                logger.info(f'Deleted old version: {fld_to_delete} : (ok)')
            except Exception as e:
                logger.info(f'Deleted old version: {fld_to_delete} : (Error)')
                logger.info(e)
#I think it would be more suitable to use logger.error or logger.fatal here


def main():
    backup = Backup('config.yaml')
    backup.do_backup()
    backup.move_backup()
    backup.clean_old()

#big advantage of using main() condtruction is that you can move this part to the top of your program.
#due to this your logic would be in the beginning of the script and subs would be in the end
if __name__ == '__main__': main()
