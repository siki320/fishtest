diff_env=/home/xiaoju/ENV/diff_canal
echo "$diff_env/case/"
case $1 in
    "get_feature_count")
        python $diff_env/case/$1/get_feature_count_iscarpool.py
        python $diff_env/case/$1/get_feature_count_taxiabnormal.py
        ;;
    "get_range")
        python $diff_env/case/$1/$1.py
        ;;
    "get_discount")
        python $diff_env/case/$1/$1.py
        ;;
    "get_time_info")
        python $diff_env/case/$1/$1.py
        ;;
    "all")
        python $diff_env/case/get_feature_count/get_feature_count_iscarpool.py
        sleep 2
        python $diff_env/case/get_feature_count/get_feature_count_taxiabnormal.py  
        sleep 2
        python $diff_env/case/get_range/get_range.py  
        sleep 2
        python $diff_env/case/get_discount/get_discount.py  
        sleep 2
        python $diff_env/case/get_timeinfo/get_timeinfo.py  
        ;;
    *)
        echo "your choice wrong"
        ;;
    esac
