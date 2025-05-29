#!/bin/bash

# エラーが発生したら停止
set -e

# 色の定義
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# コミットメッセージを取得
if [ $# -eq 0 ]; then
    echo -e "${RED}❌ コミットメッセージを指定してください${NC}"
    echo "使用方法: ./deploy.sh \"コミットメッセージ\""
    exit 1
fi

COMMIT_MESSAGE="$1"

# mainブランチにいることを確認
CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
if [ "$CURRENT_BRANCH" != "main" ]; then
    echo -e "${RED}❌ mainブランチにいません。現在のブランチ: $CURRENT_BRANCH${NC}"
    exit 1
fi

# 変更状態を確認
if [ -z "$(git status --porcelain)" ]; then
    echo -e "${YELLOW}⚠️ コミットする変更がありません${NC}"
    exit 0
fi

# 変更をステージングに追加
echo -e "${YELLOW}📝 変更をステージングに追加中...${NC}"
git add .

# 変更をコミット
echo -e "${YELLOW}💾 変更をコミット中...${NC}"
git commit -m "$COMMIT_MESSAGE"

# 変更をプッシュ
echo -e "${YELLOW}🚀 変更をプッシュ中...${NC}"
git push

echo -e "${GREEN}✅ デプロイが完了しました！${NC}"
echo -e "${BLUE}Renderが自動的にデプロイを開始します。数分お待ちください。${NC}"
echo -e "${BLUE}デプロイの進捗は以下のURLで確認できます：${NC}"
echo -e "${BLUE}https://dashboard.render.com/${NC}" 