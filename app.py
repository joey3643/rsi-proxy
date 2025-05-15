from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

@app.route('/rsi', methods=['GET'])
def get_rsi():
    try:
        symbol = request.args.get('symbol', 'ETHUSDT')
        limit = 15
        url = f'https://api.bybit.com/v5/market/kline?category=linear&symbol={symbol}&interval=5&limit={limit}'

        response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})

        # 빈 응답 또는 오류 상태 확인
        if response.status_code != 200:
            return jsonify({'error': f'Status code {response.status_code}', 'body': response.text}), 500

        if not response.text.strip():
            return jsonify({'error': 'Empty response from Bybit'}), 500

        data = response.json()

        if 'result' not in data or 'list' not in data['result']:
            return jsonify({'error': 'Invalid response format', 'raw': data}), 500

        closes = [float(row[4]) for row in reversed(data['result']['list'])]

        if len(closes) < 15:
            return jsonify({'error': 'Not enough data'}), 400

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

