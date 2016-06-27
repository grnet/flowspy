# Description

Since v1.3 FoD officially has a REST API. This allows operations on:

* `ThenAction`
* `MatchPort`
* `MatchProtocol`
* `MatchDscp`
* `FragmentType`
* `Route`

The API needs authentication. Out of the box the supported authentication
type is Token Authentication.

## Generating Tokens

A user can generate an API token using the FoD UI. Select "My Profile" from the
top right menu and on the "Api Token" section click "Generate One".

## Accessing the API

The API is available at `/api/`. One can see the available API endpoints for 
each model by making a GET request there. An authentication token must be added
in the request:

* Using `cURL`, add the `-H "Authorization: Token <your-token>"`
parameter
* Using Postman, under the "Headers" add a header with name
"Authorization" and value "Token <your-token>".

# Usage Examples

Some basic usage examples will be provided including available
actions. Examples will be provided in `cURL` form.

An example will be provided for `ThenAction`. This example applies to most other
models (`MatchPort`, `FragmentType`, `MatchProtocol`, `MatchDscp`) except
`Route` which is more complex and will be treated separately.

## ThenAction

### GET

#### All items

URL: `/api/thenactions/`

Example:
```
curl -X GET https://fod.example.com/api/thenactions/ -H "Authorization: Token <your-token>"

RESPONSE:
[  
   {  
      "id" 1,
      "action":"discard",
      "action_value":""
   },
   {  
      "id" 3,
      "action":"rate-limit",
      "action_value":"10000k"
   },
   ...
]
```

#### A specific item

One can also GET a specific `ThenAction`, by using the `id` in the GET url

URL: `/api/thenactions/<thenaction-id>/`

Example:
```
curl -X GET https://fod.example.com/api/thenactions/13/ -H "Authorization: Token <your-token>"

RESPONSE:
{  
   "id" 13,
   "action":"discard",
   "action_value":""
},
```

### POST

Here both `action`, `action_value` fields are required. 

URL: `/api/thenactions/`

Example:
```
curl -X POST https://fod.example.com/api/thenactions/ -F "action=rate-limit" -F "action_value=10k" -H "Authorization: Token <your-token>"

RESPONSE:
{
    "id": 24,
    "action": "rate-limit",
    "action_value": "10k" 
}
```

### PUT

Here whichever of the `action`, `action_value` fields can be supplied

URL: `/api/thenactions/<thenaction-id>/`

Example:
```
curl -X PUT https://fod.example.com/api/thenactions/24/ -F "action=rate-limit" -F "action_value=10k" -H "Authorization: Token <your-token>"

RESPONSE:
{
    "id": 24,
    "action": "rate-limit",
    "action_value": "10k" 
}
```
### DELETE

URL: `/api/thenactions/<thenaction-id>/`

Example:
```
curl -X DELETE https://fod.example.com/api/thenactions/24/ -H "Authorization: Token <your-token>"

RESPONSE:
NO CONTENT
```

## Route

### GET

#### All items

URL: `/api/routes/`

Example:
```
curl -X GET https://fod.example.com/api/routes/ -H "Authorization: Token <your-token>"

RESPONSE:
[
  {
    "name": "nonadmin_safts_4T0ABD",
    "id": 1,
    "comments": "testing rule myman",
    "applier": "admin",
    "source": "62.217.45.76/32",
    "sourceport": [],
    "destination": "62.217.45.88/32",
    "destinationport": [],
    "port": [],
    "dscp": [],
    "fragmenttype": [],
    "icmpcode": "",
    "packetlength": null,
    "protocol": [],
    "tcpflag": "",
    "then": [],
    "filed": "2017-03-28T14:51:33Z",
    "last_updated": "2017-03-28T14:51:33Z",
    "status": "INACTIVE",
    "expires": "2017-04-04",
    "response": "Successfully committed",
    "requesters_address": "83.212.9.94"
  },
   ...
]
```

#### A specific item

One can also GET a specific `Route`, by using the `id` in the GET url

URL: `/api/routes/<route-id>/`

Example:
```
curl -X GET https://fod.example.com/api/routes/1/ -H "Authorization: Token <your-token>"

RESPONSE:
{
    "name": "nonadmin_safts_4T0ABD",
    "id": 1,
    "comments": "testing rule myman",
    "applier": "admin",
    "source": "62.217.45.76/32",
    "sourceport": [],
    "destination": "62.217.45.88/32",
    "destinationport": [],
    "port": [],
    "dscp": [],
    "fragmenttype": [],
    "icmpcode": "",
    "packetlength": null,
    "protocol": [],
    "tcpflag": "",
    "then": [],
    "filed": "2017-03-28T14:51:33Z",
    "last_updated": "2017-03-28T14:51:33Z",
    "status": "INACTIVE",
    "expires": "2017-04-04",
    "response": "Successfully committed",
    "requesters_address": "83.212.9.94"
}
```

### POST

Required fields:

* `name`: a name for the route
* `source`: a source subnet in CIDR formation
* `destination`: a destination subnet in CIDR formation
* `comments`: a small comment on what this route is about

The response will contain all the additional fields

URL: `/api/routes/`

Example:
```
curl -X POST https://fod.example.com/api/routes/ -F "source=62.217.45.75/32" -F "destination=62.217.45.91/32" -F "name=testroute" -F "comments=Route for testing" -H "Authorization: Token <your-token>"

RESPONSE:
{
    "name": "testroute_ODUI3E",
    "id": 3,
    "comments": "Route for testing",
    "applier": "admin",
    "source": "62.217.45.76/32",
    "sourceport": [],
    "destination": "62.217.45.90/32",
    "destinationport": [],
    "port": [],
    "dscp": [],
    "fragmenttype": [],
    "icmpcode": null,
    "packetlength": null,
    "protocol": [],
    "tcpflag": null,
    "then": [],
    "filed": "2017-03-29T13:56:45.860Z",
    "last_updated": "2017-03-29T13:56:45.860Z",
    "status": "PENDING",
    "expires": "2017-04-05",
    "response": null,
    "requesters_address": null
}
```

Notice that the `Route` has a `PENDING` status. This happens because the `Route`
is applied asynchronously to the Flowspec device (the API does not wait for the
operation). After a while the `Route` application will be finished and the 
`status` field will contain the updated status (`ACTIVE`, `ERROR` etc).
You can check this `Route`s status by issuing a `GET` request with the `id`
the API returned.

This `Route`, however, is totally useless, since it applies no action for the
matched traffic. Let's add one with a `then` action which will discard it.

To do that, we must first add a `ThenAction` (or pick one of the already
existing) since we need it's `id`. Let's assume a `ThenAction` with an `id` of
`4` exists. To create a new `Route` with this `ThenAction`:

```
curl -X POST https://fod.example.com/api/routes/ -F "source=62.217.45.75/32" -F "destination=62.217.45.91/32" -F "name=testroute" -F "comments=Route for testing" -F "then=https://fod.example.com/api/thenactions/4" -H "Authorization: Token <your-token>"

{
    "name":"testroute_9Q5Y90",
    "id":5,
    "comments":"Route for testing",
    "applier":"admin",
    "source":"62.217.45.75/32",
    "sourceport":[],
    "destination":"62.217.45.94/32",
    "destinationport":[],
    "port":[],
    "dscp":[],
    "fragmenttype":[],
    "icmpcode":null,
    "packetlength":null,
    "protocol":[],
    "tcpflag":null,
    "then":[
       "https://fod.example.com/api/thenactions/4/"
    ],
    "filed":"2017-03-29T14:21:03.261Z",
    "last_updated":"2017-03-29T14:21:03.261Z",
    "status":"PENDING",
    "expires":"2017-04-05",
    "response":null,
    "requesters_address":null
}
```

With the same process one can associate a `Route` with the `MatchPort`,
`FragmentType`, `MatchProtocol` & `MatchDscp` models.

NOTE:

When adding multiple `ForeignKey` related fields (such as multiple
`MatchPort` or `ThenAction` items) it is best to use a `json` file on the
request instead of specifying each field as a form argument.

Example:

```
curl -X POST https://fod.example.com/api/routes/ -d@data.json -H "Authorization: Token <your-token>"

data.json:
{
    "name": "testroute",
    "comments": "Route for testing",
    "then": [
        "https://fod.example.com/api/thenactions/4",
        "https://fod.example.com/api/thenactions/5",
    ],
    "source": "62.217.45.75/32",
    "destination": "62.217.45.91/32"
}

RESPONSE:
{
    "name":"testroute_9Q5Y90",
    "id":5,
    "comments":"Route for testing",
    "applier":"admin",
    "source":"62.217.45.75/32",
    "sourceport":[],
    "destination":"62.217.45.94/32",
    "destinationport":[],
    "port":[],
    "dscp":[],
    "fragmenttype":[],
    "icmpcode":null,
    "packetlength":null,
    "protocol":[],
    "tcpflag":null,
    "then":[
       "https://fod.example.com/api/thenactions/4/"
    ],
    "filed":"2017-03-29T14:21:03.261Z",
    "last_updated":"2017-03-29T14:21:03.261Z",
    "status":"PENDING",
    "expires":"2017-04-05",
    "response":null,
    "requesters_address":null
}
```

### PUT, PATCH

`Route` objects can be modified using the `PUT` / `PATCH` HTTP methods.

When using `PUT` all fields should be specified (see `POST` section).
However, when using `PATCH` one can specify single fields too. This is useful
for changing the `status` of an `INACTIVE` `Route` to `ACTIVE`.

The process is the same as described above with `POST`. Don't forget to use
the correct method.

### DELETE

See `ThenAction`s.

### General notes on `Route` models:

* When `POST`ing a new `Route`, FoD will automatically commit it to the flowspec
device. Thus, `POST`ing a new `Route` with a status of `INACTIVE` has no effect,
since the `Route` will be activated and the status will be restored to `ACTIVE`.
* When `DELETE`ing a `Route`, the actual `Route` object will remain. FoD will
only delete the rule from the flowspec device and change the `Route`'s status to
'INACTIVE'
* When changing (`PUT`/`PATCH`) a `Route`, FoD will sync the changes to the
flowspec device. Changing the status of the `Route` will activate / delete the
rule respectively.
