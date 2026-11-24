FROM nginx:1.27-alpine
# Build the Vite bundle with `pnpm build` before containerizing. Keeping the
# runtime image network-independent makes local/offline demonstrations reliable.
COPY dist /usr/share/nginx/html
EXPOSE 80
