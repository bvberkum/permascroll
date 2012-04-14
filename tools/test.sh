#!/bin/sh

# TODO: daemonize server
ADDRESS=iris.dennenweg
PORT=8083
NUM="$1"
PREFIX="/tmp/permascroll$NUM"
PID="/tmp/permascroll.$PORT"

if test -z "$1"; then
    while $0 $((++i)); do true; done
    exit 0
fi

# XXX: could not figure out a way to make wget save (headers) for non 200
#if which wget > /dev/null; then
#  function download
#  {
#    echo Downloading $2 $1
#    if test -e $PREFIX.$2; then
#      WGETARGS="-c"
#    fi
#    wget --save-headers -O $PREFIX.$2 $1 $WGETARGS
#    #1>&2
#    splitheaders $2
#  }
#el
if which curl > /dev/null; then
  function download
  {
    test -e "$PREFIX.$2" && rm $PREFIX.$2
    echo Downloading $2 $1
    if test -e $PREFIX.$2; then
      CURLARGS="-C -"
    fi
    curl -s -S -i -o $PREFIX.$2 $CURLARGS $1 1>&2
    splitheaders $2
  }
else
  echo "error: no download tool available, install curl"
  exit 1
fi

function check
{
  printf " * %-67s %5s %s\n" "$1" "$2" "$3"
}

function check_exists
{
  if test -e $PREFIX.$2; then
    check "$1" PASSED
  else
    check "$1" ERROR
  fi
}

function check_headers
{
  if grep -q "$3" $PREFIX.$1.headers; then
    check "$2" PASSED
  else
    check "$2" ERROR
  fi
}

function sortheaders
{
    mv $1 $1.tmp
    sort $1.tmp > $1
    rm $1.tmp
}

function splitheaders
{
    for f in $PREFIX.$1.entity.headers $PREFIX.$1.headers;
    do [ -e "$f" ] && rm $f; done
    mv $PREFIX.$1 $PREFIX.tmp
    ENVELOPE=$(head -n 1 $PREFIX.tmp)
    HEADERS_RECEIVED=$([ "${ENVELOPE:0:7}" = "HTTP/1." ] && echo 0 || echo 1)
    LINE=0
    if [ $HEADERS_RECEIVED = 0 ]
    then
        while read L
        do
            LINE=$(($LINE + 1))
            if [ $LINE = 1 ]
            then
                # dot not want to compare statusline b/c protocol version
                echo $L > $PREFIX.$1.headers
                continue
            fi
            if [ "$L" = "$(printf '\r\n')" ]; then
                break
            fi
            STRIP=$(echo $L | grep -v '^\(Connection\|Accept-\|P3P\|Via\|X-\|Cache-\|Date\|Expires\)')
            if [ -n "$STRIP" ]
            then
                # Keep entity headers for comparison
                echo $L >> $PREFIX.$1.entity.headers
            fi
            # Keep all headers for other checks
            echo $L >> $PREFIX.$1.headers
        done < $PREFIX.tmp
    fi
    LINE=$(($LINE + 1))
    # rest of lines is message contents
    tail -n +$LINE $PREFIX.tmp > $PREFIX.$1

    [ -e $PREFIX.$1.headers ] && sortheaders $PREFIX.$1.headers
    [ -e $PREFIX.$1.entity.headers ] && sortheaders $PREFIX.$1.entity.headers

    [ -e $PREFIX.tmp ] && rm $PREFIX.tmp
}


function coveragereport
{
    [ -z "$COVERAGE_PROCESS_START" ] && return
    echo Generating coverage report
    coverage combine
    coverage html
}

set -m
case $1 in
  1)
    download http://$ADDRESS:$PORT/ out
    check_exists "downloaded headers" out.headers
    check_headers out "served redirect" "^HTTP\/1\..\ 301\ .*$"
    check_headers out.entity "served redirect location" "^Location:\ .*/frontpage"

    ;;
  2)
    download http://$ADDRESS:$PORT/frontpage out
    #check_entity out ""
    check_headers out "served HTTP v1.* OK" "HTTP/1.. 200 "

    ;;
  3)
    download http://$ADDRESS:$PORT/node/1 out
    check_headers out "served HTTP v1.* OK" "HTTP/1.. 200 "

    ;;
  4)
    download http://$ADDRESS:$PORT/node/1.1/1 out1
    check_headers out1 "served HTTP v1.* OK" "HTTP/1.. 200 "
    download http://$ADDRESS:$PORT/node/1.1.0.1 out2
    check_headers out2 "served HTTP v1.* OK" "HTTP/1.. 200 "

    ;;
  5)
    download http://$ADDRESS:$PORT/node/1.1/1/1 out1
    check_headers out1 "served HTTP v1.* OK" "HTTP/1.. 200 "
    download http://$ADDRESS:$PORT/node/1.1.0.1.0.1 out2
    check_headers out2 "served HTTP v1.* OK" "HTTP/1.. 200 "

    ;;
  6)
    download http://$ADDRESS:$PORT/node/1.1/1/1/1 out1
    check_headers out1 "served HTTP 4xx error" "HTTP/1..\ 4.. "
    download http://$ADDRESS:$PORT/node/1.1.0.1.0.1.0.1 out2
    check_headers out2 "served HTTP 4xx error" "HTTP/1..\ 4.. "

    ;;
  7)
    download http://$ADDRESS:$PORT/node/1.1/1/1/1 out1
    check_headers out1 "served HTTP 4xx error" "HTTP/1..\ 4.. "

    ;;
#  11)
#    coveragereport
#    ;;
  *)
    exit 1
    ;;
esac

exit 0
# vim:sw=2:ts=2:et:

