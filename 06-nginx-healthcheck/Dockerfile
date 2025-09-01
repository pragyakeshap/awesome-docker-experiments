# Nginx with custom health check configuration
FROM nginx:alpine

# Install curl for health checks
RUN apk add --no-cache curl

# Copy custom nginx configuration
COPY nginx.conf /etc/nginx/nginx.conf
COPY health.html /usr/share/nginx/html/health.html

# Copy custom health check script
COPY health-check.sh /usr/local/bin/health-check.sh
RUN chmod +x /usr/local/bin/health-check.sh

# Create non-root user for nginx
RUN addgroup -g 1000 -S nginx-group && \
    adduser -u 1000 -D -S -G nginx-group nginx-user

# Set proper permissions
RUN chown -R nginx-user:nginx-group /var/cache/nginx /var/run /var/log/nginx /usr/share/nginx/html

# Expose port
EXPOSE 8080

# Health check with custom script
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD /usr/local/bin/health-check.sh

# Switch to non-root user
USER nginx-user

# Start nginx
CMD ["nginx", "-g", "daemon off;"]
