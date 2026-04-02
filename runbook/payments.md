# Payment Service Runbook

## DB_CONNECTION_TIMEOUT
**Symptoms:** Logs containing `Database connection timeout at <IP>`.

**Action:**
1. Check RDS CPU metrics in Datadog.
2. Verify Security Group ingress rules for port 5432.
3. Restart the `payment-worker` pod.

## GATEWAY_LATENCY_HIGH
**Symptoms:** Logs containing `Gateway latency high: <TIME>`.

**Action:** Check the status page of the third-party provider (Stripe/Adyen).