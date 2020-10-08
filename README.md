# Beacon monitoring agent

This agent will run on each of the compute nodes as a daemon and 
will periodically report to monitoring server with relevant system information.

## Installation 
```shell script
sudo apt install python3-pip
git clone https://github.com/Ormly/ParallelNano_Lisa_Beacon_Agent.git
cd ParallelNano_Lisa_Beacon_Agent
python3 setup install --user
``` 

## Usage
```shell script
cd ParallelNano_Lisa_Beacon_Agent/beacon
python3 beacon.py
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

Agent should be restarted to apply changes to config file

## Beacon format
System information sent as part of the beacon is a [pickled](https://docs.python.org/3.6/library/pickle.html) dictionary with the following structure
```json
{
  "platform": "type of platform",
  "system": "system type",
  "cpu": "type of CPU",
  "cpu_usage": "CPU usage in percentage",
  "mem_usage": "RAM usage in percentage"
}
```