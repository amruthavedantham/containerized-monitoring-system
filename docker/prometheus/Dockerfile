FROM prom/prometheus:latest

COPY monitoring/prometheus/config/prometheus.yml /etc/prometheus/prometheus.yml
COPY monitoring/prometheus/rules/alert_rules.yml /etc/prometheus/alert_rules.yml

EXPOSE 9090
