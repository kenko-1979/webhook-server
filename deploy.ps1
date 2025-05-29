param(
    [Parameter(Mandatory=$true)]
    [string]$CommitMessage
)

# エラーが発生した場合に停止
$ErrorActionPreference = "Stop"

# 現在のディレクトリを保存
$currentDir = Get-Location

try {
    # mainブランチにいることを確認
    $branch = git rev-parse --abbrev-ref HEAD
    if ($branch -ne "main") {
        Write-Host "❌ mainブランチにいません。現在のブランチ: $branch" -ForegroundColor Red
        exit 1
    }

    # 変更状態を確認
    $status = git status --porcelain
    if (-not $status) {
        Write-Host "❌ コミットする変更がありません" -ForegroundColor Yellow
        exit 0
    }

    # 変更をステージングに追加
    Write-Host "📝 変更をステージングに追加中..." -ForegroundColor Yellow
    git add .
    if ($LASTEXITCODE -ne 0) { throw "git add failed" }

    # 変更をコミット
    Write-Host "💾 変更をコミット中..." -ForegroundColor Yellow
    git commit -m $CommitMessage
    if ($LASTEXITCODE -ne 0) { throw "git commit failed" }

    # 変更をプッシュ
    Write-Host "🚀 変更をプッシュ中..." -ForegroundColor Yellow
    git push
    if ($LASTEXITCODE -ne 0) { throw "git push failed" }

    Write-Host "✅ デプロイが完了しました！" -ForegroundColor Green
    Write-Host "Renderが自動的にデプロイを開始します。数分お待ちください。" -ForegroundColor Cyan
    Write-Host "デプロイの進捗は以下のURLで確認できます：" -ForegroundColor Cyan
    Write-Host "https://dashboard.render.com/" -ForegroundColor Blue
}
catch {
    Write-Host "❌ エラーが発生しました：" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    exit 1
}
finally {
    # 元のディレクトリに戻る
    Set-Location $currentDir
} 