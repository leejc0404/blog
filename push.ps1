param([string]$m = "")

# ── 설정 ────────────────────────────────────────────
$repo   = if ($PSScriptRoot) { $PSScriptRoot } else { "C:\Users\win\Documents\Claude\blog" }
$branch = "main"
# ──────────────────────────────────────────────────────

$ErrorActionPreference = "Continue"
try { $OutputEncoding = [Console]::OutputEncoding = [Console]::InputEncoding = [Text.Encoding]::UTF8 } catch {}

function Say($text, $color = "Gray") { Write-Host $text -ForegroundColor $color }

# git이 stderr에 쓰는 정상 메시지(To https://... 등)가 빨간 오류로 보이지 않게
# stderr를 stdout에 합쳐 평문으로 출력하고, 성공 여부는 종료 코드로만 판단한다
function Run-Git {
    $out = & git @args 2>&1
    $code = $LASTEXITCODE
    foreach ($line in $out) { if ("$line".Trim()) { Write-Host "  $line" -ForegroundColor DarkGray } }
    return $code
}

if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    Say "git이 설치되어 있지 않거나 PATH에 없습니다. https://git-scm.com/download/win" Red
    exit 1
}

if (-not (Test-Path $repo)) {
    Say "폴더를 찾을 수 없습니다: $repo" Red
    exit 1
}

Set-Location $repo

if (-not (Test-Path ".git")) {
    Say ".git 폴더가 없습니다. 먼저 아래를 실행하세요:" Red
    Say "  git init" Yellow
    Say "  git branch -M $branch" Yellow
    Say "  git remote add origin https://github.com/leejc0404/blog.git" Yellow
    exit 1
}

if ([string]::IsNullOrWhiteSpace($m)) {
    $m = "update " + (Get-Date -Format "yyyy-MM-dd HH:mm")
}

# ── 0단계: 잔여 lock 파일 정리 ──
# Cowork(원격 세션)이 git을 실행하면 삭제 권한이 없어 lock 파일이 남을 수 있다
$locks = @(".git\index.lock", ".git\HEAD.lock", ".git\config.lock", ".git\objects\maintenance.lock")
$found = $locks | Where-Object { Test-Path $_ }

if ($found) {
    if (Get-Process git -ErrorAction SilentlyContinue) {
        Say "git 프로세스가 실행 중입니다. 종료한 뒤 다시 실행하세요." Red
        exit 1
    }
    foreach ($l in $found) {
        Remove-Item $l -Force -ErrorAction SilentlyContinue
        Say "잔여 lock 제거: $l" DarkYellow
    }
}

# ── 0-1단계: 브랜치 확인 ──
$cur = "$(git rev-parse --abbrev-ref HEAD 2>&1)".Trim()
if ($cur -ne $branch) {
    Say "현재 브랜치가 '$cur' 입니다. '$branch' 가 아니면 이 스크립트는 진행하지 않습니다." Red
    Say "  git switch $branch" Yellow
    exit 1
}

# ── 0-2단계: 진행 중인 rebase/merge 잔재 확인 ──
if ((Test-Path ".git\rebase-merge") -or (Test-Path ".git\rebase-apply")) {
    Say "이전 rebase가 끝나지 않은 상태입니다. 아래 중 하나를 실행한 뒤 다시 시도하세요." Red
    Say "  git rebase --abort     (되돌리기)" Yellow
    Say "  git rebase --continue  (충돌 해결 후 이어가기)" Yellow
    exit 1
}
if (Test-Path ".git\MERGE_HEAD") {
    Say "이전 merge가 끝나지 않은 상태입니다. 'git merge --abort' 후 다시 시도하세요." Red
    exit 1
}

# ── 1단계: 올릴 파일 고르기 (2026-11-26 — 공개 저장소 보호) ──
# git add -A 를 쓰지 않는다. 이미 올라가 있는 파일의 수정·삭제와, 허용 목록에 맞는 새 파일만 올린다.
#   허용 목록: 최상위 .md(지침·루틴) / .gitignore / push.bat·push.ps1 / tools 아래 코드(py·ps1·md·json·html·css·js)
$allow = '^([^/]+\.md|\.gitignore|push\.(bat|ps1)|tools/.+\.(py|ps1|md|json|html|css|js))$'

$null = git add -u 2>&1

$skipped = @()
$newFiles = @(git -c core.quotepath=false ls-files --others --exclude-standard 2>&1 | Where-Object { "$_".Trim() })
foreach ($f in $newFiles) {
    if (("$f" -match '__pycache__') -or ("$f" -notmatch $allow)) { $skipped += "$f"; continue }
    $null = git add -- "$f" 2>&1
}
if ($skipped.Count -gt 0) {
    Say ""
    Say "[올리지 않은 새 파일 — 허용 목록 밖]" Yellow
    $skipped | ForEach-Object { Say "  $_" Yellow }
    Say "  꼭 올려야 하는 파일이면 직접 'git add 파일이름' 한 뒤 다시 실행하세요." DarkYellow
}

# ── 1-1단계: 비밀정보 검사 (이번에 올라갈 파일 이름과 추가된 줄만 본다) ──
$hits = @()
$badName = '(^|/)(pw\.txt|sa\.json|\.env.*|.+\.(key|pem|p12|pfx)|credentials.*\.json|token.*\.json|client_secret.*\.json)$'
foreach ($n in @(git -c core.quotepath=false diff --cached --name-only --diff-filter=AM 2>&1)) {
    if ("$n" -match $badName) { $hits += "$n — 비밀 파일 이름" }
}

$patterns = [ordered]@{
    "개인 키"           = 'BEGIN (RSA |EC |OPENSSH )?PRIVATE KEY'
    "서비스 계정 키"     = '"private_key"\s*:\s*"'
    "Google API 키"     = 'AIza[0-9A-Za-z_\-]{30,}'
    "GitHub 토큰"       = '(ghp_[0-9A-Za-z]{30,}|github_pat_[0-9A-Za-z_]{20,})'
    "API 비밀 키"       = '(sk-[A-Za-z0-9_\-]{20,}|xox[bpa]-[0-9A-Za-z\-]{10,})'
    "비밀번호 대입문"    = '(?i)(password|passwd|app_?pass|secret|api[_\-]?key)\s*[:=]\s*["'']?[^\s"''`<>{}]{8,}'
}
$file = ""
foreach ($line in @(git -c core.quotepath=false diff --cached -U0 --no-color 2>&1)) {
    $s = "$line"
    if ($s.StartsWith("+++ ")) { $file = $s.Substring(4) -replace '^b/', ''; continue }
    if (-not $s.StartsWith("+")) { continue }
    $body = $s.Substring(1)
    foreach ($k in $patterns.Keys) {
        if ($body -match $patterns[$k]) { $hits += "$file — $k (값은 표시하지 않음)"; break }
    }
    # 워드프레스 앱 비밀번호 형태: 영문·숫자 4자 × 6묶음 중 숫자·대문자·소문자가 모두 섞인 것
    foreach ($mm in [regex]::Matches($body, '\b[A-Za-z0-9]{4}( [A-Za-z0-9]{4}){5}\b')) {
        $v = $mm.Value
        if (($v -cmatch '[0-9]') -and ($v -cmatch '[A-Z]') -and ($v -cmatch '[a-z]')) { $hits += "$file — 앱 비밀번호 형태 (값은 표시하지 않음)" }
    }
}
if ($hits.Count -gt 0) {
    Say ""
    Say "[중단] 비밀정보로 보이는 내용이 있어 커밋하지 않았습니다. 이 저장소는 공개입니다." Red
    $hits | Select-Object -Unique | ForEach-Object { Say "  $_" Red }
    $null = git reset -q 2>&1
    Say "  그 내용을 지우거나 파일을 .gitignore 에 넣은 뒤 다시 실행하세요." Yellow
    exit 1
}

# ── 1-2단계: 커밋 ──
$staged = @(git -c core.quotepath=false diff --cached --name-status 2>&1 | Where-Object { "$_".Trim() })
if ($staged.Count -gt 0) {
    Say ""
    Say "[커밋 대상]" Cyan
    $staged | ForEach-Object { Say "  $_" Gray }
    $code = Run-Git commit -m $m
    if ($code -ne 0) {
        Say "커밋 실패." Red
        exit 1
    }
    Say "커밋 완료: $m" Green
} else {
    Say "새로 커밋할 변경사항은 없습니다." Yellow
}

# ── 2단계: 원격 상태 확인 ──
Say ""
Say "원격 확인 중..." DarkGray
$code = Run-Git fetch origin $branch
if ($code -ne 0) {
    Say "원격 조회 실패. 저장소 주소와 네트워크·인증을 확인하세요." Red
    git remote -v
    exit 1
}

function Count-Commits($range) {
    $n = "$(git rev-list --count $range 2>&1)".Trim()
    if ($n -notmatch '^\d+$') { return 0 }
    return [int]$n
}

$ahead  = Count-Commits "origin/$branch..HEAD"
$behind = Count-Commits "HEAD..origin/$branch"

Say "로컬이 원격보다 앞선 커밋 $ahead개 / 뒤처진 커밋 $behind개" DarkGray

# ── 3단계: 뒤처졌으면 먼저 받아온다 (non-fast-forward 거부의 원인) ──
# GitHub 웹에서 직접 편집·삭제하면 원격에만 커밋이 생겨 로컬이 뒤처진다.
if ($behind -gt 0) {
    Say ""
    Say "[원격에만 있는 커밋 $behind개]" Cyan
    git log --oneline "HEAD..origin/$branch"

    if ($ahead -eq 0) {
        Say "빨리감기로 원격 변경사항을 받아옵니다..." DarkGray
        $code = Run-Git merge --ff-only "origin/$branch"
        if ($code -ne 0) {
            Say "빨리감기 실패. 수동 확인이 필요합니다." Red
            exit 1
        }
        Say "원격 변경사항 반영 완료." Green
    } else {
        Say "로컬 커밋을 원격 위로 재배치(rebase)합니다..." DarkGray
        $code = Run-Git pull --rebase origin $branch
        if ($code -ne 0) {
            Say ""
            Say "rebase 충돌이 발생했습니다. 같은 파일을 로컬과 GitHub 양쪽에서 고친 경우입니다." Red
            Say "자동으로 되돌립니다..." DarkYellow
            $null = git rebase --abort 2>&1
            Say ""
            Say "해결 방법 (둘 중 하나):" Yellow
            Say "  1) 로컬 내용을 살리려면: git pull --rebase origin $branch 후 충돌 파일을 직접 정리" Yellow
            Say "  2) GitHub 내용을 살리려면: git reset --hard origin/$branch  (로컬 변경분은 사라집니다)" Yellow
            exit 1
        }
        Say "재배치 완료." Green
    }

    $ahead = Count-Commits "origin/$branch..HEAD"
}

# ── 4단계: 푸시 ──
if ($ahead -eq 0) {
    Say ""
    Say "원격과 동일합니다. 푸시할 것이 없습니다." Yellow
    exit 0
}

Say ""
Say "[푸시할 커밋 $ahead개]" Cyan
git log --oneline "origin/$branch..HEAD"

$code = Run-Git push origin $branch
if ($code -ne 0) {
    Say ""
    Say "푸시 실패." Red
    Say "원격 주소와 GitHub 인증(자격 증명 관리자의 토큰 만료 여부)을 확인하세요." Yellow
    git remote -v
    exit 1
}

Say ""
Say "푸시 완료 ($ahead개 커밋)" Green
Say ("원격 최신: " + "$(git rev-parse --short "origin/$branch" 2>&1)".Trim()) DarkGray
exit 0
