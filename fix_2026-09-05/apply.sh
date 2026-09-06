#!/bin/bash
# 2026-09-05 전수검사 수정본 적용 스크립트
# 사용법: bash apply.sh [ol|kp|all]
# 주의: content 필드만 전송하므로 발행 상태(status)는 변경되지 않습니다.
set -u
KP_AUTH='leejcfo@gmail.com:W7k2 LP3j gpyb xOAJ jNlP aPCA'
OL_AUTH='leejcfo@gmail.com:GwAT 58mR jPuO NZ38 Cqsu Wphe'
UA='Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
TARGET="${1:-all}"
DIR="$(cd "$(dirname "$0")" && pwd)"
ok=0; fail=0
for site in ol kp; do
  [ "$TARGET" != "all" ] && [ "$TARGET" != "$site" ] && continue
  [ -d "$DIR/$site" ] || continue
  if [ "$site" = "kp" ]; then AUTH="$KP_AUTH"; BASE="https://koreaplug.com"; else AUTH="$OL_AUTH"; BASE="https://0and1life.com"; fi
  for f in "$DIR/$site"/*.html; do
    id=$(basename "$f" | cut -d_ -f1)
    python3 -c "
import json,sys
c=open(sys.argv[1],encoding='utf-8').read()
json.dump({'content':c},open(sys.argv[2],'w',encoding='utf-8'),ensure_ascii=False)
" "$f" /tmp/payload_$id.json
    res=$(curl -s --max-time 60 -u "$AUTH" -A "$UA" -X POST -H "Content-Type: application/json" \
      --data-binary @/tmp/payload_$id.json "$BASE/wp-json/wp/v2/posts/$id")
    rm -f /tmp/payload_$id.json
    st=$(echo "$res" | python3 -c "
import json,sys
try:
    d=json.load(sys.stdin); print('OK status='+d.get('status','?'))
except Exception:
    print('BLOCKED/ERROR')
")
    echo "$site $id $(basename "$f") -> $st"
    case "$st" in OK*) ok=$((ok+1));; *) fail=$((fail+1));; esac
    sleep 2
  done
done
echo "완료: 성공 $ok / 실패 $fail"
