testcfgPath="/home/xiaoju/ENV/canal_test/conf"
basecfgPath="/home/xiaoju/ENV/canal_base/conf"
workPath="/home/xiaoju/ENV/diff_canal/"

function steplog(){
    echo "---------------------"
    echo " $1"
    echo "---------------------"
}
function changeServer0
{
    sed -i 's/port=8506/port=8509/g' $1
}
function changeServer1
{
	sed -i 's/port=8506/port=8508/g' $1
}
function changeConsumerGroup1
{
    sed -i '/dynamic_price_dp_group04/s/dynamic_price_dp_group04/ dynamic_price_dp_test1group04/g' $1
    sed -i '/dynamic_price_group06/s/dynamic_price_group06/ dynamic_price_test1group06/g' $1
    sed -i '/dynamic_price_group05/s/dynamic_price_group05/ dynamic_price_test1group05/g' $1
    sed -i '/dynamic_price_group07/s/dynamic_price_group07/ dynamic_price_test1group07/g' $1
    sed -i '/dynamic_price_group08/s/dynamic_price_group08/ dynamic_price_test1group08/g' $1
    sed -i '/dynamic_price_group09/s/dynamic_price_group09/dynamic_price_test1group09/g' $1
    sed -i '/dynamic_price_group10/s/dynamic_price_group10/ dynamic_price_test1group10/g' $1
    sed -i '/dynamic_discount_group11/s/dynamic_discount_group11/ dynamic_discount_test1group11/g' $1
    sed -i '/dynamic_discount_group12/s/dynamic_discount_group12/ dynamic_discount_test1group12/g' $1



}
function changeConsumerGroup0
{
	sed -i '/dynamic_price_dp_group04/s/dynamic_price_dp_group04/dynamic_price_dp_testgroup04/g' $1
	sed -i '/dynamic_price_group06/s/dynamic_price_group06/dynamic_price_testgroup06/g' $1
	sed -i '/dynamic_price_group05/s/dynamic_price_group05/dynamic_price_testgroup05/g' $1
	sed -i '/dynamic_price_group07/s/dynamic_price_group07/dynamic_price_testgroup07/g' $1
	sed -i '/dynamic_price_group08/s/dynamic_price_group08/dynamic_price_testgroup08/g' $1
	sed -i '/dynamic_price_group09/s/dynamic_price_group09/dynamic_price_testgroup09/g' $1
	sed -i '/dynamic_price_group10/s/dynamic_price_group10/dynamic_price_testgroup10/g' $1
	sed -i '/dynamic_discount_group11/s/dynamic_discount_group11/dynamic_discount_testgroup11/g' $1
	sed -i '/dynamic_discount_group12/s/dynamic_discount_group12/dynamic_discount_testgroup12/g' $1
}
function changeRedis0
{
	sed -i 's/server=.*/server=127.0.0.1:6380/g' $1
}
function changeRedis1
{
	sed -i 's/server=.*/server=127.0.0.1:6381/g' $1
}

function testModify
{
    steplog "CANAL_CHECK_DIFF_BRANCH_CONF_UPDATE"
	changeServer1 $1
	changeConsumerGroup1 $1
	changeRedis1 $1
}
function baseModify
{
    steplog "CANAL_CHECK_DIFF_MASTER_CONF_UPDATE"
    changeServer0 $1
    changeRedis0 $1
    changeConsumerGroup0 $1
}
cd $basecfgPath
baseModify canal.conf
cd $testcfgPath
testModify canal.conf
cd $workPath
