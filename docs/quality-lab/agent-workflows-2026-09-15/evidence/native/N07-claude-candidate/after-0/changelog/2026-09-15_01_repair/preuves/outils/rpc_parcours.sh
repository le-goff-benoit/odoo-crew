set -e
ev=/work/changelog/2026-09-15_01_repair/preuves
run() {  # run <nom> <json> ; echo le champ result
  printf '%s' "$2" > /work/rpc_cas/$1.json
  if ! out=$(/bridge/labctl rpc rpc_cas/$1.json 2>/dev/null); then
    echo "$out" > $ev/rpc_$1.json; echo "FAULT $1" >&2; echo "$out" >&2; exit 1
  fi
  echo "$out" > $ev/rpc_$1.json
  python3 -c "import json,sys;print(json.dumps(json.load(open('$ev/rpc_$1.json'))['result']))"
}
F='["name","state","ordered_qty","delivered_qty","prepared_qty","manual","parent_id"]'

ID=$(run c3_create '{"model":"lab.preparation","method":"create","args":[{"name":"RPC_MANUAL_ZERO","ordered_qty":10,"delivered_qty":0}],"kwargs":{}}')
run c3_set_manual "{\"model\":\"lab.preparation\",\"method\":\"action_set_manual\",\"args\":[[$ID],0],\"kwargs\":{}}" >/dev/null
run c3_read "{\"model\":\"lab.preparation\",\"method\":\"search_read\",\"args\":[[[\"id\",\"=\",$ID]],$F],\"kwargs\":{}}" >/dev/null

ID7=$(run c7_create '{"model":"lab.preparation","method":"create","args":[{"name":"RPC_DUP","ordered_qty":10,"delivered_qty":4,"prepared_qty":88,"manual":true,"state":"done"}],"kwargs":{}}')
NEW7=$(run c7_copy "{\"model\":\"lab.preparation\",\"method\":\"copy\",\"args\":[[$ID7]],\"kwargs\":{}}")
N7=$(python3 -c "print($NEW7[0])")
run c7_read "{\"model\":\"lab.preparation\",\"method\":\"search_read\",\"args\":[[[\"id\",\"in\",[$ID7,$N7]]],$F],\"kwargs\":{}}" >/dev/null

ID8=$(run c8_create '{"model":"lab.preparation","method":"create","args":[{"name":"RPC_SPLIT","ordered_qty":10,"delivered_qty":3,"prepared_qty":5}],"kwargs":{}}')
REM=$(run c8_remainder "{\"model\":\"lab.preparation\",\"method\":\"action_remainder\",\"args\":[[$ID8]],\"kwargs\":{}}")
R8=$(python3 -c "print($REM[0])")
run c8_read "{\"model\":\"lab.preparation\",\"method\":\"search_read\",\"args\":[[[\"id\",\"in\",[$ID8,$R8]]],$F],\"kwargs\":{}}" >/dev/null

ID9=$(run c9_create '{"model":"lab.preparation","method":"create","args":[{"name":"RPC_NOSPLIT","ordered_qty":10,"delivered_qty":10,"prepared_qty":5}],"kwargs":{}}')
E9=$(run c9_remainder "{\"model\":\"lab.preparation\",\"method\":\"action_remainder\",\"args\":[[$ID9]],\"kwargs\":{}}")
run c9_read "{\"model\":\"lab.preparation\",\"method\":\"search_read\",\"args\":[[[\"id\",\"=\",$ID9]],$F],\"kwargs\":{}}" >/dev/null

ID10=$(run c10_create '{"model":"lab.preparation","method":"create","args":[[{"name":"RPC_PAIR_A","ordered_qty":10,"delivered_qty":3},{"name":"RPC_PAIR_B","ordered_qty":10,"delivered_qty":3}]],"kwargs":{}}')
echo "c3=$ID c7=$ID7/$N7 c8=$ID8/$R8 c9=$ID9 vide=$E9 paire=$ID10"
