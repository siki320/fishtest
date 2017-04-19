function dat()
{
	python /home/xiaoju/ENV/dups-price/price-test/mytest/control/main.py "$@"
    echo $?
}
export PYTHONPATH=/home/xiaoju/ENV/dups-price/price-test/:/home/xiaoju/ENV/dups-price/DupsTest/mytest/lib/test_common
export LD_LIBRARY_PATH=/usr/lib:/home/xiaoju/ENV/dups-price/price-test/frame/tools/python27/lib:$LD_LIBRARY_PATH
export LANG=en_US
export LC_ALL=en_US
