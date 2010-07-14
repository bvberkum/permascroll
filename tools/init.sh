#!/bin/sh
init_nodes()
{
    #curl $CURL/node/ -F title="Docuverse I"
    #curl $CURL/node/ -F title="Docuverse II"
    #curl $CURL/node/ -F title="Docuverse III"

    #curl $CURL/node/1 -F title="Docuverse I - I"
    #curl $CURL/node/1 -F title="Docuverse I - II"
    #curl $CURL/node/1 -F title="Docuverse I - III"
    #curl $CURL/node/1 -F title="Docuverse I - IV"

    #curl $CURL/node/ -X POST
    #curl $CURL/node/ -X POST
    #curl $CURL/node/ -X POST
    #curl $CURL/node/3 -X POST
    #curl $CURL/node/3 -X POST
    #curl $CURL/node/3.2 -X POST
    #curl $CURL/node/3.2 -X POST
    #curl $CURL/node/3.2.1 -X POST
    #curl $CURL/node/3.2.1 -X POST
    #curl $CURL/node/3.2.1 -X POST
    #curl $CURL/node/3.2.1 -X POST
    #curl $CURL/node/3.2.1.4 -X POST

    #curl $CURL/node/3.2.1.4/ -X POST
    #curl $CURL/node/3.2.1.4/ -X POST
    #curl $CURL/node/3.2.1.4/2 -X POST
    #curl $CURL/node/3.2.1.4/2 -X POST
    #curl $CURL/node/3.2.1.4/2 -X POST
    #curl $CURL/node/3.2.1.4/2 -X POST
    #curl $CURL/node/3.2.1.4/2.4 -X POST
    #curl $CURL/node/3.2.1.4/2.4 -X POST
    #curl $CURL/node/3.2.1.4/2.4.2/ -X POST
    #curl $CURL/node/3.2.1.4/2.4.2/ -X POST
    #curl $CURL/node/3.2.1.4/2.4.2/2 -X POST
    #curl $CURL/node/3.2.1.4/2.4.2/2 -X POST
    #curl $CURL/node/3.2.1.4/2.4.2/2.2 -X POST
    #curl $CURL/node/3.2.1.4/2.4.2/2.2 -X POST
    #curl $CURL/node/3.2.1.4/2.4.2/2.2.2 -X POST

    curl $CURL/node/3.2.1.4/2.4.2/2.2.2/ -F data="My test data! Keep it"
    #curl $CURL/node/3.2.1.4/2.4.2/2.2.2/1 -F data="Ah forgot something"
    #curl $CURL/node/3.2.1.4/2.4.2/2.2.2/1 -F data="Nah better make that forgot something"
    #curl $CURL/node/3.2.1.4/2.4.2/2.2.2/1.2 -F data="You know, this is interesting too. "
    #curl $CURL/node/3.2.1.4/2.4.2/2.2.2/ -F data="Oh well, more to do. "
    #curl $CURL/node/3.2.1.4/2.4.2/2.2.2/ -F data="And more.. "
    #curl $CURL/node/3.2.1.4/2.4.2/2.2.2/ -F data="Hey found something.. hmmm. "
    #curl $CURL/node/3.2.1.4/2.4.2/2.2.2/4 -F data="Oh that was not so interesting, doe have a look at this shiny thing though.  "
    
    #curl $CURL/node/1/1 -F title="Another channel"
    #curl $CURL/node/1/1.1 -F title="Etc.."
    #curl $CURL/node/1/1/ -F title="My first entry"
    #curl $CURL/node/1/1/1/ -F data="My first contents"
    # gives
    #curl $CURL/node/ -> 1:Node(0~0.1), 2:Node(0~0.1)
    #curl $CURL/node/1/ -> 1:Channel(0~0.1)
    #curl $CURL/node/1/1/ -> 1:Entry(0~0.1)
    #curl $CURL/node/1/1/1/ -> 1:VStr(0~0.31)
    #curl $CURL/node/1/1/1/1(~0.10) -> "bladieblah"

    #curl $CURL/node/1.1 -F title="My first channel"
    #curl $CURL/node/1.1.1/ -F title="first"
    #curl $CURL/node/1.1.1/ -F title="second"
    #curl $CURL/node/1.1.1/ -F title="third"
    #curl $CURL/node/1.1.1/ -F title="fourth"

    #curl $CURL/node/1 -F title="Channel I - I"
    #curl $CURL/node/1 -F title="Channel I - II"
    #curl $CURL/node/1.2 -F title="Channel I - II - I"
    #curl $CURL/node/1.2 -F title="Channel I - II - II"
    #curl $CURL/node/1.2 -F title="Channel I - II - III"
    #curl $CURL/node/ -F title="Docuverse II"
    #curl $CURL/node/ -F title="Docuverse III"
    #curl $CURL/node/ -F title="Docuverse IV"
    #curl $CURL/node/2 -F title="Channel II - I"
    #curl $CURL/node/2 -F title="Channel II - II"
    #curl $CURL/node/2 -F title="Channel II - III"
    #curl $CURL/node/2.2 -F title="Channel II - II - I"
    #curl $CURL/node/2.2 -F title="Channel II - II - II"
    #curl $CURL/node/2.2 -F title="Channel II - II - III"
}
CURL_=" -L http://localhost:8080"
CURL=" --fail -o /dev/null "$CURL_
init_nodes