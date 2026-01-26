# Data Retrieval

## Get Devices

URL: https://<api-gateway-id>.execute-api.eu-central-1.amazonaws.com/prod/v1/devices
Example Response:

```json
[
    {
        "deviceId": "<device-id-1>",
        "gtin": "4031602012043",
        "type": "rbg",
        "backend": "qbeyond",
        "backendDeviceId": "<backend-device-id-1>",
        "identityId": "<identity-id>",
        "oem": "Moehlenhoff",
        "createdAt": "2026-01-23T10:07:57.644Z",
        "status": "CLAIMED",
        "groupId": "<group-id-1>",
        "homeId": "<home-id>"
    },
    {
        "deviceId": "<device-id-2>",
        "gtin": "4031602012043",
        "type": "rbg",
        "backend": "qbeyond",
        "backendDeviceId": "<backend-device-id-2>",
        "identityId": "<identity-id>",
        "oem": "Moehlenhoff",
        "createdAt": "2026-01-22T08:32:58.768Z",
        "status": "CLAIMED",
        "groupId": "<group-id-2>",
        "homeId": "<home-id>"
    },
    {
        "deviceId": "<device-id-3>",
        "gtin": "4031602012043",
        "type": "rbg",
        "backend": "qbeyond",
        "backendDeviceId": "<backend-device-id-3>",
        "identityId": "<identity-id>",
        "oem": "Moehlenhoff",
        "createdAt": "2026-01-23T10:14:08.020Z",
        "status": "CLAIMED",
        "groupId": "<group-id-3>",
        "homeId": "<home-id>"
    },
    {
        "deviceId": "<device-id-4>",
        "gtin": "4031602012005",
        "type": "basis",
        "backend": "qbeyond",
        "backendDeviceId": "<backend-device-id-4>",
        "identityId": "<identity-id>",
        "oem": "Moehlenhoff",
        "createdAt": "2026-01-22T08:31:01.764Z",
        "status": "CLAIMED",
        "groupId": "<group-id-default>",
        "homeId": "<home-id>"
    },
    {
        "deviceId": "<device-id-5>",
        "gtin": "4031602011923",
        "type": "gateway",
        "backend": "qbeyond",
        "backendDeviceId": "<backend-device-id-5>",
        "identityId": "<identity-id>",
        "oem": "Moehlenhoff",
        "createdAt": "2026-01-22T08:29:02.868Z",
        "status": "CLAIMED",
        "groupId": "<group-id-default>",
        "homeId": "<home-id>"
    },
    {
        "deviceId": "<device-id-6>",
        "gtin": "4031602012043",
        "type": "rbg",
        "backend": "qbeyond",
        "backendDeviceId": "<backend-device-id-6>",
        "identityId": "<identity-id>",
        "oem": "Moehlenhoff",
        "createdAt": "2026-01-23T10:17:39.989Z",
        "status": "CLAIMED",
        "groupId": "<group-id-4>",
        "homeId": "<home-id>"
    },
    {
        "deviceId": "<device-id-7>",
        "gtin": "4031602012043",
        "type": "rbg",
        "backend": "qbeyond",
        "backendDeviceId": "<backend-device-id-7>",
        "identityId": "<identity-id>",
        "oem": "Moehlenhoff",
        "createdAt": "2026-01-23T10:23:04.850Z",
        "status": "CLAIMED",
        "groupId": "<group-id-2>",
        "homeId": "<home-id>"
    },
    {
        "deviceId": "<device-id-8>",
        "gtin": "smartphone-apple",
        "type": "smartphone",
        "backend": "smartphone",
        "backendDeviceId": "<backend-device-id-8>",
        "identityId": "<identity-id>",
        "oem": "apple",
        "createdAt": "2026-01-20T17:56:27.277Z",
        "status": "CLAIMED"
    }
]
```
## Get Homes

URL: https://<api-gateway-id>.execute-api.eu-central-1.amazonaws.com/prod/v1/homes
Example Response:

```json
[
    {
        "groups": [
            {
                "name": "Bedroom",
                "icon": "bedroom_01",
                "subGroups": [],
                "deviceIds": [
                    "<device-id-9>"
                ],
                "id": "<group-id-1>"
            },
            {
                "name": "Bathroom",
                "icon": "bathroom_02",
                "subGroups": [],
                "deviceIds": [
                    "<device-id-7>"
                ],
                "id": "<group-id-2>"
            },
            {
                "name": "Kitchen",
                "icon": "kitchen_02",
                "subGroups": [],
                "deviceIds": [
                    "<device-id-6>"
                ],
                "id": "<group-id-4>"
            },
            {
                "name": "Dining Room",
                "icon": "kitchen_01",
                "subGroups": [],
                "deviceIds": [
                    "<device-id-10>"
                ],
                "id": "<group-id-5>"
            },
            {
                "name": "Living Room",
                "icon": "livingroom_01",
                "subGroups": [],
                "deviceIds": [
                    "<device-id-11>"
                ],
                "id": "<group-id-6>"
            },
            {
                "deviceIds": [
                    "<device-id-5>",
                    "<device-id-4>"
                ],
                "icon": "",
                "id": "<group-id-default>",
                "name": "",
                "type": "DEFAULT"
            }
        ],
        "id": "<home-id>",
        "name": "Home",
        "timezone": "Europe/Berlin"
    }
]
```

## Get Device Template

URL: https://<api-gateway-id>.execute-api.eu-central-1.amazonaws.com/prod/v1/devices/<device-id>/template
Example Response:

```json
{
    "claimingDataFormat": [
        {
            "name": "claimingCode",
            "type": "string"
        }
    ],
    "gtin": "4031602012043",
    "oem": "Moehlenhoff",
    "description": "Alpha Smartware Raumbediengerät Display, neutral",
    "shadows": [
        {
            "name": "meta",
            "category": "meta",
            "elements": [
                {
                    "content": {
                        "category": "ping",
                        "properties": {
                            "type": "boolean",
                            "comment": "Pseudo-property to trigger data dump of the device"
                        }
                    },
                    "id": "ping",
                    "writable": true
                },
                {
                    "content": {
                        "category": "restart",
                        "properties": {
                            "type": "boolean",
                            "comment": "Pseudo-property to trigger device restart"
                        }
                    },
                    "id": "restart",
                    "writable": true
                },
                {
                    "content": {
                        "category": "templateVersion",
                        "properties": {
                            "type": "number",
                            "minimum": 0
                        }
                    },
                    "id": "templateVersion",
                    "writable": false
                },
                {
                    "content": {
                        "category": "name",
                        "properties": {
                            "type": "string"
                        }
                    },
                    "id": "name",
                    "writable": true
                },
                {
                    "content": {
                        "category": "serialNo",
                        "properties": {
                            "type": "string"
                        }
                    },
                    "id": "serialNo",
                    "writable": false
                },
                {
                    "content": {
                        "category": "rssi",
                        "properties": {
                            "step": 1,
                            "places": 0,
                            "min": 0,
                            "type": "interval",
                            "max": 100
                        }
                    },
                    "id": "rssi",
                    "writable": false
                },
                {
                    "content": {
                        "category": "firmware",
                        "properties": {
                            "type": "firmware",
                            "moduleType": "MCU",
                            "current": {
                                "type": "string"
                            }
                        }
                    },
                    "id": "0",
                    "writable": false
                },
                {
                    "content": {
                        "category": "lastHeartbeatAt",
                        "properties": {
                            "type": "string",
                            "timeoutMinutes": 360,
                            "comment": "ISO 8601 conforming datetime string, e.g. 2022-02-02T13:37:00Z"
                        }
                    },
                    "id": "lastHeartbeatAt",
                    "writable": false
                },
                {
                    "content": {
                        "category": "isOnline",
                        "properties": {
                            "type": "boolean"
                        }
                    },
                    "id": "isOnline",
                    "writable": false
                }
            ]
        },
        {
            "name": "status",
            "category": "status",
            "elements": [
                {
                    "content": {
                        "category": "battery",
                        "properties": {
                            "step": 1,
                            "places": 0,
                            "min": 0,
                            "type": "interval",
                            "max": 100
                        }
                    },
                    "id": "10",
                    "writable": false
                },
                {
                    "content": {
                        "category": "targetTemperature",
                        "properties": {
                            "step": 0.2,
                            "places": 2,
                            "min": 5,
                            "type": "interval",
                            "max": 30
                        }
                    },
                    "id": "30",
                    "writable": true
                },
                {
                    "content": {
                        "category": "temperature",
                        "properties": {
                            "step": 0.01,
                            "places": 1,
                            "min": 0,
                            "type": "interval",
                            "max": 40
                        }
                    },
                    "id": "31",
                    "writable": false
                },
                {
                    "content": {
                        "category": "humidity",
                        "properties": {
                            "step": 1,
                            "places": 0,
                            "min": 0,
                            "type": "interval",
                            "max": 100
                        }
                    },
                    "id": "33",
                    "writable": false
                }
            ]
        },
        {
            "name": "settings",
            "category": "settings",
            "elements": [
                {
                    "content": {
                        "category": "heatingProfile",
                        "properties": {
                            "maxItemsPerTimeUnit": 6,
                            "minuteInterval": 15,
                            "item": {
                                "content": {
                                    "category": "targetTemperature",
                                    "properties": {
                                        "step": 0.2,
                                        "places": 2,
                                        "min": 5,
                                        "type": "interval",
                                        "max": 30
                                    }
                                },
                                "fieldName": "temperature"
                            },
                            "itemTimePattern": "hh:mm",
                            "type": "schedule",
                            "minItemsPerTimeUnit": 0,
                            "timeUnit": "weekDays"
                        }
                    },
                    "id": "timeProfile",
                    "writable": true
                },
                {
                    "content": {
                        "category": "coolingProfile",
                        "properties": {
                            "maxItemsPerTimeUnit": 6,
                            "minuteInterval": 15,
                            "item": {
                                "content": {
                                    "category": "targetTemperature",
                                    "properties": {
                                        "step": 0.2,
                                        "places": 2,
                                        "min": 5,
                                        "type": "interval",
                                        "max": 30
                                    }
                                },
                                "fieldName": "temperature"
                            },
                            "itemTimePattern": "hh:mm",
                            "type": "schedule",
                            "minItemsPerTimeUnit": 0,
                            "timeUnit": "weekDays"
                        }
                    },
                    "id": "coolingProfile",
                    "writable": true
                },
                {
                    "content": {
                        "category": "roomCorrection",
                        "properties": {
                            "maxItemsPerTimeUnit": 6,
                            "pattern": "hh:mm",
                            "type": "smartStartStopCorrection",
                            "minItemsPerTimeUnit": 0,
                            "timeUnit": "weekDays"
                        }
                    },
                    "id": "correctionProfile",
                    "writable": false
                },
                {
                    "content": {
                        "category": "aswRbgInfo",
                        "properties": {
                            "type": "aswRbgInfo"
                        }
                    },
                    "id": "aswRbgInfo",
                    "writable": false
                },
                {
                    "content": {
                        "category": "vacationTemperature",
                        "properties": {
                            "step": 1,
                            "places": 2,
                            "min": 5,
                            "type": "interval",
                            "max": 30
                        }
                    },
                    "id": "34",
                    "writable": true
                },
                {
                    "userWritable": true,
                    "id": "49",
                    "content": {
                        "category": "aswCfgTargetTemp",
                        "properties": {
                            "step": 0.2,
                            "places": 2,
                            "min": 5,
                            "type": "interval",
                            "max": 30
                        }
                    },
                    "writable": true
                },
                {
                    "userWritable": true,
                    "id": "47",
                    "content": {
                        "category": "aswCfgLockMode",
                        "properties": {
                            "type": "aswCfgLockMode"
                        }
                    },
                    "writable": true
                },
                {
                    "content": {
                        "category": "coolHeatMode",
                        "properties": {
                            "type": "coolHeatMode"
                        }
                    },
                    "id": "36",
                    "writable": false
                },
                {
                    "userWritable": true,
                    "id": "64",
                    "installationOnly": true,
                    "content": {
                        "category": "coolHeatModeLock",
                        "properties": {
                            "type": "coolHeatMode"
                        }
                    },
                    "writable": true
                },
                {
                    "userWritable": false,
                    "id": "39",
                    "content": {
                        "category": "vacationMode",
                        "properties": {
                            "type": "enum",
                            "values": [
                                "off",
                                "on"
                            ]
                        }
                    },
                    "writable": false
                },
                {
                    "content": {
                        "category": "workMode",
                        "properties": {
                            "type": "enum",
                            "values": [
                                "manual",
                                "auto"
                            ]
                        }
                    },
                    "id": "40",
                    "writable": true
                },
                {
                    "userWritable": true,
                    "id": "41",
                    "installationOnly": true,
                    "content": {
                        "category": "aswCfgExternalSensor",
                        "properties": {
                            "type": "enum",
                            "values": [
                                "none",
                                "dewPointSensor",
                                "floorSensor",
                                "roomSensor"
                            ]
                        }
                    },
                    "writable": true
                },
                {
                    "userWritable": true,
                    "id": "63",
                    "installationOnly": false,
                    "content": {
                        "category": "aswCfgFloorTempAlias",
                        "properties": {
                            "maxFloorTempOff": 12.2,
                            "minFloorTempOff": 0.8,
                            "minFloorTempMax": 6,
                            "maxFloorTempMin": 7,
                            "minFloorTempMin": 1,
                            "maxFloorTempMax": 12,
                            "step": 0.2,
                            "type": "aswCfgFloorTempAlias"
                        }
                    },
                    "writable": true
                },
                {
                    "userWritable": true,
                    "id": "35",
                    "content": {
                        "category": "aswCfgDewSensorDewAlarm",
                        "properties": {
                            "type": "aswCfgDewSensor"
                        }
                    },
                    "writable": true
                }
            ]
        }
    ],
    "backend": "qbeyond",
    "type": "rbg",
    "version": 16
}
```

## Get Device Values

URL: https://<api-gateway-id>.execute-api.eu-central-1.amazonaws.com/prod/v1/devices/<device-id>/values
Example Response:

```json
{
    "0": {
        "current": "03.10",
        "available": "03.10"
    },
    "10": 72,
    "30": 19,
    "31": 22,
    "33": 52,
    "34": 5,
    "39": "off",
    "40": "manual",
    "41": "none",
    "47": {
        "standby": false,
        "menu": false,
        "targetTemp": false,
        "reserved1": false,
        "reserved2": false,
        "reserved3": false,
        "reserved4": false,
        "reserved5": false
    },
    "49": {
        "maxTargetTemp": 30,
        "minTargetTemp": 5
    },
    "name": "ASW Room Control Unit",
    "templateVersion": 16,
    "serialNo": "<serial-no>",
    "lastHeartbeatAt": "2026-01-23T10:44:51.000Z",
    "isOnline": true,
    "rssi": 29,
    "aswRbgInfo": {
        "basisIsPaired": true,
        "coolingProfile": false,
        "heatingProfile": true
    },
    "timeProfile": {
        "monday": [
            {
                "time": "06:00",
                "temperature": 21
            },
            {
                "time": "08:00",
                "temperature": 19
            },
            {
                "time": "15:00",
                "temperature": 21
            },
            {
                "time": "22:00",
                "temperature": 19
            }
        ],
        "tuesday": [
            {
                "time": "06:00",
                "temperature": 21
            },
            {
                "time": "08:00",
                "temperature": 19
            },
            {
                "time": "15:00",
                "temperature": 21
            },
            {
                "time": "22:00",
                "temperature": 19
            }
        ],
        "wednesday": [
            {
                "time": "06:00",
                "temperature": 21
            },
            {
                "time": "08:00",
                "temperature": 19
            },
            {
                "time": "15:00",
                "temperature": 21
            },
            {
                "time": "22:00",
                "temperature": 19
            }
        ],
        "thursday": [
            {
                "time": "06:00",
                "temperature": 21
            },
            {
                "time": "08:00",
                "temperature": 19
            },
            {
                "time": "15:00",
                "temperature": 21
            },
            {
                "time": "22:00",
                "temperature": 19
            }
        ],
        "friday": [
            {
                "time": "06:00",
                "temperature": 21
            },
            {
                "time": "08:00",
                "temperature": 19
            },
            {
                "time": "15:00",
                "temperature": 21
            },
            {
                "time": "22:00",
                "temperature": 19
            }
        ],
        "saturday": [
            {
                "time": "06:00",
                "temperature": 19
            },
            {
                "time": "08:00",
                "temperature": 21
            },
            {
                "time": "22:00",
                "temperature": 19
            }
        ],
        "sunday": [
            {
                "time": "06:00",
                "temperature": 19
            },
            {
                "time": "08:00",
                "temperature": 21
            },
            {
                "time": "22:00",
                "temperature": 19
            }
        ]
    },
    "correctionProfile": {
        "monday": [
            "01:00",
            "01:00",
            "01:00",
            "01:00",
            "01:00",
            "01:00"
        ],
        "tuesday": [
            "01:00",
            "01:00",
            "01:00",
            "01:00",
            "01:00",
            "01:00"
        ],
        "wednesday": [
            "01:00",
            "01:00",
            "01:00",
            "01:00",
            "01:00",
            "01:00"
        ],
        "thursday": [
            "01:00",
            "01:00",
            "01:00",
            "01:00",
            "01:00",
            "01:00"
        ],
        "friday": [
            "01:00",
            "01:00",
            "01:00",
            "01:00",
            "01:00",
            "01:00"
        ],
        "saturday": [
            "01:00",
            "01:00",
            "01:00",
            "01:00",
            "01:00",
            "01:00"
        ],
        "sunday": [
            "01:00",
            "01:00",
            "01:00",
            "01:00",
            "01:00",
            "01:00"
        ]
    }
}
```

# Device Updates

Request: PUT https://<api-gateway-id>.execute-api.eu-central-1.amazonaws.com/prod/v1/devices/<device-id>/values
Example Request Body to set target temperature:
```json
{
    "30": 20.0
}
```

Full example with headers:

PUT https://<api-gateway-id>.execute-api.eu-central-1.amazonaws.com/prod/v1/devices/<device-id>/values HTTP/1.1
user-agent: Dart/3.10 (dart:io)
x-amz-date: <amz-date>
accept: application/json
x-amz-security-token: <security-token>
accept-encoding: gzip
content-length: 11
authorization: AWS4-HMAC-SHA256 Credential=<access-key-id>/20260123/eu-central-1/execute-api/aws4_request, SignedHeaders=accept;content-type;host;x-amz-date, Signature=<signature>
host: <api-gateway-id>.execute-api.eu-central-1.amazonaws.com
content-type: application/json

Request Body:

{
"30": 19.6
}

Example Response: It will not contain any JSON! Just take care of a successful HTTP status.

Important notes:

Take care of only trying to set ALLOWED values, e.g. thermostats also define the allowed values in their device template response, e.g.:

"content": {
    "category": "targetTemperature",
    "properties": {
        "step": 0.2,
        "places": 2,
        "min": 5,
        "type": "interval",
        "max": 30
    }
},
