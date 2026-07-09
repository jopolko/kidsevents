#!/bin/bash
# Check server's public IP address
# Run this if you suspect your IP changed

echo "🌐 Checking your server's public IP address..."
echo ""

PUBLIC_IP=$(curl -s ifconfig.me)

echo "Your public IP: $PUBLIC_IP"
echo ""
echo "✓ Use this IP in Google Cloud Console:"
echo "  https://console.cloud.google.com/apis/credentials"
echo ""
echo "✓ Current configuration in .env file"
echo "  (API key is hidden for security)"
grep -v "=" /var/www/html/kidsevents/.env | head -5
echo ""

# Compare with known IP (optional)
EXPECTED_IP="143.110.236.86"
if [ "$PUBLIC_IP" == "$EXPECTED_IP" ]; then
    echo "✅ IP matches expected value ($EXPECTED_IP)"
else
    echo "⚠️  WARNING: IP has changed!"
    echo "   Old IP: $EXPECTED_IP"
    echo "   New IP: $PUBLIC_IP"
    echo "   You MUST update Google Cloud Console!"
fi
