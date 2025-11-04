FROM node:18-alpine

WORKDIR /app

# 复制package.json和安装依赖
COPY frontend/package.json .
COPY frontend/package-lock.json .
RUN npm install

# 复制源代码
COPY frontend/ .

EXPOSE 3000

CMD ["npm", "start"]