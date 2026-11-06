# コーナー接続マップ

毎朝の自動放送ジョブ（nao-radio-daily-broadcast）が各コーナーの材料をどこから取るかの正本。
共通ルール：前回の放送以降に新しい材料が出ているコーナーだけを入れる。材料が無ければそのコーナーは作らない（無いものを読み上げない）。各コーナー2〜5項目まで。項目には出典リンクを付け、画像があるものは元の画像URLをスライドにする（取れなければ無理に付けない）。

## AIニュース（必須・接続済み）
- ソース: `~/workspace/goals/ai-2/hidden_files/ai-news-catalog.json` の最新日エントリ
- 抽出: タイトル、要約、出典URL、OGP画像URL。主要4〜6本。

## 世界情勢（接続済み）
- ソース: `~/workspace/world-monitor/reports/` の最新レポート（`YYYY-MM-DD-morning.md` / `-evening.md` のうち新しい方）
- 抽出: 主要項目の見出しと1〜2文の要約。3〜5本。レポート内の出典リンクを流用する。

## 図書館の新着（接続済み）
- ソース: `~/workspace/goals/library-new-arrivals-discovery/hidden_files/import-books-YYYY-MM-DD.json` の最新ファイル（books 配列）
- 抽出: タイトル、著者、出版社、説明文からの一言、OPACのURL。利用者の関心に合いそうなものを3〜5冊（台帳の note や説明を見て選ぶ）。

## 出版予定の本（接続済み）
- ソース: `~/workspace/goals/upcoming-books-discovery/hidden_files/run-YYYY-MM-DD.log` の最新ファイル
- 抽出: 書名、著者、出版社、発売日、出典リンク。3〜5本。週3回（月・水・金）の監視なので、新しいログがある日だけ。

## 関西イベント（接続済み）
- ソース: `~/workspace/goals/kansai-events-discovery/hidden_files/run-YYYY-MM-DD.md` の最新ファイル（週1回監視）
- 抽出: イベント名、日時、会場、チケット情報、出典リンク。2〜4件。新しい run がある週だけ。

## メディア発掘（接続済み）
- ソース: `~/workspace/goals/media-discovery-recommendations/hidden_files/` の最新の `run-*.md` または `*-topics.md`
- 抽出: 作品名、種別（映画・ドラマ等）、推薦理由の一言、出典リンク。2〜4件。週2回の監視なので新しい材料がある日だけ。

## 新しい音楽（接続済み）
- ソース: `~/workspace/music-discovery/catalog.json` の releases（週次ジョブ「知らないアーティストの曲の発見」が推薦済み楽曲を記録している台帳）
- 抽出: discovered_date が前回の放送以降のものを、アーティスト名、曲名、fit_reason（推薦理由）、youtube_url で。2〜4曲。週1回の監視なので新しい推薦がある週だけ。

## p2ptk（接続済み）
- ソース: `~/workspace/goals/p2ptk-org/hidden_files/radio-ledger.json` の items（p2ptk新着フックが検出のたびに追記する台帳。2026-11-06 に記録を開始したので、それ以前の記事は入っていない）
- 抽出: 前回の放送以降に追加された記事を、タイトル、投稿日、要約、URL で。1〜3本。新着が無い期間はコーナー自体を作らない。

## 表情タグ（expr）— 台本specの任意項目
- ニュース項目に `"expr": "<名前>"` を付けると、その項目を読み上げている間、キャスターの全身フレームがその表情カットに切り替わる（スライドの切り替わりと同時）。`"opening_expr"` / `"closing_expr"` も可。タグなしの既定は opening=energetic、closing=closing、ニュース=標準リグ（口パク・瞬きあり）。
- 使える名前（character/character.json の frames）: serious（真剣）/ reading（原稿読み）/ breaking（速報）/ energetic（元気）/ laughing（大笑い）/ warm（温かい微笑）/ surprised（驚き）/ puzzled（困惑）/ skeptical（懐疑）/ embarrassed（照れ）/ listening（聞き役）/ apologetic（謝罪・訂正）/ disappointed（残念）/ sorrowful（沈痛）/ gloomy（影）/ sleepy（眠い）
- 付け方の目安: 内容に合うときだけ付ける。真剣な話題には serious / sorrowful、謝罪や訂正には apologetic、明るい話題には warm / laughing、速報には breaking。全部の項目に付ける必要はない（標準リグが既定）。
