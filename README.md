# 関数グラフ作成サイト

Python (Flask + Matplotlib) で作った、式からグラフ画像を生成する Web アプリです。

## セットアップ

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## 起動

```bash
python app.py
```

ブラウザで `http://127.0.0.1:5000` を開いてください。

## 使い方

- 式をカンマ区切りで入力（例: `x**2, sin(x), log(x+11)`）
- x 範囲と点数を指定
- 「グラフを生成」を押す
- 生成画像を右クリック保存

## 対応関数

`sin, cos, tan, arcsin, arccos, arctan, sinh, cosh, tanh, exp, log, log10, sqrt, abs`

定数: `pi, e`
