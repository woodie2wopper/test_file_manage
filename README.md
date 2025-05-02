# test_file_manage

### タスク
空のファイルを 100 個作り、{id, filename, timestamp, dir} を SQLite に保存。
FastAPI + React で一覧表示し、ファイル名をインライン編集できる UI を追加

### 受入基準 (Acceptance)
1. `POST /seed` で ./data/ に 100 ファイル生成し DB も 100 行になること。
2. `PUT /file/{id}` で名前変更すると:
   - DB の filename が更新
   - 実ファイルが rename
   - フロントのテーブルが即時更新
3. `pytest` と `pnpm test` がどちらも pass すること。