【ソフト名】　　　将棋AIエンジン  
　　　　　　　　　「十六式いろは煌（きらめき）」  
【バージョン】　　Ver.2022winter-cpu  
【著作権者】　　　末吉 竜介  
【開発者】　　　　末吉 竜介、若月 翔威、畑中 慎吾、李 愚昶、長谷部 太一、  
　　　　　　　　　紺野 誠、若松 萌生、菊池 弘敏、小林 優輝、村越 小友梨、  
　　　　　　　　　上野 勇樹、岩田 大夢、堀内 旺、Chaeyoung Sung  
【制作日】　　　　2023/03/03  
【種　別】　　　　フリーソフトウェア  
【ソースコードのライセンス】　　MIT Licence  
【連絡先】　　　　[末吉のTwitter](https://twitter.com/16shiki168)  
【配布元ページ】　https://github.com/sueyoshiryosuke/16shiki-Iroha_kirameki  
【動作確認環境】　Windows11  
　　　　　　　　　いろは煌盤（きらめきばん）  
　　　　　　　　　　（「十六式いろは煌（きらめき）」の同梱版、非同梱版あり）  
　　　　　　　　　将棋所　　Ver.4.9.2  
　　　　　　　　　ShogiGUI　Ver.0.0.7.26  
【同梱、使用ソフト】  
　DeepLearningShogi 　https://github.com/TadaoYamaoka/DeepLearningShogi/  
　やねうら王+水匠5　　https://github.com/yaneurao/YaneuraOu  
　Ayane 　　　　　　　https://github.com/yaneurao/Ayane  
　WinPython 　　　　https://winpython.github.io/  
　VisualBat 　　　　https://www.vector.co.jp/soft/winnt/prog/se505490.html  
　7-Zip 　　　　　　https://sevenzip.osdn.jp/  
　ShogiGUI　　　　　http://shogigui.siganus.com/  
　BookConv　　　　　https://github.com/ai5/BookConv  
【参考】  
　書籍「強い将棋ソフトの創りかた」著者：山岡忠夫、加納邦彦  
　　　　　　https://book.mynavi.jp/ec/products/detail/id=126887  
　コンピュータ将棋対局場（floodgate）　http://wdoor.c.u-tokyo.ac.jp/shogi/  
  
―――――――――――――――――――――――――――――――――――――  
≪著作権および免責事項≫  
  
　本ソフトはフリーソフトです。個人／団体／社内利用を問わず、ご自由にお使い  
下さい。  
　なお，著作権は上の【著作権者】に記載している者が保有しています。  
  
　このソフトウェアを使用したことによって生じたすべての障害・損害・不具合等に  
関しては、著作権者と著作権者の関係者および著作権者の所属するいかなる  
団体・組織とも、一切の責任を負いません。各自の責任においてご使用ください。  
  
・はじめに  
　　このソフトは、USIプロトコルに対応した将棋GUIに対応した思考エンジンです。  
　Windows11 で動作します。  
  
・ファイル構成  
　16-168-kirameki_2022_avx2.exe  
　　→将棋GUIに登録するときに指定する実行ファイル（VisualBatで作成）  
　setting.bat  
　　→「十六式いろは煌（きらめき）」の設定を変更することができます。  
　readme.txt  
　　→この説明ファイルです。  
　20221203＿十六式いろは煌（きらめき）のアピール文_電竜戦3.pdf  
　　→第3回電竜戦の時のアピール文です。  
　LICENSE.txt  
　　→このソフトのライセンスの内容が書かれています。  
　dlshogiフォルダ  
　　→「十六式いろは煌（きらめき）」で利用する「DeepLearningShogi」を  
　　　同梱しています。  
　　　なお、同梱している学習モデル（model.onnx）のライセンスは  
　　　「クリエイティブ・コモンズ — 表示 4.0 国際 — CC BY 4.0」です。  
　　　　https://creativecommons.org/licenses/by/4.0/legalcode.ja  
　　　詳細は「readme_dlshogi.txt」に記載しています。  
　Suisho5-YO761フォルダ  
　　→「十六式いろは煌（きらめき）」で利用する「やねうら王7.6.1+水匠5」を  
　　　同梱しています。  
　　　定跡ファイル「jouseki_kirameki.db」も同梱しています。 
　　　定跡ファイルの作成者いわく「未完成ですし完成度も低い」とのこと。
　　　詳細は「readme_Suisho5-YO761.txt」に記載しています。  
　kiramekiフォルダ  
　　→「dlshogi」と「やねうら王7.6.1+水匠5」を制御するプログラムです。  
　　　プログラミング言語Pythonを利用するため「WinPython」も同梱しています。  
　　　「Ayane」を一部書き変えた（boundに関する部分を変更）ものを利用しています。  
　　　詳細は「readme_ayane.txt」に記載しています。  
　engine_define.xml  
　　→「いろは煌盤（きらめきばん）」用のファイルです。  
　　　　https://github.com/sueyoshiryosuke/168KIRAMEKI_GUI  
　  
・ダウンロード方法  
　[Releases](https://github.com/sueyoshiryosuke/16shiki-Iroha_kirameki/releases)から  
　ダウンロードできます。  
　  
・インストール方法  
　「16-168-kirameki_2022w.exe」を実行し展開しすると「kiameki」フォルダが  
　作成されます。  
  
・アンインストール方法  
  フォルダごと削除してください。  
  
・使用方法（USIプロトコルに対応した将棋GUIのエンジンとして）  
　フォルダ内の「16-168-kirameki_2022_avx2.exe」を  
　将棋所やShogiGUIのエンジンとして登録してください。  
　設定は「setting.bat」を実行して変更することができます。  
  
・ライセンス  
　各フォルダ内のファイルに記載。  
　ソースコードはMIT licenseです。  
　　Copyright (c) 2022-2023 Ryosuke Sueyoshi  
　　Released under the [MIT license](https://opensource.org/licenses/mit-license.php).  
  
・注意事項  
　NVIDIA社のGPUを搭載していてもGPUは使用しません。  
  
・詳細  
　[第3回電竜戦本戦](https://denryu-sen.jp/dr3/index.html)  
　上記の大会に参加した時の将棋エンジンです。  
　NVIDIA社のGPUを搭載していないパソコンでも動作するようにしています。  
　大会当日のものよりも棋力は下がります。  
　なお、7-Zipで自己解凍形式に変換し、配布するファイルにしました。  
  
・最後に  
　　日本工学院専門学校蒲田校ITカレッジAIシステム科2期生の学生と共に  
　作成することができて、いろいろと挑戦できました。学生の皆さんありがとう。  
　　また、山岡さん、加納さん、やねうらおさん、たややんさん、その他  
　多くの将棋AI開発者の努力と知識による結晶が、今日の将棋AIとなっており  
　その結晶を利用させていただけることに感謝、感謝、感謝です。  
　　そして、本作品によって少しでも将棋ソフトに興味を持っていただき  
　楽しんでいただければ幸いです。  
  
・更新履歴  
　Ver.2022winter-cpu　　2023/03/03  
　　初版公開。  
  
--以上--  
