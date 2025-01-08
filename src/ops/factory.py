# src/utils/factory.py
import os
from flask import Flask
from flask_pymongo import PyMongo
from dotenv import load_dotenv

load_dotenv()

# 전역으로 mongo 인스턴스 생성(초기화는 아직 안 함)
mongo = PyMongo()

def create_app():
    """Flask 애플리케이션을 생성해 반환하는 함수(팩토리 패턴)"""
    app = Flask(
        __name__,
        template_folder="../templates",  # src 기준 상대 경로
        static_folder="../static"
    )

    app.config["MONGO_URI"] =  os.getenv("MONGO_URI")

    # PyMongo 초기화
    mongo.init_app(app)

    # 블루프린트, 라우팅, 기타 설정 등이 있다면 여기서 app에 등록
    # from .routes import main_bp
    # app.register_blueprint(main_bp)

    return app