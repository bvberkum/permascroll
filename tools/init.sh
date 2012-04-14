#!/bin/sh
init_nodes()
{
    # Below POSTs create new nodes by appending one at an address,
    # starting at a zero-width 'root' for each component. 

    # Create first nodes for components for Node, Directory, Entry
    $CURL/node/ -X POST -F title="Docuverse I"
    $CURL/node/ -X POST -F title="Docuverse II"
    $CURL/node/ -X POST -F title="Docuverse III"
    $CURL/node/1 -X POST -F title="Node 1.1"
    $CURL/node/1 -X POST -F title="Node 1.2"
    $CURL/node/1 -X POST -F title="Node 1.3"
    $CURL/node/1 -X POST -F title="Node 1.4"
    $CURL/node/1 -X POST -F title="Node 1.5"
    $CURL/node/1.1 -X POST -F title="Node 1.1.1"
    $CURL/node/1.2 -X POST -F title="Node 1.2.1"
    $CURL/node/1.2 -X POST -F title="Node 1.2.2"
    $CURL/node/1.2 -X POST -F title="Node 1.2.3"
    $CURL/node/1.2 -X POST -F title="Node 1.2.4"
    $CURL/node/1.3 -X POST -F title="Node 1.3.1"
    $CURL/node/1.3 -X POST -F title="Node 1.3.2"
    $CURL/node/1.3 -X POST -F title="Node 1.3.3"
    $CURL/node/2 -X POST -F title="Node 2.1"
    $CURL/node/2.1 -X POST -F title="Node 2.1.1"
    $CURL/node/2.1.1 -X POST -F title="Node 2.1.1.1"
    $CURL/node/1.1/ -X POST -F title="Directory 1.1/1"
    $CURL/node/1.1/ -X POST -F title="Directory 1.1/2"
    $CURL/node/1.1/ -X POST -F title="Directory 1.1/3"
    $CURL/node/1.1/1 -X POST -F title="Directory 1.1/1.1"
    $CURL/node/1.1/1 -X POST -F title="Directory 1.1/1.2"
    $CURL/node/1.1/1 -X POST -F title="Directory 1.1/1.3"
    $CURL/node/1.1/2 -X POST -F title="Directory 1.1/2.1"
    $CURL/node/1.1/3 -X POST -F title="Directory 1.1/3.1"
    $CURL/node/1.1/3 -X POST -F title="Directory 1.1/3.2"
    $CURL/node/1.1/3 -X POST -F title="Directory 1.1/3.3"
    #$CURL/node/1.1/ -X POST
    #$CURL/node/1.1/ -F none=""
    #$CURL/node/1.1/ -X POST -H "Content-Length: 0"
}
init_entries()
{
    $CURL/node/1.1/1/ -X POST -F title="System Home Document"
    $CURL/node/1.1/1/ -X POST -F title="System Home Document" -F data="Welcome at permascroll"

    echo "\n***\n"
    #$CURL/node/1.1/2.1/20 -X POST -F title="Entry 1.1/2.1/1" -F data="Entry body"
    echo "\n***\n"
    $CURL/node/1.1/2.1/ -X POST -F title="Entry 1.1/2.1/2" \
        -F "data=@2010/08/11/permascroll.linkdoc.edl;type=text/x-pedl"

    # Havent seen this work, see UploadHandler
    #$CURL/upload/1.1/2.1/ -X POST -F title="Entry 1.1/2.1/2" \
    #    -F "data=@2010/08/11/permascroll.linkdoc.edl;type=text/x-pedl" \
    #    -F "blob-key=linkdoc"
    return
    #echo "\n***\n"
    #$CURL/node/1.1/2.1/ -X POST -F title="Entry 1.1/2.1/3" -F data="Entry body"
    echo "\n***\n"
    $CURL/node/1.1/2.1/ -X POST -F title="Entry 1.1/2.1/4" \
        -d @2010/08/11/permascroll.linkdoc.edl;type=text/x-edl

    return

    $CURL/node/1.1/2.1/1
    $CURL/node/1.1/2.1/2
    $CURL/node/1.1/2.1/3

    return

    #curl $CURL/node/1.1/1/ -F title="System Home Document" -d @2010/08/11/permascroll.init.edl
    #curl $CURL/node/1.1/1/ -F title="System Link Document" -d @2010/08/11/permascroll.linkdoc.edl
    $CURL/node/1.1/1/ \
        -F title="System Link Document" \
        -F data=@2010/08/11/permascroll.linkdoc.edl;type=text/x-edl
    #curl $CURL/node/1.1/1/ -F data="`cat 2010/08/11/permascroll.linkdoc.edl`"

    # dnde - 'dandy' tree layout?
    echo
}
test()
{
    #$CURL"/.test/1.1/1.2.3+0.4.2" -v;
    #$CURL"/node/1.2.3" 
    $CURL"/node/1+1.1.1.2" 
    echo
    echo
    $CURL"/node/1.1+1.1.1.2" 
    #curl $CURL"/content/1.1.0.1.0.1.0.1.1~0.180" -v;
    #echo
    #curl $CURL/node/3 -F none="";
    #echo
    #curl $CURL/node/ -F title="Foo"
    #echo
    $CURL/node/3/
    $CURL/node/1.1/1
    $CURL/node/1.1/1/1
    $CURL/content/1.1/1/1
}
CURL=" --trace-ascii - "
#CURL=$CURL" -L http://permascroll.appspot.com"
#CURL=$CURL" -L http://localhost:8083"
#hostname | read ADDR
ADDR=`hostname`
echo ADDR=$ADDR
CURL=$CURL" -L http://$ADDR:8083"
CURL=" --fail "$CURL
#CURL="-o /dev/null "$CURL
CURL="curl "$CURL
init_nodes
init_entries
#test


