PARSE_DONE=$(maestro task list -u plisboa | grep RUNNING | grep -o -E user\(\\.[-_A-Za-z0-9]+\)+)

echo ${PARSE_DONE}

if [ -z "$PARSE_DONE" ]; then
		echo "No tasks to download, exiting..."
else
		# TODO add check for DONE tasks that already have been downloaded
		# TODO add integrity check (compare # of jobs on cluster with # of jobs downloaded with # of configs)
		cd tasks

		# maestro castor download -d $PARSE_DONE
		# unzip ${PARSE_DONE}.zip -d $PARSE_DONE

		cd ..
fi
