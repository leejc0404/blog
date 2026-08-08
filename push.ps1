param([string]$m = "")

# ── 설정 ─────────────────────────────────────────────
$repo   = "C:\Users\win\.claude\blog"
$branch = "main"
# ────────────────────────────────────────────────────

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
    Write-Host "  git remote add origin https://github.com/사용자명/저장소명.git" -ForegroundColor Yellow
    exit 1
}

if ([string]::IsNullOrWhiteSpace($m)) {
    $m = "update " + (Get-Date -Format "yyyy-MM-dd HH:mm")
}

git add -A

if (-not (git status --porcelain)) {
    Write-Host "변경사항이 없습니다." -ForegroundColor Yellow
    exit 0
}

Write-Host "커밋 대상:" -ForegroundColor Cyan
git status --short

git commit -m $m
if ($LASTEXITCODE -ne 0) {
    Write-Host "커밋 실패." -ForegroundColor Red
    exit 1
}

git push origin $branch
if ($LASTEXITCODE -eq 0) {
    Write-Host "푸시 완료: $m" -ForegroundColor Green
} else {
    Write-Host "푸시 실패. 원격 저장소 주소와 GitHub 인증을 확인하세요." -ForegroundColor Red
    exit 1
}
