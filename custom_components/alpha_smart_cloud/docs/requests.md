# Alpha Smart Cloud API Reference

This document provides examples of API requests and responses for the Alpha Smart Cloud integration.

## Base URL

```
https://<api-gateway-id>.execute-api.eu-central-1.amazonaws.com/prod/v1
```

---

# Data Retrieval

## Get Devices

**Endpoint:** `GET /devices`

**Description:** Retrieves a list of all devices associated with the account.

**Example Response:**

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

---

## Get Homes

**Endpoint:** `GET /homes`

**Description:** Retrieves a list of all homes, including their groups and associated devices.

**Example Response:**

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

---

## Get Device Template

**Endpoint:** `GET /devices/{device-id}/template`

**Description:** Retrieves the device template, which defines the capabilities, properties, and configuration options for a specific device.

**Example Response:**

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

---

## Get Device Values

**Endpoint:** `GET /devices/{device-id}/values`

**Description:** Retrieves the current state and values of all properties for a specific device.

**Example Response:**

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

---

# Device Updates

## Update Device Values

**Endpoint:** `PUT /devices/{device-id}/values`

**Description:** Updates one or more values on a device. Values must conform to the constraints defined in the device template.

### Set Target Temperature

**Example Request Body:**

```json
{
    "30": 20.0
}
```

**Example Response:** Empty response body with HTTP 200 status on success.

**Important Notes:**

- Only set values that are allowed according to the device template
- Thermostats define allowed values in their template response, for example:

```json
"content": {
    "category": "targetTemperature",
    "properties": {
        "step": 0.2,
        "places": 2,
        "min": 5,
        "type": "interval",
        "max": 30
    }
}
```

**Full Request Example with Headers:**

```http
PUT /devices/{device-id}/values HTTP/1.1
Host: <api-gateway-id>.execute-api.eu-central-1.amazonaws.com
Content-Type: application/json
Accept: application/json
Authorization: AWS4-HMAC-SHA256 Credential=<access-key-id>/20260123/eu-central-1/execute-api/aws4_request, SignedHeaders=accept;content-type;host;x-amz-date, Signature=<signature>
X-Amz-Date: <amz-date>
X-Amz-Security-Token: <security-token>

{
    "30": 19.6
}
```

## Lock/Unlock Device

**Endpoint:** `PUT /devices/{device-id}/values`

**Description:** Controls the physical lock state of the device interface (menu and target temperature controls).

### Lock the Device

**Example Request Body:**

```json
{
    "47": {
        "standby": false,
        "menu": true,
        "targetTemp": true,
        "reserved1": false,
        "reserved2": false,
        "reserved3": false,
        "reserved4": false,
        "reserved5": false
    }
}
```

### Unlock the Device

**Example Request Body:**

```json
{
    "47": {
        "standby": false,
        "menu": false,
        "targetTemp": false,
        "reserved1": false,
        "reserved2": false,
        "reserved3": false,
        "reserved4": false,
        "reserved5": false
    }
}
```

## Set Vacation Temperature

**Endpoint:** `PUT /devices/{device-id}/values`

**Description:** Sets the vacation temperature for the device (the temperature to maintain when vacation mode is active).

**Example Request Body:**

```json
{
    "34": 17
}
```

## Set Heating Profile

**Endpoint:** `PUT /devices/{device-id}/values`

**Description:** Configures the weekly heating schedule for the device. Each day can have up to 6 time/temperature entries.

**Example Request Body:**

```json
{
    "timeProfile": {
        "monday": [
            {
                "time": "05:00",
                "temperature": 21.0
            },
            {
                "time": "08:00",
                "temperature": 20.0
            },
            {
                "time": "20:00",
                "temperature": 19.0
            }
        ],
        "tuesday": [
            {
                "time": "05:00",
                "temperature": 21.0
            },
            {
                "time": "08:00",
                "temperature": 20.0
            },
            {
                "time": "20:00",
                "temperature": 19.0
            }
        ],
        "wednesday": [
            {
                "time": "05:00",
                "temperature": 21.0
            },
            {
                "time": "08:00",
                "temperature": 20.0
            },
            {
                "time": "20:00",
                "temperature": 19.0
            }
        ],
        "thursday": [
            {
                "time": "05:00",
                "temperature": 21.0
            },
            {
                "time": "08:00",
                "temperature": 20.0
            },
            {
                "time": "20:00",
                "temperature": 19.0
            }
        ],
        "friday": [
            {
                "time": "05:00",
                "temperature": 21.0
            },
            {
                "time": "08:00",
                "temperature": 20.0
            },
            {
                "time": "20:00",
                "temperature": 19.0
            }
        ],
        "saturday": [
            {
                "time": "06:00",
                "temperature": 19.0
            },
            {
                "time": "08:00",
                "temperature": 21.0
            },
            {
                "time": "22:00",
                "temperature": 19.0
            }
        ],
        "sunday": [
            {
                "time": "06:00",
                "temperature": 19.0
            },
            {
                "time": "08:00",
                "temperature": 21.0
            },
            {
                "time": "22:00",
                "temperature": 19.0
            }
        ]
    }
}
```

---

# Home Management

## Set Holiday Mode

**Endpoint:** `POST /homes/{home-id}/vacationMode`

**Description:** Enables or disables holiday/vacation mode for the entire home (not individual devices). When enabled, all devices use their configured vacation temperature.

### Enable Holiday Mode

**Example Request Body:**

```json
{
    "mode": "on"
}
```

### Disable Holiday Mode

**Example Request Body:**

```json
{
    "mode": "off"
}
```