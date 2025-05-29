# エラー発生時に停止
$ErrorActionPreference = "Stop"

# 色の定義
$Red = "`e[31m"
$Green = "`e[32m"
$Yellow = "`e[33m"
$Blue = "`e[34m"
$Reset = "`e[0m"

# コミットメッセージを取得
if ($args.Count -eq 0) {
    Write-Host "${Red}❌ コミットメッセージを指定してください${Reset}"
    Write-Host "使用方法: .\deploy.ps1 'コミットメッセージ'"
    exit 1
}

$CommitMessage = $args[0]

# mainブランチにいることを確認
$CurrentBranch = git rev-parse --abbrev-ref HEAD
if ($CurrentBranch -ne "main") {
    Write-Host "${Red}❌ mainブランチにいません。現在のブランチ: $CurrentBranch${Reset}"
    exit 1
}

# 変更状態を確認
$Status = git status --porcelain
if ([string]::IsNullOrEmpty($Status)) {
    Write-Host "${Yellow}⚠️ コミットする変更がありません${Reset}"
    exit 0
}

# 変更をステージングに追加
Write-Host "${Yellow}📝 変更をステージングに追加中...${Reset}"
git add .

# 変更をコミット
Write-Host "${Yellow}💾 変更をコミット中...${Reset}"
git commit -m $CommitMessage

# 変更をプッシュ
Write-Host "${Yellow}🚀 変更をプッシュ中...${Reset}"
git push

Write-Host "${Green}✅ デプロイが完了しました！${Reset}"
Write-Host "${Blue}Renderが自動的にデプロイを開始します。数分お待ちください。${Reset}"
Write-Host "${Blue}デプロイの進捗は以下のURLで確認できます：${Reset}"
Write-Host "${Blue}https://dashboard.render.com/${Reset}" 