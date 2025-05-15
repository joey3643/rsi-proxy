from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

@app.route('/rsi', methods=['GET'])
def get_rsi():
    symbol = request.args.get('symbol', 'ETHUSDT')
    url = f'https://api.bybit.com/v5/market/kline?category=linear&symbol={symbol}&interval=5&limit=100'

    try:
        res = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=5)
        
        # 응답이 JSON이 아니면 예외 처리
        if not res.text.strip().startswith('{'):
            return jsonify({'error': 'Invalid response from Bybit', 'content': res.text}), 502

        data = res.json()

        candles = data.get("result", {}).get("list", [])
        if len(candles) < 15:
            return jsonify({'error': 'Not enough data'})

        closes = [float(c[4]) for c in candles[-15:]]

        gains = losses = 0
        for i in range(1, len(closes)):
            diff = closes[i] - closes[i - 1]
            if diff > 0:
                gains += diff
            else:
                losses -= diff

        avg_gain = gains / 14
        avg_loss = losses / 14
        rs = avg_gain / avg_loss if avg_loss != 0 else 0
        rsi = 100 - (100 / (1 + rs)) if avg_loss != 0 else 100

        return jsonify({
            'symbol': symbol,
            'rsi': round(rsi, 2),
            'last_close': closes[-1]
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)

