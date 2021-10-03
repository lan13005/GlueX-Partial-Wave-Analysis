if [ "$#" -ne 1 ]; then
    echo "ramdisk.sh did not receive a valid argument"
    exit 1
fi

rm -f $1
rm -rf /dev/shm/$1
mkdir /dev/shm/$1
ln -s /dev/shm/$1 $1
