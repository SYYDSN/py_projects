#!/bin/bash
redis-server &
echo 'redis-server started!'
supervisord
echo 'supervisord started!'
echo "88"