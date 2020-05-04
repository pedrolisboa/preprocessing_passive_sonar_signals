while [ $# -ge 1 ]; do
        case "$1" in
            -c|--configFile)
                shift
                configFile=$1
                ;;
            -o|--outFile)
                shift
                outFile=$1
                ;;
            -d|--dataFile)
                shift
                dataFile=$1
                ;;
            -h)
                echo "help"
                ;;
        esac
        shift
done

# scriptpath=$(dirname $(readlink -f $BASH_SOURCE))
# cd $scriptpath
# cd ../

echo $(pwd)

docker run \
    -it \
    -v "$(pwd)"/data:/data \
    -v "$(pwd)"/configs:/configs \
    -v "$(pwd)"/models:/models \
    pedrolisboa/theseus:latest \
    python3 create_job.py -c $configFile -o $outFile -d $dataFile
