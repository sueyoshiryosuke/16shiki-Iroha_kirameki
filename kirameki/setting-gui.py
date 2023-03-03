import PySimpleGUI as sg
import os
import datetime
import logging
import setting
import setting_default


# ログ出力の設定
log_file_path = 'setting.log'
fmt = "%(asctime)s %(levelname)s %(name)s :%(message)s"
logging.basicConfig(level=logging.INFO, format=fmt, filename=log_file_path)
# logのファイルの更新日時が1週間以上経っていると削除する。
log_file_time = datetime.datetime.fromtimestamp( os.path.getmtime(log_file_path) )
limit_datetime = log_file_time + datetime.timedelta(weeks=1)
now_datetime = datetime.datetime.now()
if now_datetime > limit_datetime:
    logging.info("logの更新日時が1週間以上経っているのでlogファイルを削除しました。: 現時刻:{} 更新日時:{}".format(now_datetime, log_file_time) )
logging.info("十六式いろは煌（きらめき）の設定画面を起動しました。")

# フォント
font_family = "UD デジタル 教科書体"
font_size   = 13

# ウィンドウのテーマ
sg.theme('LightGray1')

#設定のファイルパス
setting_file = r"setting.py"

# ファイル外、ここではsetting.pyでの変数の設定
engine_name = setting.engine_name  # エンジン名
engine_author = setting.engine_author  # エンジン制作者名
setting_early_stage = setting.early_stage
setting_early_stage_think_time = setting.early_stage_think_time
setting_middle_stage1 = setting.middle_stage1
setting_middle_stage1_think_time = setting.middle_stage1_think_time
setting_middle_stage2 = setting.middle_stage2
setting_ponder_early_think_time = setting.ponder_early_think_time
setting_ponder_think_time = setting.ponder_think_time

# setting_default.py（初期値）の読み込み。
default_engine_name = setting_default.engine_name  # エンジン名
default_engine_author = setting_default.engine_author  # エンジン制作者名
default_setting_early_stage = setting_default.early_stage
default_setting_early_stage_think_time = setting_default.early_stage_think_time
default_setting_middle_stage1 = setting_default.middle_stage1
default_setting_middle_stage1_think_time = setting_default.middle_stage1_think_time
default_setting_middle_stage2 = setting_default.middle_stage2
default_setting_ponder_early_think_time = setting_default.ponder_early_think_time
default_setting_ponder_think_time = setting_default.ponder_think_time

# 文字列をテキストファイルに保存する関数
#   input file_path:テキストを保存したいファイルパス（.py）
#         save_str :保存したい文字列
def save_txt(file_path, save_str):
    with open(file_path, 'w') as f:
        f.write(save_str)

layout = [
    [sg.Text('エンジン名', font=(font_family, font_size))],
    [sg.InputText(engine_name, font=(font_family, font_size), key="setting_engine_name")],
    [sg.Text('エンジン制作者名', font=(font_family, font_size))],
    [sg.InputText(engine_author, font=(font_family, font_size), key="setting_engine_author")],
    [sg.Text('' , font=(font_family, 8) )],
    [sg.Text('★最序盤、序盤、中盤初期、中終盤の思考時間を設定してください。', font=(font_family, font_size))],
    [sg.Text('（ちなみに、この設定画面はどこでもつかんで移動させることができます）', font=(font_family, font_size))],
    [sg.Text('■最序盤、序盤は1つ目のエンジンでのみ思考します。', font=(font_family, font_size))],
    [sg.Text('最序盤の終わりの手数（0～50手。定跡ファイルを使いたい最大手数）', font=(font_family, font_size)), \
        sg.Spin([i for i in range(0,51)], initial_value=setting_early_stage, key="setting_early_stage", size=(4,1), font=(font_family, font_size))],
    [sg.Text('最序盤の先読みヒット（ponderhit）時の思考時間（ミリ秒）', font=(font_family, font_size)), sg.Slider(range=(100,5000), key="setting_ponder_early_think_time", \
        default_value=setting_ponder_early_think_time, resolution=100, orientation='h', font=(font_family, font_size))],
    [sg.Text('最序盤の思考時間（ミリ秒）', font=(font_family, font_size)), sg.Slider(range=(100,10000), key="setting_early_stage_think_time", \
        default_value=setting_early_stage_think_time, resolution=100, orientation='h', font=(font_family, font_size))],
    [sg.Text('■中盤初期は2つのエンジンで思考します。', font=(font_family, font_size))],
    [sg.Text('中盤初期の終わりの手数（1～512手。必ず「最序盤の終わりの手数」より大きくしてください）', font=(font_family, font_size)), \
        sg.Spin([i for i in range(1,513)], initial_value=setting_middle_stage1, key="setting_middle_stage1", size=(4,1), font=(font_family, font_size))],
    [sg.Text('最序盤より後の先読みヒット（ponderhit）時の思考時間（ミリ秒）', font=(font_family, font_size)), sg.Slider(range=(100,5000), key="setting_ponder_think_time", \
        default_value=setting_ponder_think_time, resolution=100, orientation='h', font=(font_family, font_size))],
    [sg.Text('中盤初期の思考時間', font=(font_family, font_size)), sg.Slider(range=(100,20000), key="setting_middle_stage1_think_time", \
        default_value=setting_middle_stage1_think_time, resolution=100, orientation='h', font=(font_family, font_size))],
    [sg.Text('■中終盤は1つ目のエンジンでのみ思考し、残り時間を考慮して思考します。', font=(font_family, font_size))],
    [sg.Text('中終盤の始まりの手数（1～512手。必ず「中盤初期の終わりの手数」より大きくしてください）', font=(font_family, font_size)), \
        sg.Spin([i for i in range(1,513)], initial_value=setting_middle_stage2, key="setting_middle_stage2", size=(4,1), font=(font_family, font_size))],
    [sg.Text('' , font=(font_family, 8) )],
    [sg.Button('保存する'), sg.Button('初期値に戻す'), sg.Button('保存しないで終了')]
    ]


window = sg.Window('十六式いろは煌（きらめき）の設定', layout, grab_anywhere = True)

while True:
    event, values = window.read()
    
    if event == sg.WIN_CLOSED or event == "保存しないで終了":
        logging.info("「ｘ」か「保存しないで終了」ボタンを押しました。")
        break
    
    elif event == "保存する":
        logging.info("「保存する」ボタンが押されました。")
        
        # 「中盤初期の終わりの手数」と「最序盤の終わりの手数」チェック。
        if int(values["setting_early_stage"]) >= int(values["setting_middle_stage1"]):
            sg.popup("「中盤初期の終わりの手数」は、必ず「最序盤の終わりの手数」より大きくしてください。", font=(font_family, font_size), title = "")
            logging.info("「中盤初期の終わりの手数」が、「最序盤の終わりの手数」以下でした。保存しません。")
            continue
        
        # 中終盤の始まりの手数（1～512手。必ず「中盤初期の終わりの手数」より大きくしてください「中盤初期の終わりの手数」と「最序盤の終わりの手数」チェック。より大きくしてください）
        if int(values["setting_middle_stage1"]) >= int(values["setting_middle_stage2"]):
            sg.popup("「中終盤の始まりの手数」は、必ず「中盤初期の終わりの手数」より大きくしてください。", font=(font_family, font_size), title = "")
            logging.info("「中終盤の始まりの手数」が、「中盤初期の終わりの手数」以下でした。保存しません。")
            continue
        
        write_string = f"""\
engine_name="{values["setting_engine_name"]}"
engine_author="{values["setting_engine_author"]}"
early_stage={values["setting_early_stage"]}
ponder_early_think_time={int(values["setting_ponder_early_think_time"])}
early_stage_think_time={int(values["setting_early_stage_think_time"])}
middle_stage1={int(values["setting_middle_stage1"])}
ponder_think_time={int(values["setting_ponder_think_time"])}
middle_stage1_think_time={int(values["setting_middle_stage1_think_time"])}
middle_stage2={int(values["setting_middle_stage2"])}
"""
        with open(setting_file, mode='w', encoding='utf-8') as f:
            f.write(write_string)
        logging.info("設定を次のファイルに保存しました。： {0}".format(setting_file) )
        
        sg.popup("保存しました。\nOK押して下さい。終了します。", font=(font_family, font_size), title = "")
        logging.info("設定を保存しました。")
        break
    
    elif event == "初期値に戻す":
        window["setting_engine_name"].Update(default_engine_name)
        window["setting_engine_author"].Update(default_engine_author)
        window["setting_early_stage"].Update(default_setting_early_stage)
        window["setting_early_stage_think_time"].Update(default_setting_early_stage_think_time)
        window["setting_middle_stage1"].Update(default_setting_middle_stage1)
        window["setting_middle_stage1_think_time"].Update(default_setting_middle_stage1_think_time)
        window["setting_middle_stage2"].Update(default_setting_middle_stage2)
        window["setting_ponder_early_think_time"].Update(default_setting_ponder_early_think_time)
        window["setting_ponder_think_time"].Update(default_setting_ponder_think_time)
        
        logging.info("「初期値に戻す」ボタンが押されました。")
        continue

        
# キャンセル時ウィンドウ終了処理
logging.info("設定を終了します。")
window.close()
