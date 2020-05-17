#!/bin/bash
yesterday=$(date +'%Y%m%d' --date='1 day ago')
yesterdayy=$(date +'%Y-%m-%d' --date='1 day ago')
cd /home/admin/jasp/gasp/scripts/usee && /home/admin/jasp/pypenv/bin/python obs_to_txt_nc.py /home/admin/jasp/srm --day $yesterdayy --user diaryobs
cd /home/admin/jasp/gasp/scripts/usee && /home/admin/jasp/pypenv/bin/python obs_to_txt_nc.py /home/admin/jasp/nc --netcdf --day $yesterdayy --user diaryobs

# FTP DIR
year=$(date +'%Y' --date='1 day ago')
month=$(date +'%Y' --date='1 day ago')
NCYDIR="/home/diaryobs/ftp/nc/$year"
NCMDIR="/home/diaryobs/ftp/nc/$year/$month"
SRYDIR="/home/diaryobs/ftp/srm/$year"
SRMDIR="/home/diaryobs/ftp/srm/$year/$month"
if [ ! -d "$NCYDIR" ]; then
    sudo mkdir $NCYDIR
fi
if [ ! -d "$NCMDIR" ]; then
    sudo mkdir $NCMDIR
fi
if [ ! -d "$SRYDIR" ]; then
    sudo mkdir $SRYDIR
fi
if [ ! -d "$SRMDIR" ]; then
    sudo mkdir $SRMDIR
fi
sudo mv ~/jasp/nc/IR_TS_FB_TTDAFUNDO_$yesterday.nc $NCMDIR
sudo mv ~/jasp/srm/IR_TS_FB_TTDAFUNDO_$yesterday.srm $SRMDIR
