<#
  blog-sync.ps1 — 2026-10-16 분량·모바일 개정을 PC에 적용
  사용법 (PowerShell):
    1) 점검만(기본, 아무것도 바꾸지 않음):   .\blog-sync.ps1
    2) 점검 + 적용:                           .\blog-sync.ps1 -Fix
  실행이 막히면 먼저:  Set-ExecutionPolicy -Scope Process Bypass
#>
param(
  [switch]$Fix,
  [string]$Root = "C:\Users\win\Documents\Claude"
)

$ErrorActionPreference = "Stop"
$Blog  = Join-Path $Root "blog"
$Sched = Join-Path $Root "Scheduled"
$Stamp = Get-Date -Format "yyyyMMdd-HHmmss"
$Utf8NoBom = New-Object System.Text.UTF8Encoding($false)

function Say($msg, $color = "Gray") { Write-Host $msg -ForegroundColor $color }
function Title($msg) { Write-Host ""; Write-Host "=== $msg ===" -ForegroundColor Cyan }

# ─────────────────────────────────────────────
Title "1. 로컬 저장소를 GitHub main 과 맞추기"
# ─────────────────────────────────────────────
if (-not (Test-Path (Join-Path $Blog ".git"))) {
  Say "❌ $Blog 가 git 저장소가 아닙니다. 경로를 확인하세요 (-Root 로 바꿀 수 있음)." Red
  exit 1
}
if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
  Say "❌ git 이 설치돼 있지 않습니다. https://git-scm.com 에서 설치 후 다시 실행하세요." Red
  exit 1
}

Push-Location $Blog
try {
  $branch = (git rev-parse --abbrev-ref HEAD).Trim()
  $dirty  = git status --porcelain
  Say "현재 브랜치: $branch"
  if ($dirty) {
    Say "⚠️ 로컬에 커밋 안 된 변경이 있습니다:" Yellow
    $dirty | ForEach-Object { Say "   $_" Yellow }
  } else {
    Say "로컬 변경 없음."
  }

  git fetch origin main 2>&1 | Out-Null
  $behind = (git rev-list --count "HEAD..origin/main").Trim()
  $ahead  = (git rev-list --count "origin/main..HEAD").Trim()
  Say "main 대비: 뒤처진 커밋 $behind 개 / 앞선 커밋 $ahead 개"

  if ($Fix) {
    if ($dirty) {
      # 로컬 변경은 지우지 않고 백업 폴더 + git stash 에 보관
      $bk = Join-Path $Root "blog_backup_$Stamp"
      New-Item -ItemType Directory -Path $bk | Out-Null
      git status --porcelain | ForEach-Object {
        $f = $_.Substring(3).Trim('"')
        $src = Join-Path $Blog $f
        if (Test-Path $src -PathType Leaf) {
          $dst = Join-Path $bk $f
          New-Item -ItemType Directory -Path (Split-Path $dst) -Force | Out-Null
          Copy-Item $src $dst
        }
      }
      git stash push -u -m "blog-sync 자동 보관 $Stamp" | Out-Null
      Say "로컬 변경을 $bk 와 git stash 에 보관했습니다 (되살리기: git stash pop)." Yellow
    }
    if ($branch -ne "main") { git checkout main | Out-Null; Say "main 브랜치로 전환했습니다." }
    git pull --ff-only origin main
    if ($LASTEXITCODE -ne 0) {
      Say "❌ pull 실패 (로컬 main 에 GitHub 에 없는 커밋이 있음). 이 화면을 Claude 에게 보여 주세요." Red
      exit 1
    }
    Say "✅ main 최신본으로 맞췄습니다." Green
  } elseif ([int]$behind -gt 0 -or $dirty) {
    Say "→ -Fix 로 다시 실행하면 맞춥니다." Yellow
  }

  # 개정 반영 확인
  $checks = @(
    @{f="0and1Life-Writer.md";        p="900~1,300어절"},
    @{f="KoreaPlug-Writer.md";        p="900~1,300 단어"},
    @{f="Routine_0and1Life-Writer.md";p="모바일 점검"},
    @{f="Routine_KoreaPlug-Writer.md";p="모바일 점검"},
    @{f="0and1Life-Draft.md";         p="Phase 5-7. 📱"},
    @{f="KoreaPlug-Draft.md";         p="5-7. 📱"},
    @{f="Schd_0and1Life-Draft.md";    p="[6k-M]"},
    @{f="Schd_KoreaPlug-Draft.md";    p="[6k-M]"},
    @{f="Schd_KoreaPlug-Revenue.md";  p="1,300단어"}
  )
  Say ""
  Say "개정 반영 여부 (로컬 파일 기준):"
  foreach ($c in $checks) {
    $path = Join-Path $Blog $c.f
    $ok = (Test-Path $path) -and (Select-String -Path $path -SimpleMatch -Pattern $c.p -Encoding UTF8 -Quiet)
    if ($ok) { Say ("  ✅ {0}" -f $c.f) Green } else { Say ("  ❌ {0}  ('{1}' 없음)" -f $c.f, $c.p) Red }
  }
} finally { Pop-Location }

# ─────────────────────────────────────────────
Title "2. Cowork 예약 본문 점검 (사본인지 진입점인지)"
# ─────────────────────────────────────────────
# 어떤 예약이 어떤 저장소 파일을 따라야 하는지 — 각 문서에만 있는 표식으로 판별
$targets = @(
  # marks = 그 문서 본문에만 있는 표식 (Revenue 등 다른 예약이 파일 이름을 언급해도 오판하지 않도록 파일 이름은 쓰지 않는다)
  @{name="0and1Life Draft";  file="Schd_0and1Life-Draft.md";     marks=@("WordPress Draft 업로드 루틴")},
  @{name="KoreaPlug Draft";  file="Schd_KoreaPlug-Draft.md";     marks=@("[6h-L]", "AdSense - KoreaPlug")},
  @{name="KoreaPlug Writer"; file="Routine_KoreaPlug-Writer.md"; marks=@("루틴 : KoreaPlug-Writer")}
)

if (-not (Test-Path $Sched)) {
  Say "⚠️ $Sched 폴더가 없습니다. Cowork 앱에서 예약 3개(0and1Life Draft · KoreaPlug Draft · KoreaPlug Writer)를 직접 열어 확인하세요." Yellow
} else {
  $skills = Get-ChildItem -Path $Sched -Recurse -Filter "SKILL.md" -ErrorAction SilentlyContinue
  Say ("예약 본문 파일 {0}개 발견" -f @($skills).Count)
  $found = @{}
  foreach ($s in $skills) {
    $text  = [IO.File]::ReadAllText($s.FullName, [Text.Encoding]::UTF8)
    $lines = ($text -split "`n").Count
    $match = $null
    foreach ($t in $targets) {
      foreach ($m in $t.marks) { if ($text.Contains($m)) { $match = $t; break } }
      if ($match) { break }
    }
    if (-not $match -and $lines -le 40 -and $text -notmatch "Revenue") {
      # 짧은 진입점 본문: 파일 이름(.md 포함)을 언급하면 그 예약으로 본다
      foreach ($t in $targets) { if ($text.Contains($t.file)) { $match = $t; break } }
    }
    if (-not $match) { continue }
    $found[$match.name] = $true

    $isEntry = ($lines -le 40) -and ($text -match [regex]::Escape($match.file))
    $isNew   = $text -match [regex]::Escape("[6k-M]") -or $text -match "900~1,300"
    $rel = $s.FullName.Substring($Root.Length + 1)
    if ($isEntry) {
      Say ("  ✅ [{0}] {1} — 진입점({2}줄). 할 일 없음." -f $match.name, $rel, $lines) Green
      continue
    }
    if ($isNew) {
      Say ("  ✅ [{0}] {1} — 사본이지만 이미 최신({2}줄)." -f $match.name, $rel, $lines) Green
      continue
    }
    Say ("  ❌ [{0}] {1} — 옛 사본({2}줄). 진입점으로 바꿔야 합니다." -f $match.name, $rel, $lines) Red

    if ($Fix) {
      $ans = Read-Host ("     이 파일을 진입점으로 바꿀까요? 원본은 .bak-{0} 로 보관 (y/n)" -f $Stamp)
      if ($ans -ne "y") { Say "     건너뜀." Yellow; continue }
      # YAML 머리말(--- ... ---)이 있으면 그대로 두고 본문만 바꾼다
      $front = ""
      if ($text -match "(?s)^(---\r?\n.*?\r?\n---\r?\n)") { $front = $Matches[1] }
      $local = Join-Path $Blog $match.file
      $body = @"
# $($match.name) — 실행 진입점

이 예약 작업의 본문은 ``$local`` 이다 (GitHub ``leejc0404/blog`` main 의 ``$($match.file)`` 와 같은 파일).
실행할 때마다 그 파일을 **마지막 줄까지** 읽고, 적힌 절차를 처음부터 끝까지 그대로 수행한다.
규칙을 바꿀 때는 그 파일만 고친다. 이 예약 본문은 바꾸지 않는다.
파일을 읽지 못하면 아무것도 올리거나 고치지 않고, 알림 1회로 사유를 보낸 뒤 끝낸다.
"@
      Copy-Item $s.FullName ("{0}.bak-{1}" -f $s.FullName, $Stamp)
      [IO.File]::WriteAllText($s.FullName, $front + $body, $Utf8NoBom)
      Say "     ✅ 진입점으로 바꿨습니다." Green
    }
  }
  foreach ($t in $targets) { if (-not $found[$t.name]) { Say ("  ⚠️ [{0}] 예약 본문을 찾지 못했습니다 — Cowork 앱에서 직접 열어 확인하세요." -f $t.name) Yellow } }
  Say ""
  Say "※ 3개 중 위에 안 나온 예약이 있으면 Cowork 앱에서 직접 열어 확인하세요 (이름·폴더가 달라 자동 판별을 못 한 경우)." DarkGray
}

# ─────────────────────────────────────────────
Title "3. Draft 가 쓰는 Chrome 로그인 확인"
# ─────────────────────────────────────────────
Say "📱 모바일 점검과 1급 자료 캡처는 Claude in Chrome 이 wp-admin 로그인 상태여야 동작합니다."
if ($Fix) {
  Start-Process "chrome.exe" "https://0and1life.com/wp-admin/"
  Start-Process "chrome.exe" "https://koreaplug.com/wp-admin/"
  Say "→ Chrome 에 두 사이트 wp-admin 을 열었습니다. 로그인 화면이 나오면 로그인해 두세요." Yellow
} else {
  Say "→ -Fix 로 실행하면 두 사이트 wp-admin 을 Chrome 으로 열어 줍니다."
}

Title "끝"
if (-not $Fix) { Say "점검만 했습니다. 바꾸려면:  .\blog-sync.ps1 -Fix" Yellow }
Say "다음 Draft 알림에 '📱 390px:' 줄이 나오면 새 스케줄이 적용된 것입니다."
