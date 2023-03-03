import shogi.Ayane as ayane
import re
from concurrent import futures
import time
import datetime
import setting


# 通常探索用の思考エンジンの接続テスト
# 同期的に思考させる。

# 2022-05-03 ToDo
#   [done] mate（詰め）の文字列の処理
#   [done] ponder（先読み）の処理
#   [done] 持ち時間の調整。
#   [done] 手数によりエンジンを決める処理。（他のエンジンは動かさない）
# 2022-05-10
#   [done] どのエンジンの手が選ばれたかの数を試合毎にきちんとリセットし、
#          どのエンジンの手が選ばれたかを都度出力した。
# 2022-07-18
#   [done] どっちのエンジンも選んだ手を別カウント。
# 2022-07-24
#   [done] ゲーム終了時にエンジンを停止する処理を改修。
# 2022-12-04
#   [done] エンジン[1]でのpoderを出力していなったところを改修。
# 2023-02-26
#   [done] 設定画面を実装。
# 以下、未実装。
#   クラスタ化（サーバ、クライアントシステム）


# ログファイルのパス
LOG_FILE = "16-168kirameki_denryuusen3.log"

# 設定ファイル（setting.py）の読込。
engine_name = setting.engine_name  # エンジン名
author_name = setting.engine_author  # エンジン制作者名
early_stage = setting.early_stage  # 最序盤の終わりの手数（定跡ファイルを使いたい最大手数）1つ目のエンジンでのみ思考。
early_stage_think_time = setting.early_stage_think_time  # 最序盤の思考時間（ミリ秒）
middle_stage1 = setting.middle_stage1  # 中盤初期の終わりの手数。2つのエンジンで中盤初期の思考時間で指す。
middle_stage1_think_time = setting.middle_stage1_think_time  # 中盤初期の思考時間。
middle_stage2 = setting.middle_stage2  # 中終盤の始まりの手数。1つ目のエンジンでのみ思考。
ponder_early_think_time = setting.ponder_early_think_time  # 最序盤の先読みヒット（ponderhit）時の思考時間（ミリ秒）
ponder_think_time = setting.ponder_think_time  # 最序盤より後の先読みヒット（ponderhit）時の思考時間（ミリ秒）


# エンジンに時間限定の思考をさせる関数
def multi_usi_go_and_wait(usi_lst, i, command):
    #print(i, "thinking start.")
    usi_lst[i].usi_go_and_wait_bestmove(command[3:])
    receive_lst = usi_lst[i].think_result.to_string().splitlines()
    #print(i, "thinking end.")
    # print(receive_lst)
    return receive_lst


# エンジンに時間限定せずに思考をさせる関数
def multi_usi_go(usi_lst, i):
    #print(i, "thinking start.")
    usi_lst[i].usi_go("infinite")


# エンジンに思考を終了させてbestmoveを返す関数
def multi_usi_stop_wait_bestmove(usi_lst, i):
    usi_lst[i].usi_stop()
    usi_lst[i].wait_bestmove()
    receive_lst = usi_lst[i].think_result.to_string().splitlines()
    return receive_lst


# メイン関数
def test_ayane1():
    # エンジン名
    #engine_name = "16-168-kirameki_2022"
    # エンジンの制作者名
    #author_name = "Sueyoshi, and Students of Nihon Kogakuin"

    # 楽観合議のエンジン
    # 複数の将棋ソフトのうち、評価値の最も高いソフトの指し手を採用します。
    # 評価値の最も高いソフトが同点で複数存在する場合、エンジン番号の小さなソフトが優先されます。
    #
    # 参考　tttak/GougiShogi: 合議将棋
    # https://github.com/tttak/GougiShogi

    engine_num = 2  # エンジン数。「2」個のみ対応のソースコード。

    # 各変数の設定
    # 最序盤：usi_lst[0]（定跡を使う目的）
    # 中盤　：usi_lst[1]（序中盤に強いエンジン。dlshogi系？）
    # 中終盤：usi_lst[0]（中終盤に強いエンジン。NNUE系？）
    turn_num = 0  # 手数
    #early_stage = 32  # 最序盤の終わりの手数（1-50手まで？）。ここまでやねうら王系usi_lst[0]で指す。
    #early_stage_think_time = 3000  # 序盤の思考時間、ミリ秒。
    #middle_stage1 = 50  # 中盤初期の終わりの手数（60-100手まで？）。2つのエンジンで中盤初期の思考時間で指す。
    #middle_stage1_think_time = 7000  # 中盤初期の思考時間、ミリ秒。
    #middle_stage2 = 150  # 中終盤の始まりの手数（60-100手まで？）。これ以降やねうら王系usi_lst[0]で指す。
    #ponder_early_think_time = 1200  # 最序盤の先読みヒット（ponderhit）時の自分の手番の思考時間、ミリ秒。
    #ponder_think_time = 1500  # 最序盤以外の先読みヒット（ponderhit）時の自分の手番の思考時間、ミリ秒。

    # どちらのエンジンの手がどれだけ選ばれたかを格納する。
    # [エンジン1のみ、エンジン2のみ、どちらも選んだ]
    output_engine_choice = [0, 0, 0]

    while True:
        command = input()

        # USIプロトコルエンジンのお決まりの登録に関する出力。
        if command == 'usi':
            print(f"id name {engine_name}")
            print(f"id author {author_name}")
            print("option name 設定変更は「setting.bat」を実行してできます。 type check default true")
            print('usiok')
        if command == 'isready':
            usi_lst = []  # エンジンのリスト
            for i in range(engine_num):
                # エンジンとやりとりするクラス
                usi = ayane.UsiEngine()

                # 1つ目のエンジン。やねうら王系。
                if i == 0:
                    # usi_lst[0]のエンジンに接続
                    # 通常の思考エンジンであるものとする。
                    # エンジンオプション自体は、基本的には"engine_options.txt"で設定する。(やねうら王のdocs/を読むべし)
                    usi.connect(
                        r"..\Suisho5-YO761\YaneuraOu_NNUE-tournament-clang++-avx2.exe")  # 水匠5
                    # usi.connect(r"..\YO7-uonuma\YaneuraOu7_nn-KP256.exe")  # 魚沼産やねうら王
                    # usi.connect(r"..\shinderella-0815\YO_nn-normal-avx2.exe")  # 振デレラ

                    usi_lst.append(usi)

                # 2つ目のエンジン。dlshogi系。
                else:
                    # usi_lst[1]のエンジンに接続
                    # 通常の思考エンジンであるものとする。
                    # エンジンオプション自体は、基本的には"engine_options.txt"で設定する。(やねうら王のdocs/を読むべし)
                    # dlshogi。CPUのみで動作可。
                    usi.connect(r"..\dlshogi\dlshogi_onnxruntime.exe")
                    # dlshogi、CUDA仕様。NVIDIAのGPUで動作。
                    # usi.connect(r"..\dlshogi\dlshogi_tensorrt.exe")

                    usi_lst.append(usi)
                    
            turn_num = -2  # 手数の初期値の調整
            output_engine_choice = [0, 0, 0]
            # 準備完了。
            print('readyok')

        # 局面の受け取り。
        if command[:8] == 'position':
            # 切り替え時に指し手が変になるのを防ぐため、とりあえずどちらのエンジンにも。
            usi_lst[0].usi_position(command[9:])
            usi_lst[1].usi_position(command[9:])
            turn_num = command.count(" ") - 1  # potisionの文字列のワード数から手数を算出。
            #print("turn_num :",turn_num)
            # 十六式いろは煌が先手か後手か
            if turn_num % 2 != 0:
                my_turn = "b"  # 黒black、先手
            else:
                my_turn = "w"  # 白white、後手
            #print("my_turn :", my_turn)

        # 思考開始の合図の受け取り。
        if command[:2] == 'go' and command[:9] != 'go ponder':
            # 送られてくる持ち時間を優先する
            if my_turn == "b":  # 黒black、先手
                # GUIから送られてくる自分の持ち時間
                time_limit_org = int(re.findall(
                    r"btime\s([0-9]*)", command)[0])
            else:
                time_limit_org = int(re.findall(
                    r"wtime\s([0-9]*)", command)[0])
            try:
                if time_limit_org != 0:
                    # 実際の自分の持ち時間
                    time_limit = time_limit_org
                else:
                    time_limit = int(re.findall(
                        r"byoyomi\s([0-9]*)", command)[0])
            except:  # 想定外。とりあえず。
                time_limit = 1000
            #print("time_limit(not ponder) :", time_limit)

            # 最序盤と中終盤はusi_lst[0]やねうら王系のみ。
            # 最序盤は定跡が目的。
            if turn_num < early_stage or turn_num > middle_stage2:
                # 最序盤は持ち時間を少なく書き換える。
                if turn_num < early_stage:
                    command = re.sub(
                        r"btime.*", f"btime 0 wtime 0 byoyomi {early_stage_think_time}", command)
                usi_lst[0].usi_go_and_wait_bestmove(command[3:])
                # 思考内容を表示させてみる。
                output = usi_lst[0].think_result.to_string().splitlines()

                for string in output:
                    if string.find("bestmove") < 0:
                        print("info " + string)
                    elif string == "bestmove":
                        bestmove_cmd = string
                    elif string == "":
                        pass
                    else:
                        # Ayaneからだとscoreがなく評価値が表示されないため。
                        string = string.replace("cp", "score cp")
                        string = string.replace("mate", "score mate")
                        print("info " + string[:string.find("bestmove")])
                        bestmove_cmd = string[string.find("bestmove"):]

                print(
                    f"info string engine {usi_lst[0].engine_path} turn_num " + str(turn_num))
                print(bestmove_cmd)
                output = ""

            # 最序盤以降。
            # 持ち時間が、最序盤の思考時間よりも多いときは置き換える。
            elif time_limit > early_stage_think_time:
                # 最序盤まで。
                if turn_num < early_stage:
                    # 持ち時間を最序盤の思考時間に置き換える。
                    command = re.sub(
                        r"btime.*", f"btime 0 wtime 0 byoyomi {early_stage_think_time}", command)
                # 序中盤まで。
                elif turn_num < middle_stage1:
                    # 持ち時間を序中盤の思考時間に置き換える。
                    command = re.sub(
                        r"btime.*", f"btime 0 wtime 0 byoyomi {middle_stage1_think_time}", command)
                # 中終盤から。
                else:
                    pass

                # 各エンジンが決めた次の一手のbestmoveからの文字列
                output_bestmove_str = []
                # 各エンジンが決めた次の一手の評価値のリスト（cpやmateを含む）
                output_score_list = []
                # 各エンジンが決めた次の一手
                output_bestmove = []
                # 各エンジンが決めた次の一手からの予想手
                output_ponder = []

                # 思考内容を格納するリスト。
                output = []
                # 1つ目のエンジンusi_lst[0]に読ませる。
                # start_time = time.time()  # 処理時間の計測開始。

                # ここから並列処理（not並行処理）
                # 参考：**Python - concurrent.futures を使った並列化の方法について - pystyle**
                # https://pystyle.info/python-concurrent-futures/#outline__6

                # 1つ目のエンジンからの返事をoutput(list)に読ませる。
                #output.append(multi_usi_go_and_wait(usi_lst, 0, command))
                # 2つ目のエンジンからの返事をoutput(list)に読ませる。
                #output.append(multi_usi_go_and_wait(usi_lst, 1, command))

                # エンジンからの返事を格納するリスト。
                future_list = []
                # 2つのエンジンを動かす。
                with futures.ThreadPoolExecutor() as executor:
                #with futures.ProcessPoolExecutor() as executor:
                    for i in range(2):
                        # タスクを追加する。引数は、関数の後に続けて書く。
                        future = executor.submit(
                            multi_usi_go_and_wait, usi_lst, i, command)
                        # Future オブジェクトを記録する。
                        future_list.append(future)

                # すべてのエンジンの返事が帰ってきてから
                # エンジンから帰ってきた返事を読ませる。
                # print(future_list[0].result())
                # print(future_list[1].result())
                output.append(future_list[0].result())
                output.append(future_list[1].result())
                # print("time: ", str(time.time()- start_time))  # 処理時間の計測終了
                # ここまで並列処理（not並行処理）

                # ここから関数化したい。
                #output_string = []

                for i in range(2):
                    #print("info string engine: ", i)
                    for string in output[i]:
                        #print(i, "output[i] :", output[i])
                        #print("string :", string)
                        if string.find("bestmove") < 0:
                            print("info string [res] " + string, flush=True)
                        else:
                            # Ayaneからだとscoreがなく評価値が表示されないため。
                            string = string.replace("cp", "score cp")
                            string = string.replace("mate", "score mate")

                            if string != "":
                                # 各エンジンから出力された文字列に
                                # 「bestmove」があれば、その前の文字列を抜き取る。
                                info_string = string[:string.find("bestmove")]
                                # 抜き出した文字列から「pv」があれば、pv以降の文字列を抜き取る。
                                # 例）pv G*5h 6i7i 5h5g B*5b G*4b P*3b 3a2b 7a4a+ 4b4a 5b4a+ B*6h 7i8h S*7i 8h9h R*8h
                                info_string2 =  info_string[info_string.find("pv"):]
                                # info_string2_listのインデックス0は「pv」、
                                # インデックス1は自分の予測手、
                                # インデックス2は相手の次の予測手。
                                # 例）info_string2_list[0]="pv"、info_string2_list[1]="G*5h"
                                info_string2_list = list(info_string2.split())
                                print("info " + info_string, flush=True)
                                #print("a info2 " + info_string2, flush=True)
                            
                            # 評価値を取得する。
                            tmp_str1 = re.search(r"score\s\S*\s\S*", string)
                            #print("string :", string)
                            
                            if tmp_str1 == None:  # scoreが見つからないときは定跡にヒット？
                                tmp_str2 = ["score", "cp", 0]  # とりあえず代入
                            else:
                                # スペース区切りのリスト
                                tmp_str2 = list(tmp_str1.group().split())
                            # tmp_str2の例） ['score', 'cp', '-275']
                            #print("tmp_str2 :", tmp_str2)

                            # エンジンusi_lst[i]の次の一手の文字列output_score_list[i]
                            # 例） "cp" 256
                            # 例） "mate" -8
                            output_score_list.append(
                                [tmp_str2[1], int(tmp_str2[2])])
                            # 1つ目のエンジンusi_lst[0]の次の一手
                            # tmp_str_best1の例） "bestmove P*7f ponder 7g7f"
                            #tmp_str_best1 = string[string.find("bestmove"):]
                            try:
                                tmp_str_best1 = f"bestmove {info_string2_list[1]} ponder {info_string2_list[2]}"
                            except:
                                try:
                                    tmp_str_best1 = f"bestmove {info_string2_list[1]}"
                                except:
                                    tmp_str_best1 = f"bestmove resign"
                            #print("string :", string)
                            #print("tmp_str_best1 :", tmp_str_best1)

                            # output_bestmove_strの例） "bestmove P*7f ponder 7g7f"
                            output_bestmove_str.append(tmp_str_best1)

                            tmp_str_best2 = list(
                                tmp_str_best1.split())  # 空白文字区切りのリスト。
                            # output_bestmove[i]の例） "P*7f"
                            #print("tmp_str_best2 :", tmp_str_best2)

                            output_bestmove.append(tmp_str_best2[1])
                            try:
                                # output_bestmove[i]の例） "7g7f"
                                output_ponder.append(tmp_str_best2[3])
                            except:
                                # output_bestmove[i]の例） "none"
                                output_ponder.append("none")

                    # エンジンusi_lst[i]の次の一手
                    print(
                        f"info string engine {usi_lst[i].engine_path} turn_num " + str(turn_num), flush=True)
                    #print(f"info string engine {usi_lst[i].engine_path} cp " + str(output_score_list[i]))
                    #print(f"info string engine {usi_lst[i].engine_path} bestmove " + output_bestmove[i])
                    #print(f"info string engine {usi_lst[i].engine_path} ponder " + output_ponder[i])

                # エンジン[0]がmateを出していないとき
                if output_score_list[0][0] == "cp":
                    # どちらのエンジンもmateが出ていないとき
                    if output_score_list[1][0] == "cp":
                        # エンジン[1]の数字が大きい時
                        if output_score_list[0][1] < output_score_list[1][1]:
                            output_engine_choice[1] += 1
                            is_both_choice = False  # bool。どちらも同じ手を選んだかどうか。
                            # 次の一手が同じ指し手なら、どちらもchoiceカウントに追加
                            if output_bestmove[0] == output_bestmove[1]:
                                is_both_choice = True
                                output_engine_choice[1] -= 1
                                output_engine_choice[2] += 1
                                print("info string choice both", flush=True)
                            # 評価値が低い方のエンジンの指し手を先に出力する
                            print(
                                f"info score cp {str(output_score_list[0][1])} pv {output_bestmove[0]} {output_ponder[0]}", flush=True)
                            print(
                                f"info score cp {str(output_score_list[1][1])} pv {output_bestmove[1]} {output_ponder[1]}", flush=True)
                                
                            output_choice = f"info string choice engine0 {str(output_engine_choice[0])} engine1 {str(output_engine_choice[1])} both {str(output_engine_choice[2])}"
                            print(output_choice)
                            with open(LOG_FILE, mode="a") as f:
                                f.write(str(datetime.datetime.now())+" turn "+str(turn_num)+" "+output_choice+"\n")
                            
                            if is_both_choice == False:
                                print("info string choice dlshogi", flush=True)
                            print(output_bestmove_str[1], flush=True)

                        # エンジン[0]の数字が大きい時
                        else:
                            output_engine_choice[0] += 1
                            is_both_choice = False  # bool。どちらも同じ手を選んだかどうか。
                            # 次の一手が同じ指し手なら、どちらもchoiceカウントに追加
                            if output_bestmove[0] == output_bestmove[1]:
                                is_both_choice = True
                                output_engine_choice[0] -= 1
                                output_engine_choice[2] += 1
                                print("info string choice both", flush=True)
                            # 評価値が低い方のエンジンの指し手を先に出力する
                            print(
                                f"info score cp {str(output_score_list[1][1])} pv {output_bestmove[1]}", flush=True)
                            print(
                                f"info score cp {str(output_score_list[0][1])} pv {output_bestmove[0]}", flush=True)
                                
                            output_choice = f"info string choice engine0 {str(output_engine_choice[0])} engine1 {str(output_engine_choice[1])} both {str(output_engine_choice[2])}"
                            print(output_choice)
                            with open(LOG_FILE, mode="a") as f:
                                f.write(str(datetime.datetime.now())+" turn "+str(turn_num)+" "+output_choice+"\n")
                            
                            if is_both_choice == False:
                                print("info string choice YaneuraOu", flush=True)
                            print(output_bestmove_str[0], flush=True)

                    # エンジン[1]だけmateが出ているとき
                    elif output_score_list[1][0] == "mate":
                        is_both_choice = False  # bool。どちらも同じ手を選んだかどうか。
                        output_engine_choice[1] += 1
                        # 次の一手が同じ指し手なら、どちらもchoiceカウントに追加
                        if output_bestmove[0] == output_bestmove[1]:
                            output_engine_choice[1] -= 1
                            output_engine_choice[2] += 1
                            is_both_choice = True
                            print("info string choice both", flush=True)
                        # 評価値が低い方のエンジンの指し手を先に出力する
                        print(
                            f"info score cp {str(output_score_list[0][1])} pv {output_bestmove[0]}", flush=True)
                        print(
                            f"info score mate {str(output_score_list[1][1])} pv {output_bestmove[1]}", flush=True)
                            
                        output_choice = f"info string choice engine0 {str(output_engine_choice[0])} engine1 {str(output_engine_choice[1])} both {str(output_engine_choice[2])}"
                        print(output_choice)
                        with open(LOG_FILE, mode="a") as f:
                            f.write(str(datetime.datetime.now())+" turn "+str(turn_num)+" "+output_choice+"\n")
                        
                        if is_both_choice == False:
                            print("info string choice dlshogi", flush=True)
                        print(output_bestmove_str[1], flush=True)

                    # エンジン[1]がcpもmateも出していないとき（想定外）
                    # とりあえず、エンジン[0]の結果を出力する
                    else:
                        output_engine_choice[0] += 1
                        # 評価値が低い方のエンジンの指し手を先に出力する
                        print("info string engin1 cp Unexpected")
                        print(
                            f"info score {str(output_score_list[0][0])} {str(output_score_list[0][1])} pv {output_bestmove[1]}")
                            
                        output_choice = f"info string choice engine0 {str(output_engine_choice[0])} engine1 {str(output_engine_choice[1])} both {str(output_engine_choice[2])}"
                        print(output_choice)
                        with open(LOG_FILE, mode="a") as f:
                            f.write(str(datetime.datetime.now())+" turn "+str(turn_num)+" "+output_choice+"\n")
                        
                        print("info string choice YaneuraOu", flush=True)
                        print(output_bestmove_str[0], flush=True)

                # エンジン[0]がmateを出しているとき
                elif output_score_list[0][0] == "mate":
                    # エンジン[1]はmateが出ていないとき
                    if output_score_list[1][0] == "cp":
                        is_both_choice = False  # bool。どちらも同じ手を選んだかどうか。
                        output_engine_choice[0] += 1
                        # 次の一手が同じ指し手なら、どちらもchoiceカウントに追加
                        if output_bestmove[0] == output_bestmove[1]:
                            output_engine_choice[0] -= 1
                            output_engine_choice[2] += 1
                            is_both_choice = True
                            print("info string choice both", flush=True)
                        # 評価値が低い方のエンジンの指し手を先に出力する
                        print(
                            f"info score cp {str(output_score_list[1][1])} pv {output_bestmove[1]}", flush=True)
                        print(
                            f"info score mate {str(output_score_list[0][1])} pv {output_bestmove[0]}", flush=True)
                            
                        output_choice = f"info string choice engine0 {str(output_engine_choice[0])} engine1 {str(output_engine_choice[1])} both {str(output_engine_choice[2])}"
                        print(output_choice)
                        with open(LOG_FILE, mode="a") as f:
                            f.write(str(datetime.datetime.now())+" turn "+str(turn_num)+" "+output_choice+"\n")
                        
                        if is_both_choice == False:
                            print("info string choice YaneuraOu", flush=True)
                        print(output_bestmove_str[0], flush=True)

                    # エンジン[1]もmate出しているとき
                    elif output_score_list[1][0] == "mate":
                        # エンジン[0]の方が早く詰める時、同じ速さで詰める時。
                        if output_score_list[0][1] <= output_score_list[1][1]:
                            output_engine_choice[0] += 1
                            # 次の一手が同じ指し手なら、どちらもchoiceカウントに追加
                            if output_bestmove[0] == output_bestmove[1]:
                                output_engine_choice[0] -= 1
                                output_engine_choice[2] += 1
                                is_both_choice = True
                                print("info string choice both", flush=True)
                            # 評価値が低い方のエンジンの指し手を先に出力する
                            print(
                                f"info score mate {str(output_score_list[1][1])} pv {output_bestmove[1]}", flush=True)
                            print(
                                f"info score mate {str(output_score_list[0][1])} pv {output_bestmove[0]}", flush=True)
                                
                            output_choice = f"info string choice engine0 {str(output_engine_choice[0])} engine1 {str(output_engine_choice[1])} both {str(output_engine_choice[2])}"
                            print(output_choice)
                            with open(LOG_FILE, mode="a") as f:
                                f.write(str(datetime.datetime.now())+" turn "+str(turn_num)+" "+output_choice+"\n")
                            
                            if is_both_choice == False:
                                print("info string choice YaneuraOu", flush=True)
                            print(output_bestmove_str[0], flush=True)

                        # エンジン[1]の方が早く詰める時、同じ速さで詰める時。
                        else:
                            output_engine_choice[1] += 1
                            # 次の一手が同じ指し手なら、どちらもchoiceカウントに追加
                            if output_bestmove[0] == output_bestmove[1]:
                                output_engine_choice[1] -= 1
                                output_engine_choice[2] += 1
                                is_both_choice = True
                                print("info string choice both", flush=True)
                            # 評価値が低い方のエンジンの指し手を先に出力する
                            print(
                                f"info score mate {str(output_score_list[0][1])} pv {output_bestmove[0]}", flush=True)
                            print(
                                f"info score mate {str(output_score_list[1][1])} pv {output_bestmove[1]}", flush=True)
                                
                            output_choice = f"info string choice engine0 {str(output_engine_choice[0])} engine1 {str(output_engine_choice[1])} both {str(output_engine_choice[2])}"
                            print(output_choice)
                            with open(LOG_FILE, mode="a") as f:
                                f.write(str(datetime.datetime.now())+" turn "+str(turn_num)+" "+output_choice+"\n")
                            
                            if is_both_choice == False:
                                print("info string choice dlshogi", flush=True)
                            print(output_bestmove_str[1], flush=True)

                # エンジン[0]がcpもmateも出していないとき（想定外）
                # とりあえず、エンジン[1]の結果を出力する
                else:
                    output_engine_choice[1] += 1
                    # 評価値が低い方のエンジンの指し手を出力する
                    print("info string engin0 cp Unexpected")
                    print(
                        f"info score {str(output_score_list[1][0])} {str(output_score_list[1][1])} pv {output_bestmove[1]}")
                        
                    output_choice = f"info string choice engine0 {str(output_engine_choice[0])} engine1 {str(output_engine_choice[1])} both {str(output_engine_choice[2])}"
                    print(output_choice)
                    with open(LOG_FILE, mode="a") as f:
                        f.write(str(datetime.datetime.now())+" turn "+str(turn_num)+" "+output_choice+"\n")
                    
                    print("info string choice dlshogi", flush=True)
                    print(output_bestmove_str[1], flush=True)
                # ここまで関数化したい。

        # 先読み（ponder）の思考開始の合図の受け取り。
        elif command[:9] == 'go ponder':
            # 各エンジンが決めた次の一手のbestmoveからの文字列
            output_bestmove_str = []
            # 各エンジンが決めた次の一手の評価値のリスト（cpやmateを含む）
            output_score_list = []
            # 各エンジンが決めた次の一手
            output_bestmove = []
            # 各エンジンが決めた次の一手からの予想手
            output_ponder = []

            # 送られてくる持ち時間を優先する
            if my_turn == "b":  # 黒black、先手
                # GUIから送られてくる指したあとに増える自分の持ち時間
                time_limit_org = int(re.findall(
                    r"btime\s([0-9]*)", command)[0])
            else:
                time_limit_org = int(re.findall(
                    r"wtime\s([0-9]*)", command)[0])
            try:
                if time_limit_org != 0:
                    # 実際の自分の持ち時間
                    time_limit = time_limit_org
                else:
                    time_limit = int(re.findall(
                        r"byoyomi\s([0-9]*)", command)[0])
            except:  # 想定外。とりあえず。
                time_limit = 1000
            #print("time_limit :", time_limit)

            # 最序盤と中終盤のみ。
            if turn_num < early_stage or turn_num > middle_stage2:
                # usi_lst[0]やねうら王系エンジンのみ思考させる。
                usi_lst[0].usi_go("infinite")

            # 最序盤以外。
            else:
                # エンジンからの返事を格納するリスト。
                future_list = []
                #print("[>cmd] go infinite")
                # 2つのエンジンを動かす。
                with futures.ThreadPoolExecutor() as executor:
                    for i in range(2):
                        # タスクを追加する。引数は、関数の後に続けて書く。
                        # 時間制限なしで思考を開始させる。
                        future = executor.submit(multi_usi_go, usi_lst, i)
                        # Future オブジェクトを記録する。
                        future_list.append(future)

        # ponder(先読み)機能は、"stop"か"ponderhit"がGUIから送られる。
        # 先読みがハズレた場合。
        elif command[:4] == "stop":
            # 最序盤のみ。
            #print("[cmd>] stop")
            #print(f"turn_num {turn_num} early_stage {early_stage}")

            # 最序盤と中終盤のみ。
            if turn_num < early_stage or turn_num > middle_stage2:
                # やねうら王系エンジンの思考を止める。
                usi_lst[0].usi_stop()
                usi_lst[0].wait_bestmove()
                # 合法手なら何でも良いので返す。
                # とりあえず意味はないが「resign」を返す。
                #print("info string early Toriaezu.")
                print("bestmove resign")

            # 最序盤以外。
            else:
                future_list = []
                # 2つのエンジンの思考をすぐに止める。
                with futures.ThreadPoolExecutor() as executor:
                    for i in range(2):
                        # タスクを追加する。引数は、関数の後に続けて書く。
                        # 思考を停止させる。
                        future = executor.submit(
                            multi_usi_stop_wait_bestmove, usi_lst, i)
                        # Future オブジェクトを記録する。
                        future_list.append(future)
                # すべてのエンジンの返事が返ってきてから
                # 合法手なら何でも良いので返す。
                # とりあえず意味はないが「resign」を返す。
                #print("info string Toriaezu.")
                print("bestmove resign")

        # 先読みが当たった場合。
        elif command[:9] == "ponderhit":
            # 最序盤と中終盤のみ。
            if turn_num < early_stage or turn_num > middle_stage2:
                # 最序盤は持ち時間を少なく書き換える。
                if turn_num < early_stage:
                    # 最序盤用のponderhitの思考時間だけ待つ。
                    time_limit_sec = int(ponder_early_think_time/1000)
                # 最序盤以外はponderhitのponder_think_timeだけ待つ。
                else:
                    time_limit_sec = int(ponder_think_time/1000)
                print(
                    f"info string thinking {time_limit_sec} sec.", flush=True)
                time.sleep(time_limit_sec)

                # エンジンを停止させて、bestmoveを待つ。
                usi_lst[0].usi_stop()
                usi_lst[0].wait_bestmove()
                # 思考内容を表示させてみる。
                output = usi_lst[0].think_result.to_string().splitlines()

                for string in output:
                    if string.find("bestmove") < 0:
                        print("info " + string)
                    elif string == "bestmove":
                        bestmove_cmd = string
                    elif string == "":
                        pass
                    else:
                        # Ayaneからだとscoreがなく評価値が表示されないため。
                        string = string.replace("cp", "score cp")
                        string = string.replace("mate", "score mate")
                        print("info " + string[:string.find("bestmove")])
                        bestmove_cmd = string[string.find("bestmove"):]

                print(
                    f"info string engine {usi_lst[0].engine_path} turn_num " + str(turn_num))
                print(bestmove_cmd)
                output = ""

            # 最序盤以外。
            else:
                # 実際の自分の持ち時間だけ考えせる。
                #print(f"info string time_limit {time_limit} ponder_think_time {ponder_think_time}", flush=True)
                # 最序盤。
                if turn_num < early_stage:
                    time_limit_sec = int(ponder_early_think_time/1000)
                # 最序盤以外。
                elif time_limit > ponder_think_time:
                    time_limit_sec = int(ponder_think_time/1000)
                # 持ち時間がないとき。1秒だけ使う。
                else:
                    time_limit_sec = 1
                # start_time = time.time()  # 処理時間の計測開始。
                print(
                    f"info string thinking {time_limit_sec} sec.", flush=True)
                time.sleep(time_limit_sec)

                future_list = []
                with futures.ThreadPoolExecutor() as executor:
                    for i in range(2):
                        # タスクを追加する。引数は、関数の後に続けて書く。
                        # 思考を停止させる。
                        future = executor.submit(
                            multi_usi_stop_wait_bestmove, usi_lst, i)
                        # Future オブジェクトを記録する。
                        future_list.append(future)
                # すべてのエンジンの返事が返ってきてから
                # エンジンから返ってきた返事を読ませる。
                output = []
                output.append(future_list[0].result())
                output.append(future_list[1].result())

                # ここから関数化したい。
                #output_string = []

                for i in range(2):
                    #print("info string engine: ", i)
                    for string in output[i]:
                        #print(i, "output[i] :", output[i])
                        #print("string :", string)
                        if string.find("bestmove") < 0:
                            print("info string [res] " + string, flush=True)
                        else:
                            # Ayaneからだとscoreがなく評価値が表示されないため。
                            string = string.replace("cp", "score cp")
                            string = string.replace("mate", "score mate")

                            if string != "":
                                # 各エンジンから出力された文字列に
                                # 「bestmove」があれば、その前の文字列を抜き取る。
                                info_string = string[:string.find("bestmove")]
                                # 抜き出した文字列から「pv」があれば、pv以降の文字列を抜き取る。
                                # 例）pv G*5h 6i7i 5h5g B*5b G*4b P*3b 3a2b 7a4a+ 4b4a 5b4a+ B*6h 7i8h S*7i 8h9h R*8h
                                info_string2 =  info_string[info_string.find("pv"):]
                                # info_string2_listのインデックス0は「pv」、
                                # インデックス1は自分の予測手、
                                # インデックス2は相手の次の予測手。
                                # 例）info_string2_list[0]="pv"、info_string2_list[1]="G*5h"
                                info_string2_list = list(info_string2.split())
                                print("info " + info_string, flush=True)
                                #print("info " + string[:string.find("bestmove")], flush=True)
                            
                            # 評価値を取得する。
                            tmp_str1 = re.search(r"score\s\S*\s\S*", string)
                            #print("string :", string)

                            if tmp_str1 == None:  # scoreが見つからないときは定跡にヒット？
                                tmp_str2 = ["score", "cp", 0]  # とりあえず代入
                            else:
                                # スペース区切りのリスト
                                tmp_str2 = list(tmp_str1.group().split())
                            # tmp_str2の例） ['score', 'cp', '-275']
                            #print("tmp_str2 :", tmp_str2)

                            # エンジンusi_lst[i]の次の一手の文字列output_score_list[i]
                            # 例） "cp" 256
                            # 例） "mate" -8
                            output_score_list.append(
                                [tmp_str2[1], int(tmp_str2[2])])
                            # 1つ目のエンジンusi_lst[0]の次の一手
                            # tmp_str_best1の例） "bestmove P*7f ponder 7g7f"
                            #tmp_str_best1 = string[string.find("bestmove"):]
                            try:
                                tmp_str_best1 = f"bestmove {info_string2_list[1]} ponder {info_string2_list[2]}"
                            except:
                                try:
                                    tmp_str_best1 = f"bestmove {info_string2_list[1]}"
                                except:
                                    tmp_str_best1 = f"bestmove resign"
                            #print("string :", string)
                            #print("tmp_str_best1 :", tmp_str_best1)
                            
                            # output_bestmove_strの例） "bestmove P*7f ponder 7g7f"
                            output_bestmove_str.append(tmp_str_best1)
                            
                            tmp_str_best2 = list(
                                tmp_str_best1.split())  # 空白文字区切りのリスト。
                            # output_bestmove[i]の例） "P*7f"
                            #print("tmp_str_best2 :", tmp_str_best2)
                            
                            output_bestmove.append(tmp_str_best2[1])
                            try:
                                # output_bestmove[i]の例） "7g7f"
                                output_ponder.append(tmp_str_best2[3])
                            except:
                                # output_bestmove[i]の例） "none"
                                output_ponder.append("none")

                    # エンジンusi_lst[i]の次の一手
                    print(
                        f"info string engine {usi_lst[i].engine_path} turn_num " + str(turn_num), flush=True)
                    #print(f"info string engine {usi_lst[i].engine_path} cp " + str(output_score_list[i]))
                    #print(f"info string engine {usi_lst[i].engine_path} bestmove " + output_bestmove[i])
                    #print(f"info string engine {usi_lst[i].engine_path} ponder " + output_ponder[i])

                # エンジン[0]がmateを出していないとき
                if output_score_list[0][0] == "cp":
                    # どちらのエンジンもmateが出ていないとき
                    if output_score_list[1][0] == "cp":
                        # エンジン[1]の数字が大きい時
                        if output_score_list[0][1] < output_score_list[1][1]:
                            output_engine_choice[1] += 1
                            # 次の一手が同じ指し手なら、どちらもchoiceカウントに追加
                            if output_bestmove[0] == output_bestmove[1]:
                                output_engine_choice[0] += 1
                            # 評価値が低い方のエンジンの指し手を先に出力する
                            print(
                                f"info score cp {str(output_score_list[0][1])} pv {output_bestmove[0]} {output_ponder[0]}", flush=True)
                            print(
                                f"info score cp {str(output_score_list[1][1])} pv {output_bestmove[1]} {output_ponder[1]}", flush=True)
                                
                            output_choice = f"info string choice engine0 {str(output_engine_choice[0])} engine1 {str(output_engine_choice[1])} both {str(output_engine_choice[2])}"
                            print(output_choice)
                            with open(LOG_FILE, mode="a") as f:
                                f.write(str(datetime.datetime.now())+" turn "+str(turn_num)+" "+output_choice+"\n")
                            
                            print("info string choice dlshogi", flush=True)
                            #print("bestmove", output_bestmove[1])
                            print(output_bestmove_str[1], flush=True)

                        # エンジン[0]の数字が大きい時
                        else:
                            output_engine_choice[0] += 1
                            # 次の一手が同じ指し手なら、どちらもchoiceカウントに追加
                            if output_bestmove[0] == output_bestmove[1]:
                                output_engine_choice[1] += 1
                            # 評価値が低い方のエンジンの指し手を先に出力する
                            print(
                                f"info score cp {str(output_score_list[1][1])} pv {output_bestmove[1]}", flush=True)
                            print(
                                f"info score cp {str(output_score_list[0][1])} pv {output_bestmove[0]}", flush=True)
                                
                            output_choice = f"info string choice engine0 {str(output_engine_choice[0])} engine1 {str(output_engine_choice[1])} both {str(output_engine_choice[2])}"
                            print(output_choice)
                            with open(LOG_FILE, mode="a") as f:
                                f.write(str(datetime.datetime.now())+" turn "+str(turn_num)+" "+output_choice+"\n")
                            
                            print("info string choice YaneuraOu", flush=True)
                            print(output_bestmove_str[0], flush=True)

                    # エンジン[1]だけmateが出ているとき
                    elif output_score_list[1][0] == "mate":
                        output_engine_choice[1] += 1
                        # 次の一手が同じ指し手なら、どちらもchoiceカウントに追加
                        if output_bestmove[0] == output_bestmove[1]:
                            output_engine_choice[0] += 1
                        # 評価値が低い方のエンジンの指し手を先に出力する
                        print(
                            f"info score cp {str(output_score_list[0][1])} pv {output_bestmove[0]}", flush=True)
                        print(
                            f"info score mate {str(output_score_list[1][1])} pv {output_bestmove[1]}", flush=True)
                            
                        output_choice = f"info string choice engine0 {str(output_engine_choice[0])} engine1 {str(output_engine_choice[1])} both {str(output_engine_choice[2])}"
                        print(output_choice)
                        with open(LOG_FILE, mode="a") as f:
                            f.write(str(datetime.datetime.now())+" turn "+str(turn_num)+" "+output_choice+"\n")
                        
                        print("info string choice dlshogi", flush=True)
                        print(output_bestmove_str[1])

                    # エンジン[1]がcpもmateも出していないとき（想定外）
                    # とりあえず、エンジン[0]の結果を出力する
                    else:
                        output_engine_choice[0] += 1
                        # 評価値が低い方のエンジンの指し手を先に出力する
                        print("info string engin1 cp Unexpected")
                        print(
                            f"info score {str(output_score_list[0][0])} {str(output_score_list[0][1])} pv {output_bestmove[1]}")
                            
                        output_choice = f"info string choice engine0 {str(output_engine_choice[0])} engine1 {str(output_engine_choice[1])} both {str(output_engine_choice[2])}"
                        print(output_choice)
                        with open(LOG_FILE, mode="a") as f:
                            f.write(str(datetime.datetime.now())+" turn "+str(turn_num)+" "+output_choice+"\n")
                        
                        print("info string choice YaneuraOu", flush=True)
                        print(output_bestmove_str[0], flush=True)

                # エンジン[0]がmateを出しているとき
                elif output_score_list[0][0] == "mate":
                    # エンジン[1]はmateが出ていないとき
                    if output_score_list[1][0] == "cp":
                        output_engine_choice[0] += 1
                        # 次の一手が同じ指し手なら、どちらもchoiceカウントに追加
                        if output_bestmove[0] == output_bestmove[1]:
                            output_engine_choice[1] += 1
                        # 評価値が低い方のエンジンの指し手を先に出力する
                        print(
                            f"info score cp {str(output_score_list[1][1])} pv {output_bestmove[1]}")
                        print(
                            f"info score mate {str(output_score_list[0][1])} pv {output_bestmove[0]}")
                            
                        output_choice = f"info string choice engine0 {str(output_engine_choice[0])} engine1 {str(output_engine_choice[1])} both {str(output_engine_choice[2])}"
                        print(output_choice)
                        with open(LOG_FILE, mode="a") as f:
                            f.write(str(datetime.datetime.now())+" turn "+str(turn_num)+" "+output_choice+"\n")
                        
                        print("info string choice YaneuraOu", flush=True)
                        print(output_bestmove_str[0])

                    # エンジン[1]もmate出しているとき
                    elif output_score_list[1][0] == "mate":
                        # エンジン[0]の方が早く詰める時、同じ速さで詰める時。
                        if output_score_list[0][1] <= output_score_list[1][1]:
                            output_engine_choice[0] += 1
                            # 次の一手が同じ指し手なら、どちらもchoiceカウントに追加
                            if output_bestmove[0] == output_bestmove[1]:
                                output_engine_choice[1] += 1
                            # 評価値が低い方のエンジンの指し手を先に出力する
                            print(
                                f"info score mate {str(output_score_list[1][1])} pv {output_bestmove[1]}")
                            print(
                                f"info score mate {str(output_score_list[0][1])} pv {output_bestmove[0]}")
                                
                            output_choice = f"info string choice engine0 {str(output_engine_choice[0])} engine1 {str(output_engine_choice[1])} both {str(output_engine_choice[2])}"
                            print(output_choice)
                            with open(LOG_FILE, mode="a") as f:
                                f.write(str(datetime.datetime.now())+" turn "+str(turn_num)+" "+output_choice+"\n")
                            
                            print("info string choice YaneuraOu", flush=True)
                            #print("bestmove", output_bestmove[1])
                            print(output_bestmove_str[0])

                        # エンジン[1]の方が早く詰める時、同じ速さで詰める時。
                        else:
                            output_engine_choice[1] += 1
                            # 次の一手が同じ指し手なら、どちらもchoiceカウントに追加
                            if output_bestmove[0] == output_bestmove[1]:
                                output_engine_choice[0] += 1
                            # 評価値が低い方のエンジンの指し手を先に出力する
                            print(
                                f"info score mate {str(output_score_list[0][1])} pv {output_bestmove[0]}")
                            print(
                                f"info score mate {str(output_score_list[1][1])} pv {output_bestmove[1]}")
                                
                            output_choice = f"info string choice engine0 {str(output_engine_choice[0])} engine1 {str(output_engine_choice[1])} both {str(output_engine_choice[2])}"
                            print(output_choice)
                            with open(LOG_FILE, mode="a") as f:
                                f.write(str(datetime.datetime.now())+" turn "+str(turn_num)+" "+output_choice+"\n")
                            
                            print("info string choice dlshogi", flush=True)
                            print(output_bestmove_str[1])

                # エンジン[0]がcpもmateも出していないとき（想定外）
                # とりあえず、エンジン[1]の結果を出力する
                else:
                    output_engine_choice[1] += 1
                    # 評価値が低い方のエンジンの指し手を出力する
                    print("info string engin0 cp Unexpected")
                    print(
                        f"info score {str(output_score_list[1][0])} {str(output_score_list[1][1])} pv {output_bestmove[1]}")
                        
                    output_choice = f"info string choice engine0 {str(output_engine_choice[0])} engine1 {str(output_engine_choice[1])} both {str(output_engine_choice[2])}"
                    print(output_choice)
                    with open(LOG_FILE, mode="a") as f:
                        f.write(str(datetime.datetime.now())+" turn "+str(turn_num)+" "+output_choice+"\n")
                    
                    print("info string choice dlshogi", flush=True)
                    print(output_bestmove_str[1])
                # ここまで関数化したい。
        
        # ゲームが終了した時、将棋エンジンを切る。
        elif command[:8] == "gameover":
            # エンジンを切断
            usi_lst[0].disconnect()
            usi_lst[1].disconnect()
        # 上記以外のコマンドを受け取った場合、コマンドをそのまま返し無視する。
        else:
            #print("[cmd] " + command)
            pass

        if command == 'quit':
            break

        #print("[cmd] " + command + " / turn_num " + str(turn_num))

    # （コマンド「isready」を実行して）エンジンを起動させている場合は、
    # エンジンを切断
    if "usi_lst" in locals():
        usi_lst[0].disconnect()
        usi_lst[1].disconnect()

    exit()


if __name__ == "__main__":
    test_ayane1()
