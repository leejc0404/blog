param([string]$m = "")

# ── 설정 ────────────────────────────────────────────
$repo   = if ($PSScriptRoot) { $PSScriptRoot } else { "C:\Users\win\Documents\Claude\blog" }
$branch = "main"
# ──────────────────────────────────────────────────────

$OutputEncoding = [Console]::OutputEncoding = [Text.Encoding]::UTF8

if (-not (Test-Path $repo)) {
    Write-Host "폴더를 찾을 수 없습니다: $repo" -ForegroundColor Red
    exit 1
}

Set-Location $repo

if (-not (Test-Path ".git")) {
    Write-Host ".git 폴더가 없습니다. 먼저 아래를 실행하세요:" -ForegroundColor Red
    Write-Host "  git init" -ForegroundColor Yellow
    Write-Host "  git branch -M $branch" -ForegroundColor Yellow
    Write-Host "  git remote add origin https://github.com/leejc0404/blog.git" -ForegroundColor Yellow
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
        Write-Host "git 프로세스가 실행 중입니다. 종료한 뒤 다시 실행하세요." -ForegroundColor Red
        exit 1
    }
    foreach ($l in $found) {
        Remove-Item $l -Force -ErrorAction SilentlyContinue
        Write-Host "잔여 lock 제거: $l" -ForegroundColor DarkYellow
    }
}

# ── 1단계: 커밋 ──
git add -A

if (git status --porcelain) {
    Write-Host "" 
    Write-Host "[커밋 대상]" -ForegroundColor Cyan
    git status --short

    git commit -m $m
    if ($LASTEXITCODE -ne 0) {
        Write-Host "커밋 실패." -ForegroundColor Red
        exit 1
    }
    Write-Host "커밋 완료: $m" -ForegroundColor Green
} else {
    Write-Host "새로 커밋할 변경사항은 없습니다." -ForegroundColor Yellow
}

# ── 2단계: 푸시 (이미 만들어진 커밋도 함께 올라간다) ──
git fetch origin $branch 2>$null
$ahead = @(git rev-list "origin/$branch..$branch" 2>$null).Count

if ($ahead -eq 0) {
    Write-Host "원격과 이미 동일합니다. 푸시할 것이 없습니다." -ForegroundColor Yellow
    exit 0
}

Write-Host ""
Write-Host "[푸시할 커밋 $ahead개]" -ForegroundColor Cyan
git log --oneline "origin/$branch..$branch"

git push origin $branch
if ($LASTEXITCODE -eq 0) {
    Write-Host "푸시 완료 ($ahead개 커밋)" -ForegroundColor Green
} else {
    Write-Host "푸시 실패. 원격 저장소 주소와 GitHub 인증을 확인하세요." -ForegroundColor Red
    exit 1
}
