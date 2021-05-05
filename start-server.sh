#!/bin/bash
cd rtfm
export FLASK_APP=rtfm
(flask run -h 0.0.0.0 -p 8010) &
nginx -g "daemon off;"