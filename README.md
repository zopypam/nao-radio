# なおラジオ

Museが監視・報告しているものを全部、キャラクターが読み上げる個人ラジオ局。
AIニュース、世界情勢、図書館の新着、出版予定の本、関西イベント、新しい音楽などを、コーナーごとにまとめて毎朝放送する。

- プレーヤーは [myradio](https://github.com/monoradio102/myradio)（ものラジオ）の仕組みを利用
- 声：VOICEVOX:冥鳴ひまり
- 話す文は中立に、皮肉は時々。ルールは `STYLE.md`
- 台本（`episodes/`）と音声（直近30日分だけ Pages 側に公開）で放送する

## 運用

- 毎朝、監視側の最新レポートから台本JSONを組み、`tools-local/build_episode.py` で音声合成して `tools/publish.sh` で公開する
- 音声は main ブランチに入れない（publish.sh が gh-pages を作り直す）
