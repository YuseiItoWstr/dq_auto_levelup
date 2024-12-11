import cv2
import numpy as np
import mss
import time
import pyautogui  # type:ignore
import random

def get_monitor_area_for_top_left_quarter():
    """
    画面左上の1/4領域を計算して返す。
    """
    with mss.mss() as sct:
        monitor = sct.monitors[0]  # 全画面モニタ情報を取得
        width = monitor["width"]
        height = monitor["height"]
        top = monitor["top"]
        left = monitor["left"]

        # 左上の1/4領域を計算
        monitor_area = {
            "top": top,
            "left": left,
            "width": width // 2,
            "height": height // 2
        }
        return monitor_area

def detect_template_from_screenshot(template_img, threshold, monitor_area):
    """
    指定されたテンプレート画像が画面に存在するかを検出。

    :param template_img: 検出対象のテンプレート画像
    :param threshold: 検出閾値 (0.8推奨）
    :param monitor_area: スクリーンキャプチャ領域 (Noneの場合、全画面)
    :return: True if detected, else False
    """
    with mss.mss() as sct:
        screenshot = sct.grab(monitor_area) if monitor_area else sct.grab(sct.monitors[0])
        screen_img = np.array(screenshot)
        screen_img = cv2.cvtColor(screen_img, cv2.COLOR_BGRA2BGR)

        result = cv2.matchTemplate(screen_img, template_img, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, _ = cv2.minMaxLoc(result)

        return max_val >= threshold

def detect_state(lost_metal_img, field_img, battle_cmd_img, threshold, monitor_area):
    """
    現在の状態を検出する。

    :param lost_metal_img: はぐれメタルのテンプレート画像
    :param field_img: フィールド状態のテンプレート画像
    :param battle_cmd_img: バトルコマンド状態のテンプレート画像
    :param threshold: 検出閾値
    :param monitor_area: スクリーンキャプチャ領域
    :return: 状態 ('lost_metal', 'on_field', 'in_battle', or None)
    """
    if detect_template_from_screenshot(lost_metal_img, threshold, monitor_area):
        return "lost_metal"
    if detect_template_from_screenshot(field_img, threshold, monitor_area):
        return "on_field"
    if detect_template_from_screenshot(battle_cmd_img, threshold, monitor_area):
        return "in_battle"
    return None

def perform_action(state, field_img, battle_cmd_img, threshold, monitor_area):
    """
    検出された状態に基づいて適切なキー操作を実行。

    :param state: 検出された状態
    :param field_img: フィールド状態のテンプレート画像
    :param battle_cmd_img: バトルコマンド状態のテンプレート画像
    :param threshold: 検出閾値
    :param monitor_area: スクリーンキャプチャ領域
    """
    if state == "lost_metal":
        print("はぐれメタル出現！")
        while True:
            current_state = detect_template_from_screenshot(field_img, threshold, monitor_area)
            if current_state:
                break
            pyautogui.keyDown("space")
            time.sleep(0.1)
            pyautogui.keyUp("space")

    elif state == "in_battle":
        print("バトル中")
        for _ in range(3):
            pyautogui.keyDown("up")
            time.sleep(0.1)
            pyautogui.keyUp("up")
            time.sleep(0.1)
            pyautogui.keyDown("space")
            time.sleep(0.1)
            pyautogui.keyUp("space")

    elif state == "on_field":
        print("フィールド上")
        for _ in range(5):
            # ランダムに"right"か"left"を選択
            first_key = random.choice(["right", "left"])
            second_key = "left" if first_key == "right" else "right"

            # ランダムに選択されたキーを順番に押下
            pyautogui.keyDown(first_key)
            time.sleep(0.05)
            pyautogui.keyUp(first_key)
            pyautogui.keyDown(second_key)
            time.sleep(0.05)
            pyautogui.keyUp(second_key)


def main_loop(lost_metal_path, field_path, battle_cmd_path, interval, threshold, save_folder):
    """
    連続的に画面左上1/4をキャプチャして状態を検出し、対応する動作を実行する。

    :param lost_metal_path: はぐれメタルのテンプレート画像パス
    :param field_path: フィールド状態のテンプレート画像パス
    :param battle_cmd_path: バトルコマンド状態のテンプレート画像パス
    :param interval: キャプチャ間隔（秒）
    :param threshold: 検出閾値
    :param save_folder: キャプチャ画像の保存先フォルダ
    """
    lost_metal_img = cv2.imread(lost_metal_path, cv2.IMREAD_COLOR)
    field_img = cv2.imread(field_path, cv2.IMREAD_COLOR)
    battle_cmd_img = cv2.imread(battle_cmd_path, cv2.IMREAD_COLOR)

    if lost_metal_img is None or field_img is None or battle_cmd_img is None:
        raise ValueError("いずれかのテンプレート画像が読み込めませんでした。パスを確認してください。")

    monitor_area = get_monitor_area_for_top_left_quarter()

    print("左上1/4領域での状態検出を開始します...")

    while True:
        start_time = time.time()
        state = detect_state(lost_metal_img, field_img, battle_cmd_img, threshold, monitor_area)
        if state:
            perform_action(state, field_img, battle_cmd_img, threshold, monitor_area)

        elapsed_time = time.time() - start_time
        time.sleep(max(0, interval - elapsed_time))

# 使用例
if __name__ == "__main__":
    base_path = r"C:\\Users\\yuseigpc\\dq_auto_levelup\\img\\template"
    lost_metal_path = f"{base_path}\\lost_metal.png"
    field_path = f"{base_path}\\field.png"
    battle_cmd_path = f"{base_path}\\battle_cmd.png"
    save_folder = r"C:\\Users\\yuseigpc\\dq_auto_levelup\\img\\screenshots"

    capture_interval = 3    
    detection_threshold = 0.62

    main_loop(
        lost_metal_path, 
        field_path, 
        battle_cmd_path, 
        interval=capture_interval, 
        threshold=detection_threshold, 
        save_folder=save_folder
    )











 
 
 
 
 
 
 
  
  
  
 
