#!/bin/sh
init_nodes()
{
    # Below POSTs create new nodes by appending one at an address,
    # starting at a zero-width 'root' for each component. 

    # Create first nodes for components for Node, Directory, Entry
    curl $CURL/node/ -X POST -F title="Docuverse I"
    curl $CURL/node/ -X POST -F title="Docuverse II"
    curl $CURL/node/ -X POST -F title="Docuverse III"
    curl $CURL/node/1 -X POST -F title="Node 1.1"
    curl $CURL/node/1 -X POST -F title="Node 1.2"
    curl $CURL/node/1 -X POST -F title="Node 1.3"
    curl $CURL/node/1 -X POST -F title="Node 1.4"
    curl $CURL/node/1 -X POST -F title="Node 1.5"
    curl $CURL/node/1.1 -X POST -F title="Node 1.1.1"
    curl $CURL/node/1.2 -X POST -F title="Node 1.2.1"
    curl $CURL/node/1.2 -X POST -F title="Node 1.2.2"
    curl $CURL/node/1.2 -X POST -F title="Node 1.2.3"
    curl $CURL/node/1.2 -X POST -F title="Node 1.2.4"
    curl $CURL/node/1.3 -X POST -F title="Node 1.3.1"
    curl $CURL/node/1.3 -X POST -F title="Node 1.3.2"
    curl $CURL/node/1.3 -X POST -F title="Node 1.3.3"
    curl $CURL/node/2 -X POST -F title="Node 2.1"
    curl $CURL/node/2.1 -X POST -F title="Node 2.1.1"
    curl $CURL/node/2.1.1 -X POST -F title="Node 2.1.1.1"
    curl $CURL/node/1.1/ -X POST -F title="Account 1.1/1"
    #curl $CURL/node/1.1/ -X POST -F none=""
    #curl $CURL/node/1.1/ -X POST -H "Content-Length: 0"
    #curl $CURL/node/1.1/1/ -F data="Hier eet dit maar dan."
    #curl $CURL/node/1.1/1/ -d @2010/08/11/permascroll.init.edl
    #curl $CURL/node/1.1/1/ -F data="`cat 2010/08/11/permascroll.linkdoc.edl`"
    #curl $CURL/node/1.1/1/ -F data="`cat test.data`"
    #curl $CURL/node/1.1/1/ -F data=@2010/08/11/permascroll.linkdoc.edl;type=text/x-edl

    # dnde - 'dandy' tree layout?
    echo
}

test()
{
    #curl $CURL"/.test/1.1/1.2.3+0.4.2" -v;
    #curl $CURL"/node/1.2.3" 
    curl $CURL"/node/1+1.1.1.2" 
    echo
    echo
    curl $CURL"/node/1.1+1.1.1.2" 
    #curl $CURL"/content/1.1.0.1.0.1.0.1.1~0.180" -v;
    #echo
    #curl $CURL/node/3 -F none="";
    #echo
    #curl $CURL/node/ -F title="Foo"
    #echo
    #curl $CURL/node/7
    return

    curl $CURL/node/3 -X POST -F none="" 
    curl $CURL/node/3.2 -X POST -F none="" 
    curl $CURL/node/3.2 -X POST -F none="" 
    curl $CURL/node/3.2.1 -X POST -F none="" 
    curl $CURL/node/3.2.1 -X POST -F none="" 
    curl $CURL/node/3.2.1 -X POST -F none="" 
    curl $CURL/node/3.2.1 -X POST -F none="" 
    curl $CURL/node/3.2.1.4 -X POST -F none="" 

    curl $CURL/node/3.2.1.4/ -X POST -F none="" 
    curl $CURL/node/3.2.1.4/ -X POST -F none="" 
    curl $CURL/node/3.2.1.4/2 -X POST -F none="" 
    curl $CURL/node/3.2.1.4/2 -X POST -F none="" 
    curl $CURL/node/3.2.1.4/2 -X POST -F none="" 
    curl $CURL/node/3.2.1.4/2 -X POST -F none="" 
    curl $CURL/node/3.2.1.4/2.4 -X POST -F none="" 
    curl $CURL/node/3.2.1.4/2.4 -X POST -F none="" 
    curl $CURL/node/3.2.1.4/2.4.2/ -X POST -F none="" 
    curl $CURL/node/3.2.1.4/2.4.2/ -X POST -F none="" 
    curl $CURL/node/3.2.1.4/2.4.2/2 -X POST -F none="" 
    curl $CURL/node/3.2.1.4/2.4.2/2 -X POST -F none="" 
    curl $CURL/node/3.2.1.4/2.4.2/2.2 -X POST -F none="" 
    curl $CURL/node/3.2.1.4/2.4.2/2.2 -X POST -F none="" 

    # Note: the last component below, 1 does not represent a node instance but
    # rather a more abstract 'virtual type'. After appending data 
    
    # For the Docuverse.Node/Directory/Entry tree the following are recognized:
    # 1. literal
    # 2. link
    # 3. image
    curl $CURL/node/3.2.1.4/2.4.2/2.2.2/ -F type=literal -F data="My test data! Keep it"

    curl $CURL/node/3.2.1.4/2.4.2/2.2.2/ -F data="Aargh.. forgot some"
    curl $CURL/node/3.2.1.4/2.4.2/2.2.2/ -F data="Nah better make that forgot something"
    curl $CURL/node/3.2.1.4/2.4.2/2.2.2/ -F data="You know, this is interesting too. "
    curl $CURL/node/3.2.1.4/2.4.2/2.2.2/ -F data="Oh well, more to do. "
    curl $CURL/node/3.2.1.4/2.4.2/2.2.2/ -F data="And more.. "
    curl $CURL/node/3.2.1.4/2.4.2/2.2.2/ -F data="Hey found something.. hmmm. "
    curl $CURL/node/3.2.1.4/2.4.2/2.2.2/ -F data="Ok that was not so interesting. "


}
#CURL_=" -L http://permascroll.appspot.com"
#CURL_=" --trace-ascii - "
CURL_=" -L http://localhost:8083"
CURL=" --fail -o /dev/null "$CURL_
CURL=$CURL_
#init_nodes
test
