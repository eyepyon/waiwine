import streamlit as st
import os
from dotenv import load_dotenv
from livekit import api
import sqlite3
from datetime import datetime
import json

# 環境変数の読み込み
load_dotenv()

# データベース初期化
def init_db():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            google_id TEXT UNIQUE,
            email TEXT,
            name TEXT,
            main_language TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

# ユーザー登録
def register_user(google_id, email, name, main_language):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    try:
        c.execute('''
            INSERT INTO users (google_id, email, name, main_language)
            VALUES (?, ?, ?, ?)
        ''', (google_id, email, name, main_language))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

# ユーザー取得
def get_user(google_id):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('SELECT * FROM users WHERE google_id = ?', (google_id,))
    user = c.fetchone()
    conn.close()
    return user

# LiveKit トークン生成
def generate_livekit_token(user_id, room_name):
    token = api.AccessToken(
        api_key=os.getenv('LIVEKIT_API_KEY'),
        api_secret=os.getenv('LIVEKIT_API_SECRET')
    )
    token.with_identity(user_id)
    token.with_name(user_id)
    token.with_grants(api.VideoGrants(
        room_join=True,
        room=room_name,
        can_publish=True,
        can_subscribe=True
    ))
    return token.to_jwt()

def main():
    st.set_page_config(
        page_title="LiveKit Video Chat App",
        page_icon="🎥",
        layout="wide"
    )
    
    init_db()
    
    # セッション状態の初期化
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'user_data' not in st.session_state:
        st.session_state.user_data = None
    
    # メインアプリケーション
    if not st.session_state.authenticated:
        show_login_page()
    else:
        show_main_app()

def show_login_page():
    st.title("🎥 LiveKit Video Chat App")
    st.markdown("### ようこそ！")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("---")
        st.markdown("#### Googleアカウントでログイン")
        
        # 簡易的なログインシミュレーション（実際の実装では Google OAuth を使用）
        with st.form("login_form"):
            email = st.text_input("メールアドレス", placeholder="example@gmail.com")
            name = st.text_input("名前", placeholder="山田太郎")
            
            if st.form_submit_button("🔐 Googleでログイン", use_container_width=True):
                if email and name:
                    # 簡易的なGoogle IDシミュレーション
                    google_id = f"google_{hash(email)}"
                    
                    # ユーザー確認
                    user = get_user(google_id)
                    
                    if user:
                        # 既存ユーザー
                        st.session_state.authenticated = True
                        st.session_state.user_data = {
                            'google_id': user[1],
                            'email': user[2],
                            'name': user[3],
                            'main_language': user[4]
                        }
                        st.rerun()
                    else:
                        # 新規ユーザー - 言語選択
                        st.session_state.temp_user = {
                            'google_id': google_id,
                            'email': email,
                            'name': name
                        }
                        st.session_state.show_language_selection = True
                        st.rerun()
    
    # 言語選択画面
    if hasattr(st.session_state, 'show_language_selection') and st.session_state.show_language_selection:
        show_language_selection()

def show_language_selection():
    st.markdown("---")
    st.markdown("#### メイン言語を選択してください")
    
    languages = {
        'ja': '日本語',
        'en': 'English',
        'ko': '한국어',
        'zh': '中文',
        'es': 'Español',
        'fr': 'Français',
        'de': 'Deutsch'
    }
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        selected_language = st.selectbox(
            "メイン言語",
            options=list(languages.keys()),
            format_func=lambda x: languages[x]
        )
        
        if st.button("登録完了", use_container_width=True):
            temp_user = st.session_state.temp_user
            
            # ユーザー登録
            if register_user(
                temp_user['google_id'],
                temp_user['email'],
                temp_user['name'],
                selected_language
            ):
                st.session_state.authenticated = True
                st.session_state.user_data = {
                    'google_id': temp_user['google_id'],
                    'email': temp_user['email'],
                    'name': temp_user['name'],
                    'main_language': selected_language
                }
                # 一時データをクリア
                del st.session_state.temp_user
                del st.session_state.show_language_selection
                st.success("登録が完了しました！")
                st.rerun()
            else:
                st.error("登録に失敗しました。")

def show_main_app():
    user_data = st.session_state.user_data
    
    # ヘッダー
    col1, col2 = st.columns([3, 1])
    with col1:
        st.title(f"こんにちは、{user_data['name']}さん！")
    with col2:
        if st.button("ログアウト"):
            st.session_state.authenticated = False
            st.session_state.user_data = None
            st.rerun()
    
    st.markdown("---")
    
    # メイン機能
    tab1, tab2, tab3 = st.tabs(["🎥 ビデオチャット", "⚙️ 設定", "👥 ルーム一覧"])
    
    with tab1:
        show_video_chat()
    
    with tab2:
        show_settings()
    
    with tab3:
        show_room_list()

def show_video_chat():
    st.markdown("### ビデオチャットルーム")
    
    col1, col2 = st.columns(2)
    
    with col1:
        room_name = st.text_input("ルーム名", value="general")
    
    with col2:
        if st.button("ルームに参加", use_container_width=True):
            user_data = st.session_state.user_data
            token = generate_livekit_token(user_data['google_id'], room_name)
            
            # LiveKit接続情報を表示
            st.success(f"ルーム '{room_name}' に参加準備完了！")
            
            # フロントエンド用の接続情報
            connection_info = {
                'url': os.getenv('LIVEKIT_URL'),
                'token': token,
                'room': room_name
            }
            
            st.json(connection_info)
            st.markdown("**フロントエンドでこの情報を使用してLiveKitに接続してください。**")

def show_settings():
    st.markdown("### ユーザー設定")
    
    user_data = st.session_state.user_data
    
    languages = {
        'ja': '日本語',
        'en': 'English',
        'ko': '한국어',
        'zh': '中文',
        'es': 'Español',
        'fr': 'Français',
        'de': 'Deutsch'
    }
    
    current_lang_index = list(languages.keys()).index(user_data['main_language'])
    
    new_language = st.selectbox(
        "メイン言語",
        options=list(languages.keys()),
        index=current_lang_index,
        format_func=lambda x: languages[x]
    )
    
    if st.button("設定を更新"):
        # データベース更新
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        c.execute(
            'UPDATE users SET main_language = ? WHERE google_id = ?',
            (new_language, user_data['google_id'])
        )
        conn.commit()
        conn.close()
        
        # セッション更新
        st.session_state.user_data['main_language'] = new_language
        st.success("設定が更新されました！")

def show_room_list():
    st.markdown("### アクティブなルーム")
    
    # 簡易的なルーム一覧（実際の実装ではLiveKit APIを使用）
    rooms = [
        {"name": "general", "participants": 3},
        {"name": "meeting-room-1", "participants": 5},
        {"name": "casual-chat", "participants": 2}
    ]
    
    for room in rooms:
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            st.write(f"**{room['name']}**")
        
        with col2:
            st.write(f"👥 {room['participants']} 人")
        
        with col3:
            if st.button(f"参加", key=f"join_{room['name']}"):
                user_data = st.session_state.user_data
                token = generate_livekit_token(user_data['google_id'], room['name'])
                st.success(f"ルーム '{room['name']}' に参加準備完了！")

if __name__ == "__main__":
    main()