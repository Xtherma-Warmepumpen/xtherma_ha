#!/bin/bash

test -f ../../.env && source ../../.env

if [ -z "$API_KEY" -o -z "$SERIAL_NO" ]; then
	echo "API_KEY / SERIAL_NO undefined."
	exit 1
fi

curl -H "Authorization: Bearer $API_KEY" https://fernportal.xtherma.de/api/device/$SERIAL_NO > temp.json

# anonymize and inject values so our snapshots don't change needlessly.
# the main goal here is to pick up changes in the REST API.
cat temp.json | \
jq  '.serial_number = "FP-04-123456"' | \
jq '(.settings[] | select(.key == "310")).value = 1' | \
jq '(.settings[] | select(.key == "311")).value = -9' | \
jq '(.settings[] | select(.key == "312")).value = 14' | \
jq '(.settings[] | select(.key == "316")).value = 22' | \
jq '(.settings[] | select(.key == "320")).value = 29' | \
jq '(.settings[] | select(.key == "350")).value = 0' | \
jq '(.settings[] | select(.key == "351")).value = 28' | \
jq '(.settings[] | select(.key == "352")).value = 35' | \
jq '(.settings[] | select(.key == "355")).value = 25' | \
jq '(.settings[] | select(.key == "356")).value = 20' | \
jq '(.settings[] | select(.key == "360")).value = 20' | \
jq '(.settings[] | select(.key == "410")).value = 0' | \
jq '(.settings[] | select(.key == "411")).value = -9' | \
jq '(.settings[] | select(.key == "415")).value = 35' | \
jq '(.settings[] | select(.key == "416")).value = 25' | \
jq '(.settings[] | select(.key == "420")).value = 35' | \
jq '(.settings[] | select(.key == "450")).value = 1' | \
jq '(.settings[] | select(.key == "451")).value = 33' | \
jq '(.settings[] | select(.key == "452")).value = 33' | \
jq '(.settings[] | select(.key == "455")).value = 29' | \
jq '(.settings[] | select(.key == "456")).value = 20' | \
jq '(.settings[] | select(.key == "460")).value = 20' | \
jq '(.settings[] | select(.key == "501")).value = 50' | \
jq '(.settings[] | select(.key == "522")).value = 45' | \
jq '(.settings[] | select(.key == "811")).value = 5' | \
jq '(.settings[] | select(.key == "812")).value = 10' | \
jq '(.settings[] | select(.key == "813")).value = 0' | \
jq '(.settings[] | select(.key == "412")).value = 18' | \
jq '(.settings[] | select(.key == "315")).value = 32' | \
jq '(.settings[] | select(.key == "002")).value = 4' | \
jq '(.settings[] | select(.key == "001")).value = 1' | \
jq '(.settings[] | select(.key == "003")).value = 0' | \
jq '(.settings[] | select(.key == "808")).value = 0' | \
jq '(.settings[] | select(.key == "815")).value = 0' | \
jq '(.telemetry[] | select(.key == "tvl")).value = 261' | \
jq '(.telemetry[] | select(.key == "trl")).value = 267' | \
jq '(.telemetry[] | select(.key == "tw")).value = 515' | \
jq '(.telemetry[] | select(.key == "tk")).value = 325' | \
jq '(.telemetry[] | select(.key == "tk1")).value = 301' | \
jq '(.telemetry[] | select(.key == "tk2")).value = -989' | \
jq '(.telemetry[] | select(.key == "vf")).value = 0' | \
jq '(.telemetry[] | select(.key == "ta")).value = 135' | \
jq '(.telemetry[] | select(.key == "ta1")).value = 120' | \
jq '(.telemetry[] | select(.key == "ta4")).value = 121' | \
jq '(.telemetry[] | select(.key == "ta24")).value = 118' | \
jq '(.telemetry[] | select(.key == "ld1")).value = 5' | \
jq '(.telemetry[] | select(.key == "ld2")).value = 0' | \
jq '(.telemetry[] | select(.key == "tr")).value = 219' | \
jq '(.telemetry[] | select(.key == "evu")).value = 0' | \
jq '(.telemetry[] | select(.key == "pkl")).value = 0' | \
jq '(.telemetry[] | select(.key == "pk")).value = 0' | \
jq '(.telemetry[] | select(.key == "pk1")).value = 0' | \
jq '(.telemetry[] | select(.key == "pk2")).value = 0' | \
jq '(.telemetry[] | select(.key == "pww")).value = 1' | \
jq '(.telemetry[] | select(.key == "hw_target")).value = 50' | \
jq '(.telemetry[] | select(.key == "h_target")).value = 229' | \
jq '(.telemetry[] | select(.key == "h1_target")).value = 229' | \
jq '(.telemetry[] | select(.key == "h2_target")).value = 350' | \
jq '(.telemetry[] | select(.key == "c_target")).value = 200' | \
jq '(.telemetry[] | select(.key == "c1_target")).value = 200' | \
jq '(.telemetry[] | select(.key == "c2_target")).value = 200' | \
jq '(.telemetry[] | select(.key == "in_hp")).value = 0' | \
jq '(.telemetry[] | select(.key == "v")).value = 0' | \
jq '(.telemetry[] | select(.key == "out_hp")).value = 0' | \
jq '(.telemetry[] | select(.key == "efficiency_hp")).value = 0' | \
jq '(.telemetry[] | select(.key == "efficiency_total")).value = 0' | \
jq '(.telemetry[] | select(.key == "in_backup")).value = 0' | \
jq '(.telemetry[] | select(.key == "out_backup")).value = 0' | \
jq '(.telemetry[] | select(.key == "ta8")).value = 109' | \
jq '(.telemetry[] | select(.key == "sg")).value = 0' | \
jq '(.telemetry[] | select(.key == "day_hp_out_h")).value = 1428' | \
jq '(.telemetry[] | select(.key == "day_hp_out_c")).value = 0' | \
jq '(.telemetry[] | select(.key == "day_hp_out_hw")).value = 398' | \
jq '(.telemetry[] | select(.key == "day_backup3_out_h")).value = 0' | \
jq '(.telemetry[] | select(.key == "day_backup6_out_h")).value = 0' | \
jq '(.telemetry[] | select(.key == "day_backup6_out_hw")).value = 0' | \
jq '(.telemetry[] | select(.key == "day_backup3_out_hw")).value = 0' | \
jq '(.telemetry[] | select(.key == "day_hp_in_h")).value = 244' | \
jq '(.telemetry[] | select(.key == "day_hp_in_c")).value = 0' | \
jq '(.telemetry[] | select(.key == "day_hp_in_hw")).value = 119' | \
jq '(.telemetry[] | select(.key == "day_backup3_in_hw")).value = 0' | \
jq '(.telemetry[] | select(.key == "day_backup6_in_hw")).value = 0' | \
jq '(.telemetry[] | select(.key == "day_backup3_in_h")).value = 0' | \
jq '(.telemetry[] | select(.key == "day_backup6_in_h")).value = 0' | \
jq '(.telemetry[] | select(.key == "14a")).value = 0' | \
jq '(.telemetry[] | select(.key == "controller_v")).value = 243' | \
jq '(.telemetry[] | select(.key == "error")).value = 1' | \
jq '(.telemetry[] | select(.key == "mode")).value = 3' | \
cat - > rest_response.json
