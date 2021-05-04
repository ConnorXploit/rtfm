#!/bin/bash
(cd rtfm/rtfm; flask run -h 0.0.0.0 -p 8010) &
nginx -g "daemon off;"