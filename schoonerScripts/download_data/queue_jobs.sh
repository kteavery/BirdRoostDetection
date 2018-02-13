#!/bin/bash
## declare an array variable
declare -a arr=("KLCH" "KFCX" "KCRP" "KTBW" "KILN" "KSHV" "KENX" "KVWX"
          "KFWS" "KJGX" "KPBZ" "KLOT" "KHTX" "KDIX" "KJKL" "KLZK"
          "KSJT" "KLVX" "KJAX" "KHPX" "KFFC" "KOKX" "KLSX" "KDVN"
          "KIND" "KEAX" "KDGX" "KMOB" "KLWX" "KDTX" "KBOX" "KDMX"
          "KBMX" "KMXX" "KEVX" "KGWX" "KCAE" "KEOX" "KLIX" "KGSP"
          "KBRO" "KDOX" "KOAX" "KINX" "KVAX" "KBGM" "KBUF" "KMKX"
          "KDLH" "KSRX" "KNQA" "KRAX" "KPOE" "KILX" "KGRR" "KOHX"
          "KAMX" "KPAH" "KTLX" "KMPX" "KICT" "KCLX" "KRLX" "KLTX"
          "KGRB" "KIWX" "KHGX" "KMVX" "KEWX" "KGRK" "KABR" "KFSD"
          "KTLH" "KTWX" "KMHX" "KAKQ" "KSGF" "KCLE" "KTYX" "KDYX"
          "KMRX")

## now loop through the above array
for i in "${arr[@]}"
do
   sbatch download_$i.qsub
# or do whatever with individual element of the array
done