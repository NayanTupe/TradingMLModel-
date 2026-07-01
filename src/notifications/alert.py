"""
Send trading alerts via Telegram or Slack.
"""

import requests
import logging

logger = logging.getLogger(__name__)

class AlertManager:
    def __init__(self, config):
        self.telegram_token = config.get('telegram_bot_token')
        self.telegram_chat_id = config.get('telegram_chat_id')
        self.slack_webhook = config.get('slack_webhook')
        self.enable_slack = config.get('enable_slack', False)
    
    def send_telegram(self, message):
        if not self.telegram_token or not self.telegram_chat_id:
            logger.warning("Telegram credentials missing")
            return
        url = f"https://api.telegram.org/bot{self.telegram_token}/sendMessage"
        payload = {'chat_id': self.telegram_chat_id, 'text': message, 'parse_mode': 'Markdown'}
        try:
            r = requests.post(url, json=payload, timeout=5)
            if r.status_code != 200:
                logger.error(f"Telegram send failed: {r.text}")
        except Exception as e:
            logger.error(f"Telegram exception: {e}")
    
    def send_slack(self, message):
        if not self.enable_slack or not self.slack_webhook:
            return
        payload = {'text': message}
        try:
            requests.post(self.slack_webhook, json=payload, timeout=5)
        except Exception as e:
            logger.error(f"Slack exception: {e}")
    
    def send_alert(self, message):
        """Send alert to all configured channels."""
        self.send_telegram(message)
        self.send_slack(message)
        logger.info(f"Alert sent: {message}")

# Example usage:
# alert = AlertManager(config['alerts'])
# alert.send_alert(f"🔔 New trade signal for {stock} at {price}")