import subprocess
import os
import glob

# デフォルトの動画長（秒）
DEFAULT_DURATION = 30             

def create_youtube_short(input_file, output_file, start_time):
    """
    指定された動画から YouTube Shorts 用の動画を生成する関数
    
    Parameters:
        input_file (str): 入力動画ファイルのパス（必須）
        output_file (str): 出力動画ファイルのパス（必須）
        start_time (int): 切り抜き開始時間（秒）（必須）
    
    Returns:
        bool: 処理が成功したかどうか
    """
    # 入力ファイルが存在するか確認
    if not os.path.exists(input_file):
        print(f"エラー: 入力ファイル '{input_file}' が見つかりません。")
        return False
    
    # FFmpegコマンドの構築
    # アスペクト比9:16、中央部分の切り抜き、30秒間、指定された開始秒数から
    command = [
        'ffmpeg',
        '-ss', str(start_time),  # 開始秒数
        '-t', str(DEFAULT_DURATION),  # 時間（30秒）
        '-i', input_file,        # 入力ファイル
        '-vf', 'crop=ih*9/16:ih:in_w/2-ih*9/32:0',  # 9:16アスペクト比でセンタリング
        '-c:a', 'copy',          # 音声はコピー
        '-y',                    # 既存ファイルを上書き
        output_file              # 出力ファイル
    ]
    
    # コマンドを表示（デバッグ用）
    print("実行するコマンド:")
    print(' '.join(command))
    
    try:
        # FFmpegコマンドを実行
        result = subprocess.run(command, check=True, stderr=subprocess.PIPE, text=True)
        print(f"成功: '{output_file}' にショート動画を生成しました。")
        return True
    except subprocess.CalledProcessError as e:
        print(f"エラー: FFmpegコマンドの実行に失敗しました。")
        print(f"エラーメッセージ: {e.stderr}")
        return False

# 使用例
if __name__ == "__main__":
    print("ショート動画生成スクリプトを開始します。")
    mp4_files = glob.glob(os.path.join(".", "*.mp4"))
    for mp4_file in mp4_files:
        print(mp4_file)
        output_file = mp4_file.replace(".mp4", "_shorts.mp4")
        # 2. 関数を直接呼び出す例
        create_youtube_short(mp4_file, output_file, 15)