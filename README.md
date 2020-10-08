# Beacon monitoring agent

This agent will run on each of the compute nodes as a daemon and 
will periodically report to monitoring server with relevant system information.

## Dependencies 
* python3 
* psutil - https://pypi.org/project/psutil/
* python-daemon - https://pypi.org/project/python-daemon/
 
## Usage
* Clone repository
* Install all dependencies
* run ```beacon.py```

```shell script
python3 /path/to/beacon.py
```

To kill daemon:

```shell script
$ ps -ef | grep beacon
mario       4481    1720  3 10:38 ?        00:00:00 python beacon.py
$ kill 4481
```

## Configuration
Agent is configured using the ```config.json``` file residing in the same library.

```json
{
  "server_ip": "127.0.0.1", 
  "server_port": 4444,
  "interval": 1.0
}
```
* ```service_ip``` - ip of the system controller
* ```server_port``` - port of the beacon server component
* ```interval``` - seconds two wait before sending the next beacon 

## Beacon format
System information sent as part of the beacon is a pickled dictionary with the following structure
```json
{
  "platform": "type of platform",
  "system": "system type",
  "cpu": "type of CPU",
  "cpu_usage": "CPU usage in percentage",
  "mem_usage": "RAM usage in percentage"
}
```