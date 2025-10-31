# SekaiOverlay
某セカイ風の動画をAviUtl2で作るためのツール・スクリプトです。
GUI上で特定のサーバーの譜面IDを入力すると、背景の生成から動画用UIの生成までをほとんど自動で行います。
これにより、創作譜面の動画などをより本家らしく見せることが可能です。

## 注意
これはまだ開発途上のツールです。
不具合等がありましたらこのリポジトリのIssuesか、Discordにてお願いします。

> [!CAUTION]
> Notice for English Users
> This tool currently supports **Japanese only.**
> You can still try to use it, but please be aware that there may be risks or unexpected behavior.
> 
> Also, **please do not ask questions about this tool** in fan communities such as the 
> **ChartCyanvas**, **UntitledCharts**, or **NextSEKAI** Discord servers.
> This is just a **small personal project**, not an officially supported tool.

## 必要な物
- [AviUtl ExEdit2](https://spring-fragrance.mints.ne.jp/aviutl/) (beta17での動作を確認済み)
- AviUtl2に関する基本的な知識
- [L-SMASH-Works](https://github.com/Mr-Ojii/L-SMASH-Works-Auto-Builds/releases/latest) (Mr-Ojii_vimeoを推奨)

## 使い方
1. [Release](https://github.com/Hallkun19/SekaiOverlay/releases/latest)ページからSekaiOverlay.zipをダウンロード、任意の場所に解凍（_internalフォルダも忘れずに）
2. SekaiOverlay.exeを起動
3. 開いたウィンドウで楽曲などの情報を入力
4. 生成開始ボタンを押下
5. エイリアスの生成が完了すると、フォルダが開きます
6. AviUtl2を開き、1920x1080, 60fpsで新規プロジェクトを作成します
7. 5で開いたフォルダの"main.object"をAviUtl2のタイムラインにドラッグします
8. AP演出の位置や、テキストの調整をして完成です

## カスタマイズ
### InitSettings@SekaiObjects
#### skobj data
ここで任意の曲のskobj_data.jsonを選択することによって、アニメーションの挙動を変更できます
#### offset
この値を調整することによって、全体のアニメーションのオフセットを変更できます
#### ignore cache
skobj dataの読み込みのキャッシュを無視するかを選択できます

### Combo@SekaiObjects
#### AP
AP演出を1でON、0でオフにすることができます
#### X Area Expand
この値を増やすことにより、桁数が多いときなどに途切れたような見た目になることを防げます

### Score@SekaiObjects
#### Max Digit
スコアを表示する最大桁数を変更できます
#### Animation Speed
スコアが増加するアニメーションの速度を変更できます
#### X Area Expand
この値を増やすことにより、桁数が多いときなどに途切れたような見た目になることを防げます

### Life@SekaiObjects
#### Life
表示するライフの値を変更できます

### Judgement@SekaiObjects
#### Judge
1でPERFECT、2でGREAT、3でGOOD、4でBAD、5でMISS、6でAUTOを表示できます

## 利用規約
1. このツール・スクリプトを使ったことによるトラブルや不利益などが発生しても、作者は**一切の責任を負いません。**
2. 決して**悪意のある使用を**しないでください。（SNS上でデマを流すために使う等）
3. このツール・スクリプトを使用して作成した動画をSNSなどに投稿する場合は必ず、**`はるくん`・`@halkun19`** という名前・IDと「これは**某セカイ風の動画**であり、**本家ではない**」とわかることを明確に記載してください。

**例：**
```
※この動画はファンメイドであり、非公式のものです
動画作成ツール：はるくん(@halkun19)
```

## 謝辞
[名無し｡](https://github.com/sevenc-nanashi)氏の[pjsekai-overlay](https://github.com/sevenc-nanashi/pjsekai-overlay)と[pjsekai-background-gen-rust](https://github.com/sevenc-nanashi/pjsekai-background-gen-rust)を参考にさせていただきました。この場をお借りして感謝申し上げます。