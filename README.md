# なおラジオ

Museが監視・報告しているものを全部、キャラクターが読み上げる個人ラジオ局。
世界情勢を中心に、その日のニュースをコーナーごとにまとめて毎朝放送する。こちらは形式紹介のためのデモ版です。

- プレーヤーは [myradio](https://github.com/monoradio102/myradio)（ものラジオ）の仕組みを利用
- 声：VOICEVOX:冥鳴ひまり
- 話す文は中立に、皮肉は時々。ルールは `STYLE.md`
- 台本（`episodes/`）と音声（直近30日分だけ Pages 側に公開）で放送する

## 運用

- 毎朝、監視側の最新レポートから台本JSONを組み、`tools-local/build_episode.py` で音声合成して `tools/publish.sh` で公開する
- 音声は main ブランチに入れない（publish.sh が gh-pages を作り直す）
