import os

path = 'download_data/'

if not os.path.exists(path):
    os.makedirs(path)

radars = ['KLCH', 'KFCX', 'KCRP', 'KTBW', 'KILN', 'KSHV', 'KENX', 'KVWX',
          'KFWS', 'KJGX', 'KPBZ', 'KLOT', 'KHTX', 'KDIX', 'KJKL', 'KLZK',
          'KSJT', 'KLVX', 'KJAX', 'KHPX', 'KFFC', 'KOKX', 'KLSX', 'KDVN',
          'KIND', 'KEAX', 'KDGX', 'KMOB', 'KLWX', 'KDTX', 'KBOX', 'KDMX',
          'KBMX', 'KMXX', 'KEVX', 'KGWX', 'KCAE', 'KEOX', 'KLIX', 'KGSP',
          'KBRO', 'KDOX', 'KOAX', 'KINX', 'KVAX', 'KBGM', 'KBUF', 'KMKX',
          'KDLH', 'KSRX', 'KNQA', 'KRAX', 'KPOE', 'KILX', 'KGRR', 'KOHX',
          'KAMX', 'KPAH', 'KTLX', 'KMPX', 'KICT', 'KCLX', 'KRLX', 'KLTX',
          'KGRB', 'KIWX', 'KHGX', 'KMVX', 'KEWX', 'KGRK', 'KABR', 'KFSD',
          'KTLH', 'KTWX', 'KMHX', 'KAKQ', 'KSGF', 'KCLE', 'KTYX', 'KDYX',
          'KMRX']

qsub_job = """#!/bin/csh
#SBATCH -J {0}_download
#SBATCH -o {0}_log.out
#SBATCH -e {0}_log.err
#SBATCH --ntasks=1
#SBATCH --tasks-per-node=1
#SBATCH --exclusive
#SBATCH --mail-user=carmenchilson@ou.edu
#SBATCH --mail-type=ALL
#SBATCH -p swat_plus
#SBATCH -t  12:00:00
#SBATCH -D /home/cchilson/schoonerJobs/download_data/outfiles

set echo

date
python /home/cchilson/gitRepositories/BirdRoostDetection/BirdRoostDetection\
/PrepareData/DownloadData.py \
{0} \
ml_labels.csv \
/condo/swatwork/cchilson/OBS_research
"""

for radar in radars:
    file = open('{0}download_{1}.qsub'.format(path, radar), 'w+')
    file.write(qsub_job.format(radar))
    file.close()
