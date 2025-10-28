## 目的
このリポジトリはWindowsの名前付きパイプを使った「増分検索フィルタ」サーバとテストクライアントを実装しています。
このファイルはリポジトリ内で作業するAIコーディングエージェント向けに、重要なアーキテクチャ、ワークフロー、慣習、具体例を短くまとめたものです。

## 主要コンポーネント（参照ファイル）
- サーバ: `src/server.py` — Windows API（pywin32）を使う名前付きパイプの同期サーバ。単一スレッド、同時接続は想定していない。
- クライアント: `src/client.py` — tkinter を使ったテストクライアント。UIはメインスレッド、通信は背景スレッドで初期化。
- コアロジック: `src/search_filter.py` — プラットフォーム非依存の増分検索ロジック。ここはユニットテスト（`tests/test_search.py`）で検証される。
- 設定: `config.toml` — パイプ名、エンコーディング、case_sensitive の設定を読む（`tomli` を使用）。

## 「なぜ」この構成か（短く）
- 名前付きパイプはWindowsローカルでの低レイテンシ双方向通信に適しているため、ローカルのクライアント/サーバで使う設計にしている。
- 検索ロジックを `search_filter.py` に分離することで、Windows固有部分（パイプ、tkinter UI）をテストから切り離し、単体テストを容易にしている。

## 通信プロトコル（必読・具体例）
- すべてJSONを改行で区切って送受信するメッセージベース（文字列は改行終端）。
- 初期化例（クライアント→サーバ）:
  ```json
  {"type":"init","filename":"C:\\path\\to\\file.txt"}
  ```
  サーバ応答例:
  ```json
  {"status":"ok","line":"first line"}
  ```
- 検索更新例:
  ```json
  {"type":"search","pattern":"text"}
  ```
- 選択移動例:
  ```json
  {"type":"move","delta":1}
  ```

※ エージェントがメッセージを生成する際は、必ずJSON構造と改行終端を守ってください（`src/server.py` の Read/Write 実装に依存）。

## 開発ワークフロー・コマンド
- 依存インストール: `pip install -r requirements.txt`
- サーバ起動: `python src/server.py --config-filename config.toml`（Windows 上で実行）
- クライアント起動: `python src/client.py --config-filename config.toml`（別ターミナル）
- テスト実行（Platform-independent）: `python -m unittest tests/test_search.py -v` — このテストはpywin32不要で、`search_filter.py`の動作だけ検証する。
- 簡易スクリプト: `start_server.bat` / `start_client.bat` を参照（Windows 用）。

## プロジェクト固有の注意点・慣習
- Windows限定の依存 (pywin32) があるため、サーバ/クライアントは基本的にWindows上でしか動作しない。
- テストはプラットフォーム独立部（`search_filter.py`）に限定されており、CIでクロスプラットフォーム実行が可能。
- import のスタイル: 実行ファイルは `from search_filter import IncrementalSearchFilter` と相対にインポートしている。テストは `sys.path` を操作して `src` を先頭に追加している点に注意。
- 設定は TOML（`tomli`）で読み込む。エンコードは config の `encoding.default` を使う。

## コード生成・変更時の具体的ルール（AI向け）
1. サーバ側の変更が必要な場合は、まず `src/search_filter.py` のみに影響があるか検討し、ユニットテストを追加/更新すること。
2. 名前付きパイプ周りのメッセージの読み書き形式（JSON + 改行）を変えるなら、クライアント実装と `tests` にも必ず反映する。
3. Windows API 呼び出し（`win32pipe`, `win32file`）に変更を加える場合、ローカルWindowsでの手動確認手順を `README.md` に追記すること。

## 追加参照（実例を探したいとき）
- プロトコル実装: `src/server.py` の `handle_client` / `send_message` ロジック
- UI とイベント結合: `src/client.py` の `on_search_change` + `root.after` パターン
- 検索ロジック： `src/search_filter.py` の `update_filter` / `move_selection`

---
フィードバックください：不明確な点や追加してほしい「例（例えば典型的なJSON通信ログ）」があれば指示をください。更新してマージします。
