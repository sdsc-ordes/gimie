#!/bin/sh

set -e

# If the first argument starts with "-" or if it is not recognized as a command,
# use "gimie" as command
if [ -z "${1##-*}" ] || [ -z "$(command -v $1)" ] ; then 
	set -- gimie "$@"
fi

exec "$@"
