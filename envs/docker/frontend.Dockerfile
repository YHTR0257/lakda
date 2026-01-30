# ========================================
# マルチステージビルド: 依存関係インストール
# ========================================
FROM node:22-slim AS dependencies

WORKDIR /app

# package.jsonとpackage-lock.jsonをコピー
COPY frontend/package*.json ./

# 依存関係のインストール
RUN npm install --omit=dev

# ========================================
# マルチステージビルド: 開発用ステージ
# ========================================
FROM node:22-slim AS development

WORKDIR /app

# 依存関係を前のステージからコピー
COPY --from=dependencies /app/node_modules ./node_modules
COPY frontend/package*.json ./

# 開発用依存関係も追加インストール
RUN npm install

# アプリケーションコードのコピー
COPY frontend/src ./src
COPY frontend/public ./public
COPY frontend/next.config.js ./
COPY frontend/tsconfig.json ./
COPY frontend/tailwind.config.ts ./
COPY frontend/postcss.config.js ./

ENV NODE_ENV=development

EXPOSE 3000

CMD ["npm", "run", "dev"]

# ========================================
# マルチステージビルド: ビルドステージ
# ========================================
FROM node:22-slim AS builder

WORKDIR /app

# package.jsonをコピーして全依存関係をインストール（tailwindcss等のdevDependencies含む）
COPY frontend/package*.json ./
RUN npm install

# アプリケーションコードのコピー
COPY frontend/src ./src
COPY frontend/public ./public
COPY frontend/next.config.js ./
COPY frontend/tsconfig.json ./
COPY frontend/tailwind.config.ts ./
COPY frontend/postcss.config.js ./

# Next.jsアプリケーションのビルド
RUN npm run build

# ========================================
# マルチステージビルド: 本番用ステージ
# ========================================
FROM node:22-slim AS production

WORKDIR /app

ENV NODE_ENV=production

# 本番用依存関係のコピー
COPY --from=dependencies /app/node_modules ./node_modules
COPY frontend/package*.json ./

# ビルド成果物のコピー
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/public ./public
COPY --from=builder /app/next.config.js ./

# 非rootユーザーで実行
RUN addgroup --system --gid 1001 nodejs && \
    adduser --system --uid 1001 nextjs && \
    chown -R nextjs:nodejs /app
USER nextjs

EXPOSE 3000

CMD ["npm", "start"]