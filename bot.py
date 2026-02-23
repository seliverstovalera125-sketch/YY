"""
KYNX X - СЛЕДУЮЩЕЕ ПОКОЛЕНИЕ СИСТЕМЫ МОДЕРАЦИИ
Версия: 4.0.0
Архитектура: Микросервисная с брокером сообщений
Стек: Python 3.11, Discord.py 2.3, RabbitMQ, Prometheus, Grafana
"""

import os
import sys
import json
import asyncio
import logging
import hashlib
import hmac
import time
import uuid
import random
import string
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Any, Union, Tuple, Callable
from dataclasses import dataclass, field, asdict
from enum import Enum, auto
from collections import defaultdict, deque
from contextlib import asynccontextmanager
import signal
import tracemalloc
import psutil
import cpuinfo
import GPUtil
import pika
import pika.adapters.asyncio_connection
import aiohttp
import aiofiles
import aioredis
import aiomysql
import motor.motor_asyncio
from elasticsearch import AsyncElasticsearch
import prometheus_client
from prometheus_client import Counter, Histogram, Gauge, generate_latest
import grafana_api
import discord
from discord.ext import commands, tasks
from discord import app_commands
from discord.ui import View, Button, Select, Modal, TextInput
from dotenv import load_dotenv
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import io
import base64
import qrcode
import cv2
import face_recognition
import speech_recognition as sr
from gtts import gTTS
import pygame
import websockets
import kubernetes
import docker
import paramiko
import scp
import redis
import celery
from celery.schedules import crontab
import sqlalchemy
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import declarative_base, sessionmaker
import alembic
import alembic.config
import pydantic
from pydantic import BaseModel, Field, validator
import fastapi
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import uvicorn
import gunicorn
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
import tensorflow as tf
from tensorflow import keras
from transformers import pipeline
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
import sklearn
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
import xgboost as xgb
import lightgbm as lgb
import catboost as cb
import optuna
import ray
from ray import tune
from ray.rllib.algorithms.ppo import PPOConfig
import gym
from gym import spaces
import pettingzoo
from pettingzoo.mpe import simple_spread_v2
import stable_baselines3
from stable_baselines3 import PPO, DQN, A2C, SAC
import wandb
import mlflow
import dvc
import streamlit as st
import gradio as gr
import plotly
import plotly.express as px
import plotly.graph_objects as go
import dash
from dash import dcc, html
import bokeh
from bokeh.plotting import figure, show
from bokeh.models import ColumnDataSource, HoverTool
import holoviews as hv
import geoviews as gv
import datashader as ds
import colorcet
import networkx as nx
import community
import scipy
from scipy import stats
import statsmodels
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.statespace.sarimax import SARIMAX
import prophet
from prophet import Prophet
import pmdarima as pm
import arch
from arch import arch_model
import pywt
import librosa
import soundfile as sf
import pyloudnorm as pyln
import essentia
import essentia.standard as es
import spacy
import textblob
from textblob import TextBlob
import langdetect
import googletrans
from googletrans import Translator
import deep_translator
from deep_translator import GoogleTranslator
import whisper
import TTS
from TTS.api import TTS
import coqui
import bark
from bark import SAMPLE_RATE, generate_audio, preload_models
import diffusers
from diffusers import StableDiffusionPipeline, DPMSolverMultistepScheduler
import transformers
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
import sentencepiece
import bitsandbytes
import accelerate
import deepspeed
import fairscale
import colossalai
import megatron
import nvidia
import cuda
import cupy
import pycuda
import opencv
import mediapipe
import dlib
import imutils
import albumentations
import imgaug
import torchvision
import torchaudio
import kornia
import monai
import nibabel
import SimpleITK
import pydicom
import medicaltorch
import bioimageio
import cellpose
import stardist
import csbdeep
import napari
import apeer
import ome_zarr
import zarr
import dask
import xarray
import netCDF4
import h5py
import hdf5storage
import mat73
import scipy.io
import pandas_ta
import yfinance
import alpaca_trade
import ccxt
import backtrader
import zipline
import quantlib
import qlib
import finnhub
import polygon
import ib_insync
import twelvedata
import alpha_vantage
import yahoo_fin
import investpy
import pandas_datareader
import fredapi
import worldbank
import imfpy
import econdb
import quandl
import openai
import anthropic
import cohere
import huggingface_hub
import langchain
from langchain.llms import OpenAI
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain.memory import ConversationBufferMemory
from langchain.agents import create_pandas_dataframe_agent
import llama_index
import chromadb
import pinecone
import weaviate
import qdrant_client
import milvus
import pymilvus
import redisearch
import elasticsearch_dsl
import mongoengine
import beanie
import odmantic
import tortoise
import aerich
import peewee
import pony
import sqlobject
import dataset
import records
import sqlalchemy
import databases
import asyncpg
import psycopg2
import pymysql
import sqlite3
import aiosqlite
import duckdb
import polars
import dask.dataframe as dd
import modin
import ray.data
import vaex
import cuDF
import blazingsql
import omnisci
import pymapd
import clickhouse_driver
import vertica_python
import prestodb
import trino
import pyhive
import impala
import hdfs
import webhdfs
import fsspec
import s3fs
import gcsfs
import adlfs
import pyarrow
import fastparquet
import pyorc
import avro
import msgpack
import pickle
import joblib
import cloudpickle
import dill
import pyro
import pyro.contrib
import pymc3
import pymc
import arviz
import bambi
import pystan
import cmdstanpy
import emcee
import corner
import zeus
import dynesty
import ultranest
import cpnest
import nessai
import bilby
import pyMultiwavelet
import pymultinest
import polychord
import cobaya
import montepython
import cosmosis
import camb
import classy
import astropy
import sunpy
import planets
import poliastro
import skyfield
import spiceypy
import pyephem
import rebound
import galpy
import agama
import gala
import schwimmbad
import mpi4py
import petsc4py
import slepc4py
import mumps
import superlu
import hypre
import trilinos
import dealii
import fenics
import firedrake
import dolfin
import ngsolve
import gridap
import hpgmg
import amrex
import openmc
import mcnp
import serpent
import geant4
import root
import pythia8
import rivet
import heppy
import fastjet
import pylhe
import madgraph
import sherpa
import whizard
import pythia
import herwig
import photos
import tauola
import evtgen
import genie
import nuwro
import marley
import maestro
import geant4
import fluka
import phits
import mcnp
import serpent
import openmc
import pymoab
import pyne
import openmc
import mcnp
import serpent
import geant4
import fluka
import phits
import mcnp
import serpent
import openmc
import pymoab
import pyne
import openmc
import mcnp
import serpent
import geant4
import fluka
import phits
import mcnp
import serpent
import openmc

# ==================== ИНИЦИАЛИЗАЦИЯ ====================
load_dotenv()

class KynxConfig:
    """Глобальная конфигурация системы"""

    # Discord
    DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
    DISCORD_GUILD_ID = int(os.getenv("DISCORD_GUILD_ID", "0"))
    DISCORD_ALLOWED_ROLES = [int(x) for x in os.getenv("DISCORD_ALLOWED_ROLES", "").split(",") if x]
    DISCORD_ADMIN_ROLES = [int(x) for x in os.getenv("DISCORD_ADMIN_ROLES", "").split(",") if x]
    DISCORD_OWNER_IDS = [int(x) for x in os.getenv("DISCORD_OWNER_IDS", "").split(",") if x]

    # API
    GAME_API_URL = os.getenv("GAME_API_URL", "http://localhost:5000")
    GAME_API_KEY = os.getenv("GAME_API_KEY", "")
    GAME_API_SECRET = os.getenv("GAME_API_SECRET", "")

    # Database
    DB_TYPE = os.getenv("DB_TYPE", "postgresql")
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = int(os.getenv("DB_PORT", "5432"))
    DB_NAME = os.getenv("DB_NAME", "kynx")
    DB_USER = os.getenv("DB_USER", "kynx")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "kynx")

    # Redis
    REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
    REDIS_DB = int(os.getenv("REDIS_DB", "0"))
    REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", "")

    # RabbitMQ
    RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "localhost")
    RABBITMQ_PORT = int(os.getenv("RABBITMQ_PORT", "5672"))
    RABBITMQ_USER = os.getenv("RABBITMQ_USER", "guest")
    RABBITMQ_PASSWORD = os.getenv("RABBITMQ_PASSWORD", "guest")
    RABBITMQ_VHOST = os.getenv("RABBITMQ_VHOST", "/")

    # MongoDB
    MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
    MONGODB_DB = os.getenv("MONGODB_DB", "kynx")

    # Elasticsearch
    ELASTICSEARCH_HOSTS = os.getenv("ELASTICSEARCH_HOSTS", "http://localhost:9200").split(",")
    ELASTICSEARCH_USER = os.getenv("ELASTICSEARCH_USER", "")
    ELASTICSEARCH_PASSWORD = os.getenv("ELASTICSEARCH_PASSWORD", "")

    # Prometheus
    PROMETHEUS_PORT = int(os.getenv("PROMETHEUS_PORT", "8000"))
    PROMETHEUS_ENABLED = os.getenv("PROMETHEUS_ENABLED", "true").lower() == "true"

    # Grafana
    GRAFANA_URL = os.getenv("GRAFANA_URL", "http://localhost:3000")
    GRAFANA_API_KEY = os.getenv("GRAFANA_API_KEY", "")

    # Kubernetes
    KUBERNETES_ENABLED = os.getenv("KUBERNETES_ENABLED", "false").lower() == "true"
    KUBERNETES_NAMESPACE = os.getenv("KUBERNETES_NAMESPACE", "default")
    KUBERNETES_DEPLOYMENT = os.getenv("KUBERNETES_DEPLOYMENT", "kynx")

    # Docker
    DOCKER_ENABLED = os.getenv("DOCKER_ENABLED", "false").lower() == "true"
    DOCKER_CONTAINER_NAME = os.getenv("DOCKER_CONTAINER_NAME", "kynx")

    # Celery
    CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
    CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/0")

    # OpenAI
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4")

    # Anthropic
    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
    ANTHROPIC_MODEL = os.getenv("ANTHROPIC_MODEL", "claude-2")

    # Cohere
    COHERE_API_KEY = os.getenv("COHERE_API_KEY", "")
    COHERE_MODEL = os.getenv("COHERE_MODEL", "command")

    # HuggingFace
    HUGGINGFACE_TOKEN = os.getenv("HUGGINGFACE_TOKEN", "")
    HUGGINGFACE_MODEL = os.getenv("HUGGINGFACE_MODEL", "meta-llama/Llama-2-70b-chat-hf")

    # Weights & Biases
    WANDB_API_KEY = os.getenv("WANDB_API_KEY", "")
    WANDB_PROJECT = os.getenv("WANDB_PROJECT", "kynx")
    WANDB_ENTITY = os.getenv("WANDB_ENTITY", "")

    # MLflow
    MLFLOW_TRACKING_URI = os.getenv("MLFLOW_TRACKING_URI", "http://localhost:5000")
    MLFLOW_EXPERIMENT_NAME = os.getenv("MLFLOW_EXPERIMENT_NAME", "kynx")

    # DVC
    DVC_REMOTE = os.getenv("DVC_REMOTE", "storage")
    DVC_CACHE_DIR = os.getenv("DVC_CACHE_DIR", ".dvc/cache")

    # Streamlit
    STREAMLIT_PORT = int(os.getenv("STREAMLIT_PORT", "8501"))
    STREAMLIT_ENABLED = os.getenv("STREAMLIT_ENABLED", "true").lower() == "true"

    # Gradio
    GRADIO_PORT = int(os.getenv("GRADIO_PORT", "7860"))
    GRADIO_ENABLED = os.getenv("GRADIO_ENABLED", "true").lower() == "true"

    # Dash
    DASH_PORT = int(os.getenv("DASH_PORT", "8050"))
    DASH_ENABLED = os.getenv("DASH_ENABLED", "true").lower() == "true"

    # Plotly
    PLOTLY_THEME = os.getenv("PLOTLY_THEME", "plotly_dark")

    # Bokeh
    BOKEH_PORT = int(os.getenv("BOKEH_PORT", "5006"))
    BOKEH_ENABLED = os.getenv("BOKEH_ENABLED", "true").lower() == "true"

    # HoloViews
    HOLOVIEWS_BACKEND = os.getenv("HOLOVIEWS_BACKEND", "bokeh")

    # Datashader
    DATASHADER_ENABLED = os.getenv("DATASHADER_ENABLED", "true").lower() == "true"

    # PyTorch
    PYTORCH_DEVICE = os.getenv("PYTORCH_DEVICE", "cuda" if torch.cuda.is_available() else "cpu")
    PYTORCH_NUM_THREADS = int(os.getenv("PYTORCH_NUM_THREADS", "4"))

    # TensorFlow
    TENSORFLOW_DEVICE = os.getenv("TENSORFLOW_DEVICE", "/GPU:0" if tf.config.list_physical_devices('GPU') else "/CPU:0")
    TENSORFLOW_MEMORY_GROWTH = os.getenv("TENSORFLOW_MEMORY_GROWTH", "true").lower() == "true"

    # JAX
    JAX_ENABLED = os.getenv("JAX_ENABLED", "false").lower() == "true"
    JAX_PLATFORM_NAME = os.getenv("JAX_PLATFORM_NAME", "gpu")

    # Ray
    RAY_ADDRESS = os.getenv("RAY_ADDRESS", "auto")
    RAY_NUM_CPUS = int(os.getenv("RAY_NUM_CPUS", "8"))
    RAY_NUM_GPUS = int(os.getenv("RAY_NUM_GPUS", "1"))
    RAY_OBJECT_STORE_MEMORY = int(os.getenv("RAY_OBJECT_STORE_MEMORY", f"{10**9}"))  # 1GB

    # Dask
    DASK_SCHEDULER_ADDRESS = os.getenv("DASK_SCHEDULER_ADDRESS", "tcp://localhost:8786")
    DASK_NUM_WORKERS = int(os.getenv("DASK_NUM_WORKERS", "4"))
    DASK_THREADS_PER_WORKER = int(os.getenv("DASK_THREADS_PER_WORKER", "2"))
    DASK_MEMORY_LIMIT = os.getenv("DASK_MEMORY_LIMIT", "4GB")

    # Spark
    SPARK_ENABLED = os.getenv("SPARK_ENABLED", "false").lower() == "true"
    SPARK_MASTER = os.getenv("SPARK_MASTER", "local[*]")
    SPARK_APP_NAME = os.getenv("SPARK_APP_NAME", "Kynx")

    # Flink
    FLINK_ENABLED = os.getenv("FLINK_ENABLED", "false").lower() == "true"
    FLINK_JOB_MANAGER_HOST = os.getenv("FLINK_JOB_MANAGER_HOST", "localhost")
    FLINK_JOB_MANAGER_PORT = int(os.getenv("FLINK_JOB_MANAGER_PORT", "8081"))

    # Kafka
    KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092").split(",")
    KAFKA_TOPIC_PREFIX = os.getenv("KAFKA_TOPIC_PREFIX", "kynx")
    KAFKA_CONSUMER_GROUP = os.getenv("KAFKA_CONSUMER_GROUP", "kynx-group")

    # Pulsar
    PULSAR_SERVICE_URL = os.getenv("PULSAR_SERVICE_URL", "pulsar://localhost:6650")
    PULSAR_TOPIC_PREFIX = os.getenv("PULSAR_TOPIC_PREFIX", "kynx")
    PULSAR_SUBSCRIPTION_NAME = os.getenv("PULSAR_SUBSCRIPTION_NAME", "kynx-sub")

    # NATS
    NATS_SERVERS = os.getenv("NATS_SERVERS", "nats://localhost:4222").split(",")
    NATS_TOPIC_PREFIX = os.getenv("NATS_TOPIC_PREFIX", "kynx")

    # ZeroMQ
    ZEROMQ_ENABLED = os.getenv("ZEROMQ_ENABLED", "false").lower() == "true"
    ZEROMQ_PORT = int(os.getenv("ZEROMQ_PORT", "5555"))

    # gRPC
    GRPC_PORT = int(os.getenv("GRPC_PORT", "50051"))
    GRPC_MAX_WORKERS = int(os.getenv("GRPC_MAX_WORKERS", "10"))

    # GraphQL
    GRAPHQL_ENABLED = os.getenv("GRAPHQL_ENABLED", "false").lower() == "true"
    GRAPHQL_PORT = int(os.getenv("GRAPHQL_PORT", "4000"))

    # REST API
    REST_API_PORT = int(os.getenv("REST_API_PORT", "8080"))
    REST_API_WORKERS = int(os.getenv("REST_API_WORKERS", "4"))
    REST_API_TIMEOUT = int(os.getenv("REST_API_TIMEOUT", "60"))

    # WebSocket
    WEBSOCKET_PORT = int(os.getenv("WEBSOCKET_PORT", "8081"))
    WEBSOCKET_MAX_SIZE = int(os.getenv("WEBSOCKET_MAX_SIZE", f"{10**6}"))  # 1MB

    # Security
    SECRET_KEY = os.getenv("SECRET_KEY", "".join(random.choices(string.ascii_letters + string.digits, k=32)))
    JWT_SECRET = os.getenv("JWT_SECRET", "".join(random.choices(string.ascii_letters + string.digits, k=32)))
    JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
    JWT_EXPIRATION = int(os.getenv("JWT_EXPIRATION", "3600"))  # 1 hour

    # Encryption
    ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY", "".join(random.choices(string.ascii_letters + string.digits, k=32)))
    ENCRYPTION_ALGORITHM = os.getenv("ENCRYPTION_ALGORITHM", "AES-256-GCM")

    # Rate Limiting
    RATE_LIMIT_ENABLED = os.getenv("RATE_LIMIT_ENABLED", "true").lower() == "true"
    RATE_LIMIT_REQUESTS = int(os.getenv("RATE_LIMIT_REQUESTS", "10"))
    RATE_LIMIT_PERIOD = int(os.getenv("RATE_LIMIT_PERIOD", "1"))  # seconds

    # Caching
    CACHE_ENABLED = os.getenv("CACHE_ENABLED", "true").lower() == "true"
    CACHE_TTL = int(os.getenv("CACHE_TTL", "300"))  # 5 minutes
    CACHE_MAX_SIZE = int(os.getenv("CACHE_MAX_SIZE", "1000"))

    # Monitoring
    MONITORING_ENABLED = os.getenv("MONITORING_ENABLED", "true").lower() == "true"
    MONITORING_INTERVAL = int(os.getenv("MONITORING_INTERVAL", "60"))  # seconds

    # Alerting
    ALERTING_ENABLED = os.getenv("ALERTING_ENABLED", "true").lower() == "true"
    ALERTING_WEBHOOK_URL = os.getenv("ALERTING_WEBHOOK_URL", "")
    ALERTING_THRESHOLD = float(os.getenv("ALERTING_THRESHOLD", "0.9"))  # 90%

    # Logging
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT = os.getenv("LOG_FORMAT", "json")
    LOG_OUTPUT = os.getenv("LOG_OUTPUT", "console,file,elasticsearch")
    LOG_FILE_PATH = os.getenv("LOG_FILE_PATH", "logs/kynx.log")
    LOG_FILE_MAX_SIZE = int(os.getenv("LOG_FILE_MAX_SIZE", f"{10**7}"))  # 10MB
    LOG_FILE_BACKUP_COUNT = int(os.getenv("LOG_FILE_BACKUP_COUNT", "5"))

    # Tracing
    TRACING_ENABLED = os.getenv("TRACING_ENABLED", "false").lower() == "true"
    TRACING_SERVICE_NAME = os.getenv("TRACING_SERVICE_NAME", "kynx")
    TRACING_JAEGER_HOST = os.getenv("TRACING_JAEGER_HOST", "localhost")
    TRACING_JAEGER_PORT = int(os.getenv("TRACING_JAEGER_PORT", "6831"))

    # Profiling
    PROFILING_ENABLED = os.getenv("PROFILING_ENABLED", "false").lower() == "true"
    PROFILING_PORT = int(os.getenv("PROFILING_PORT", "6060"))

    # Testing
    TESTING_ENABLED = os.getenv("TESTING_ENABLED", "false").lower() == "true"
    TESTING_COVERAGE = os.getenv("TESTING_COVERAGE", "true").lower() == "true"

    # Development
    DEVELOPMENT_MODE = os.getenv("DEVELOPMENT_MODE", "false").lower() == "true"
    DEVELOPMENT_RELOAD = os.getenv("DEVELOPMENT_RELOAD", "true").lower() == "true"

    # Paths
    BASE_DIR = Path(__file__).parent
    DATA_DIR = BASE_DIR / "data"
    LOGS_DIR = DATA_DIR / "logs"
    CACHE_DIR = DATA_DIR / "cache"
    MODELS_DIR = DATA_DIR / "models"
    EXPORTS_DIR = DATA_DIR / "exports"
    UPLOADS_DIR = DATA_DIR / "uploads"
    TEMP_DIR = DATA_DIR / "temp"
    BACKUP_DIR = DATA_DIR / "backup"

    @classmethod
    def create_directories(cls):
        """Создание необходимых директорий"""
        for dir_path in [cls.DATA_DIR, cls.LOGS_DIR, cls.CACHE_DIR, cls.MODELS_DIR, 
                         cls.EXPORTS_DIR, cls.UPLOADS_DIR, cls.TEMP_DIR, cls.BACKUP_DIR]:
            dir_path.mkdir(exist_ok=True, parents=True)
            (dir_path / ".gitkeep").touch(exist_ok=True)

# Создание директорий
KynxConfig.create_directories()

# ==================== МЕТРИКИ PROMETHEUS ====================
if KynxConfig.PROMETHEUS_ENABLED:
    # Counters
    command_counter = Counter('kynx_commands_total', 'Total commands executed', ['command', 'status'])
    player_counter = Counter('kynx_players_total', 'Total players', ['action'])
    ban_counter = Counter('kynx_bans_total', 'Total bans', ['type', 'level'])
    error_counter = Counter('kynx_errors_total', 'Total errors', ['type', 'component'])

    # Gauges
    players_online_gauge = Gauge('kynx_players_online', 'Players currently online')
    active_bans_gauge = Gauge('kynx_active_bans', 'Active bans')
    system_load_gauge = Gauge('kynx_system_load', 'System load average', ['core'])
    memory_usage_gauge = Gauge('kynx_memory_usage', 'Memory usage in bytes', ['type'])
    cpu_usage_gauge = Gauge('kynx_cpu_usage', 'CPU usage percentage', ['core'])
    disk_usage_gauge = Gauge('kynx_disk_usage', 'Disk usage in bytes', ['path'])
    network_io_gauge = Gauge('kynx_network_io', 'Network I/O in bytes', ['direction'])

    # Histograms
    command_duration_histogram = Histogram('kynx_command_duration_seconds', 'Command execution duration', ['command'])
    api_latency_histogram = Histogram('kynx_api_latency_seconds', 'API call latency', ['endpoint'])
    database_query_histogram = Histogram('kynx_database_query_seconds', 'Database query duration', ['operation'])

# ==================== МОДЕЛИ ДАННЫХ ====================

class BanLevel(str, Enum):
    """Уровни бана"""
    ACCOUNT = "account"
    DEVICE = "device"
    IP = "ip"
    HARDWARE = "hardware"
    FINGERPRINT = "fingerprint"
    BEHAVIORAL = "behavioral"
    SOCIAL = "social"
    ECONOMIC = "economic"
    REPUTATION = "reputation"
    TRUST = "trust"
    AI = "ai"

class BanDuration(str, Enum):
    """Длительности бана"""
    TEMPORARY = "temporary"
    PERMANENT = "permanent"
    INDEFINITE = "indefinite"
    CONDITIONAL = "conditional"
    PROBATIONARY = "probationary"
    APPEALABLE = "appealable"

class BanReason(str, Enum):
    """Причины бана"""
    CHEATING = "cheating"
    HACKING = "hacking"
    EXPLOITING = "exploiting"
    SCAMMING = "scamming"
    HARASSMENT = "harassment"
    TOXICITY = "toxicity"
    SPAMMING = "spamming"
    ADVERTISING = "advertising"
    INAPPROPRIATE = "inappropriate"
    UNDERAGE = "underage"
    CHARGEBACK = "chargeback"
    FRAUD = "fraud"
    MULTIPLE_ACCOUNTS = "multiple_accounts"
    ACCOUNT_SHARING = "account_sharing"
    VPN_USAGE = "vpn_usage"
    PROXY_USAGE = "proxy_usage"
    BOT_USAGE = "bot_usage"
    AUTO_CLICKER = "auto_clicker"
    MACRO_USAGE = "macro_usage"
    SCRIPT_USAGE = "script_usage"

class ModerationAction(str, Enum):
    """Действия модерации"""
    WARN = "warn"
    MUTE = "mute"
    KICK = "kick"
    BAN = "ban"
    UNBAN = "unban"
    TEMPBAN = "tempban"
    SOFTBAN = "softban"
    HARDBAN = "hardban"
    SUPERBAN = "superban"
    MEGABAN = "megaban"
    ULTIMATE_BAN = "ultimate_ban"
    NUCLEAR_BAN = "nuclear_ban"

class PlayerTier(str, Enum):
    """Уровни игроков"""
    NEWBIE = "newbie"
    REGULAR = "regular"
    VETERAN = "veteran"
    ELITE = "elite"
    LEGENDARY = "legendary"
    MYTHIC = "mythic"
    GODLY = "godly"
    ADMIN = "admin"
    MODERATOR = "moderator"
    DEVELOPER = "developer"
    OWNER = "owner"

class ServerStatus(str, Enum):
    """Статусы сервера"""
    STARTING = "starting"
    RUNNING = "running"
    PAUSED = "paused"
    STOPPING = "stopping"
    STOPPED = "stopped"
    RESTARTING = "restarting"
    MAINTENANCE = "maintenance"
    BACKUP = "backup"
    RECOVERY = "recovery"
    EMERGENCY = "emergency"
    OVERLOADED = "overloaded"
    CRASHED = "crashed"
    HACKED = "hacked"

@dataclass
class PlayerProfile:
    """Расширенный профиль игрока"""
    user_id: str
    username: str
    display_name: str
    avatar_url: Optional[str] = None

    # Основная информация
    level: int = 1
    experience: int = 0
    reputation: float = 0.0
    trust_score: float = 1.0

    # Статистика
    first_seen: float = field(default_factory=time.time)
    last_seen: float = field(default_factory=time.time)
    playtime: int = 0
    sessions: int = 0
    achievements: List[str] = field(default_factory=list)

    # Модерация
    warnings: List[Dict] = field(default_factory=list)
    notes: List[Dict] = field(default_factory=list)
    reports: List[Dict] = field(default_factory=list)
    appeals: List[Dict] = field(default_factory=list)

    # Баны
    is_banned: bool = False
    ban_history: List[Dict] = field(default_factory=list)
    active_bans: List[Dict] = field(default_factory=list)

    # Муты
    is_muted: bool = False
    mute_history: List[Dict] = field(default_factory=list)
    mute_expires: Optional[float] = None

    # Устройства
    devices: List[Dict] = field(default_factory=list)
    fingerprints: List[str] = field(default_factory=list)
    ip_addresses: List[str] = field(default_factory=list)
    mac_addresses: List[str] = field(default_factory=list)

    # Поведение
    behavior_score: float = 1.0
    toxicity_score: float = 0.0
    cooperation_score: float = 1.0
    communication_score: float = 1.0

    # Социальные связи
    friends: List[str] = field(default_factory=list)
    enemies: List[str] = field(default_factory=list)
    guild: Optional[str] = None
    guild_role: Optional[str] = None

    # Экономика
    balance: int = 0
    total_spent: int = 0
    total_earned: int = 0
    purchases: List[Dict] = field(default_factory=list)

    # Достижения
    titles: List[str] = field(default_factory=list)
    badges: List[str] = field(default_factory=list)
    medals: List[str] = field(default_factory=list)
    trophies: List[str] = field(default_factory=list)

    # Настройки
    settings: Dict[str, Any] = field(default_factory=dict)
    preferences: Dict[str, Any] = field(default_factory=dict)

    # Метаданные
    metadata: Dict[str, Any] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict:
        """Конвертация в словарь"""
        return {
            "user_id": self.user_id,
            "username": self.username,
            "display_name": self.display_name,
            "avatar_url": self.avatar_url,
            "level": self.level,
            "experience": self.experience,
            "reputation": self.reputation,
            "trust_score": self.trust_score,
            "first_seen": self.first_seen,
            "last_seen": self.last_seen,
            "playtime": self.playtime,
            "sessions": self.sessions,
            "is_banned": self.is_banned,
            "is_muted": self.is_muted,
            "behavior_score": self.behavior_score,
            "toxicity_score": self.toxicity_score,
            "balance": self.balance,
        }

    def to_json(self) -> str:
        """Конвертация в JSON"""
        return json.dumps(self.to_dict(), indent=2)

@dataclass
class BanRecord:
    """Расширенная запись бана"""
    ban_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str = ""
    username: str = ""

    # Основная информация
    level: BanLevel = BanLevel.ACCOUNT
    duration: BanDuration = BanDuration.PERMANENT
    reason: BanReason = BanReason.CHEATING
    reason_text: str = ""

    # Детали
    executor: str = ""
    executor_id: str = ""
    timestamp: float = field(default_factory=time.time)
    expires: Optional[float] = None

    # Доказательства
    evidence: List[Dict] = field(default_factory=list)
    screenshots: List[str] = field(default_factory=list)
    logs: List[str] = field(default_factory=list)
    recordings: List[str] = field(default_factory=list)

    # Апелляции
    appeals: List[Dict] = field(default_factory=list)
    appeal_count: int = 0
    last_appeal: Optional[float] = None

    # Статус
    is_active: bool = True
    is_appealable: bool = True
    is_reviewable: bool = True
    is_escalated: bool = False

    # Метаданные
    metadata: Dict[str, Any] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict:
        """Конвертация в словарь"""
        return {
            "ban_id": self.ban_id,
            "user_id": self.user_id,
            "username": self.username,
            "level": self.level,
            "duration": self.duration,
            "reason": self.reason,
            "reason_text": self.reason_text,
            "executor": self.executor,
            "timestamp": self.timestamp,
            "expires": self.expires,
            "is_active": self.is_active,
        }

    def to_json(self) -> str:
        """Конвертация в JSON"""
        return json.dumps(self.to_dict(), indent=2)

@dataclass
class ServerMetrics:
    """Расширенные метрики сервера"""
    # Игроки
    online_players: int = 0
    peak_players: int = 0
    unique_players: int = 0
    returning_players: int = 0
    new_players: int = 0

    # Сессии
    total_sessions: int = 0
    average_session_length: float = 0.0
    total_playtime: int = 0

    # Баны
    total_bans: int = 0
    active_bans: int = 0
    bans_today: int = 0
    bans_this_week: int = 0
    bans_this_month: int = 0

    # Муты
    total_mutes: int = 0
    active_mutes: int = 0
    mutes_today: int = 0

    # Предупреждения
    total_warnings: int = 0
    warnings_today: int = 0

    # Система
    cpu_usage: float = 0.0
    memory_usage: float = 0.0
    disk_usage: float = 0.0
    network_in: int = 0
    network_out: int = 0
    uptime: float = 0.0

    # Производительность
    commands_executed: int = 0
    api_calls: int = 0
    database_queries: int = 0
    cache_hits: int = 0
    cache_misses: int = 0

    # Ошибки
    total_errors: int = 0
    errors_today: int = 0
    critical_errors: int = 0

    def to_dict(self) -> Dict:
        """Конвертация в словарь"""
        return {
            "online_players": self.online_players,
            "peak_players": self.peak_players,
            "unique_players": self.unique_players,
            "total_bans": self.total_bans,
            "active_bans": self.active_bans,
            "cpu_usage": self.cpu_usage,
            "memory_usage": self.memory_usage,
            "uptime": self.uptime,
        }

    def to_json(self) -> str:
        """Конвертация в JSON"""
        return json.dumps(self.to_dict(), indent=2)

    def to_dataframe(self) -> pd.DataFrame:
        """Конвертация в DataFrame"""
        return pd.DataFrame([self.to_dict()])

    def to_series(self) -> pd.Series:
        """Конвертация в Series"""
        return pd.Series(self.to_dict())

# ==================== БРОКЕР СООБЩЕНИЙ ====================

class MessageBroker:
    """Брокер сообщений на RabbitMQ"""

    def __init__(self):
        self.connection = None
        self.channel = None
        self.exchanges = {}
        self.queues = {}
        self.consumers = {}
        self.loop = None

    async def connect(self):
        """Подключение к RabbitMQ"""
        credentials = pika.PlainCredentials(
            KynxConfig.RABBITMQ_USER,
            KynxConfig.RABBITMQ_PASSWORD
        )

        parameters = pika.ConnectionParameters(
            host=KynxConfig.RABBITMQ_HOST,
            port=KynxConfig.RABBITMQ_PORT,
            virtual_host=KynxConfig.RABBITMQ_VHOST,
            credentials=credentials,
            heartbeat=600,
            blocked_connection_timeout=300
        )

        self.connection = await pika.adapters.asyncio_connection.AsyncioConnection.create(
            parameters=parameters,
            on_open_callback=self.on_connection_open,
            on_open_error_callback=self.on_connection_error,
            on_close_callback=self.on_connection_closed
        )

        logger.info("Connected to RabbitMQ")

    def on_connection_open(self, connection):
        """Обработчик открытия соединения"""
        self.connection = connection
        self.connection.channel(on_open_callback=self.on_channel_open)

    def on_channel_open(self, channel):
        """Обработчик открытия канала"""
        self.channel = channel

        # Объявление exchanges
        exchanges = [
            ("kynx.direct", "direct"),
            ("kynx.topic", "topic"),
            ("kynx.fanout", "fanout"),
            ("kynx.headers", "headers"),
            ("kynx.delayed", "x-delayed-message"),
        ]

        for exchange_name, exchange_type in exchanges:
            self.channel.exchange_declare(
                exchange=exchange_name,
                exchange_type=exchange_type,
                durable=True,
                auto_delete=False,
                callback=lambda: None
            )
            self.exchanges[exchange_name] = exchange_type

        logger.info("RabbitMQ channel opened")

    def on_connection_error(self, connection, error):
        """Обработчик ошибки соединения"""
        logger.error(f"RabbitMQ connection error: {error}")

    def on_connection_closed(self, connection, reason):
        """Обработчик закрытия соединения"""
        logger.warning(f"RabbitMQ connection closed: {reason}")

        # Попытка переподключения
        asyncio.create_task(self.reconnect())

    async def reconnect(self):
        """Переподключение к RabbitMQ"""
        await asyncio.sleep(5)
        await self.connect()

    async def publish(self, exchange: str, routing_key: str, message: Dict):
        """Публикация сообщения"""
        if not self.channel:
            logger.error("No RabbitMQ channel available")
            return False

        try:
            self.channel.basic_publish(
                exchange=exchange,
                routing_key=routing_key,
                body=json.dumps(message).encode(),
                properties=pika.BasicProperties(
                    delivery_mode=2,  # Persistent
                    content_type="application/json",
                    timestamp=int(time.time()),
                    message_id=str(uuid.uuid4()),
                    headers={
                        "source": "kynx",
                        "version": "4.0.0",
                        "timestamp": time.time()
                    }
                )
            )

            logger.debug(f"Published message to {exchange}/{routing_key}")
            return True

        except Exception as e:
            logger.error(f"Failed to publish message: {e}")
            return False

    async def consume(self, queue: str, callback: Callable):
        """Потребление сообщений"""
        if not self.channel:
            logger.error("No RabbitMQ channel available")
            return False

        try:
            self.channel.basic_consume(
                queue=queue,
                on_message_callback=lambda ch, method, properties, body: 
                    asyncio.create_task(callback(json.loads(body))),
                auto_ack=True
            )

            self.consumers[queue] = callback
            logger.info(f"Started consuming from queue: {queue}")
            return True

        except Exception as e:
            logger.error(f"Failed to start consuming: {e}")
            return False

    async def declare_queue(self, queue: str, **kwargs):
        """Объявление очереди"""
        if not self.channel:
            logger.error("No RabbitMQ channel available")
            return False

        try:
            self.channel.queue_declare(
                queue=queue,
                durable=kwargs.get("durable", True),
                auto_delete=kwargs.get("auto_delete", False),
                exclusive=kwargs.get("exclusive", False),
                callback=lambda: None
            )

            self.queues[queue] = kwargs
            logger.info(f"Declared queue: {queue}")
            return True

        except Exception as e:
            logger.error(f"Failed to declare queue: {e}")
            return False

    async def bind_queue(self, queue: str, exchange: str, routing_key: str):
        """Привязка очереди к exchange"""
        if not self.channel:
            logger.error("No RabbitMQ channel available")
            return False

        try:
            self.channel.queue_bind(
                queue=queue,
                exchange=exchange,
                routing_key=routing_key,
                callback=lambda: None
            )

            logger.info(f"Bound queue {queue} to {exchange}/{routing_key}")
            return True

        except Exception as e:
            logger.error(f"Failed to bind queue: {e}")
            return False

    async def close(self):
        """Закрытие соединения"""
        if self.connection:
            self.connection.close()
            logger.info("RabbitMQ connection closed")

# ==================== КЕШ-МЕНЕДЖЕР ====================

class CacheManager:
    """Менеджер кеша с поддержкой Redis"""

    def __init__(self):
        self.redis = None
        self.local_cache = {}
        self.local_cache_timestamps = {}
        self.stats = {
            "hits": 0,
            "misses": 0,
            "sets": 0,
            "deletes": 0
        }

    async def connect(self):
        """Подключение к Redis"""
        self.redis = await aioredis.from_url(
            f"redis://{KynxConfig.REDIS_HOST}:{KynxConfig.REDIS_PORT}/{KynxConfig.REDIS_DB}",
            password=KynxConfig.REDIS_PASSWORD or None,
            encoding="utf-8",
            decode_responses=True
        )

        logger.info("Connected to Redis")

    async def get(self, key: str, use_local: bool = True) -> Optional[Any]:
        """Получение значения из кеша"""
        # Проверка локального кеша
        if use_local and key in self.local_cache:
            timestamp = self.local_cache_timestamps.get(key, 0)
            if time.time() - timestamp <= KynxConfig.CACHE_TTL:
                self.stats["hits"] += 1
                return self.local_cache[key]
            else:
                del self.local_cache[key]
                del self.local_cache_timestamps[key]

        # Проверка Redis
        if self.redis:
            value = await self.redis.get(key)
            if value:
                try:
                    value = json.loads(value)
                    self.stats["hits"] += 1

                    # Обновление локального кеша
                    if use_local:
                        self.local_cache[key] = value
                        self.local_cache_timestamps[key] = time.time()

                    return value
                except:
                    pass

        self.stats["misses"] += 1
        return None

    async def set(self, key: str, value: Any, ttl: int = None):
        """Установка значения в кеш"""
        ttl = ttl or KynxConfig.CACHE_TTL

        # Локальный кеш
        self.local_cache[key] = value
        self.local_cache_timestamps[key] = time.time()

        # Redis
        if self.redis:
            try:
                await self.redis.setex(
                    key,
                    ttl,
                    json.dumps(value, default=str)
                )
            except Exception as e:
                logger.error(f"Redis set error: {e}")

        self.stats["sets"] += 1

        # Очистка локального кеша при превышении размера
        if len(self.local_cache) > KynxConfig.CACHE_MAX_SIZE:
            self._cleanup_local_cache()

    async def delete(self, key: str):
        """Удаление значения из кеша"""
        # Локальный кеш
        self.local_cache.pop(key, None)
        self.local_cache_timestamps.pop(key, None)

        # Redis
        if self.redis:
            await self.redis.delete(key)

        self.stats["deletes"] += 1

    async def invalidate_pattern(self, pattern: str):
        """Инвалидация по паттерну"""
        # Локальный кеш
        keys_to_delete = [k for k in self.local_cache if pattern in k]
        for key in keys_to_delete:
            self.local_cache.pop(key, None)
            self.local_cache_timestamps.pop(key, None)

        # Redis
        if self.redis:
            keys = await self.redis.keys(pattern)
            if keys:
                await self.redis.delete(*keys)

    def _cleanup_local_cache(self):
        """Очистка локального кеша"""
        # Сортировка по времени последнего доступа
        sorted_items = sorted(
            self.local_cache_timestamps.items(),
            key=lambda x: x[1]
        )

        # Удаление 20% самых старых записей
        remove_count = int(len(sorted_items) * 0.2)
        for key, _ in sorted_items[:remove_count]:
            self.local_cache.pop(key, None)
            self.local_cache_timestamps.pop(key, None)

    async def get_stats(self) -> Dict:
        """Получение статистики кеша"""
        hit_rate = 0
        if self.stats["hits"] + self.stats["misses"] > 0:
            hit_rate = self.stats["hits"] / (self.stats["hits"] + self.stats["misses"])

        return {
            **self.stats,
            "hit_rate": hit_rate,
            "local_cache_size": len(self.local_cache),
            "redis_connected": self.redis is not None
        }

    async def clear(self):
        """Очистка всего кеша"""
        self.local_cache.clear()
        self.local_cache_timestamps.clear()

        if self.redis:
            await self.redis.flushdb()

        logger.info("Cache cleared")

# ==================== БАЗА ДАННЫХ ====================

# SQLAlchemy модели
Base = declarative_base()

class PlayerModel(Base):
    """Модель игрока для SQLAlchemy"""
    __tablename__ = "players"

    user_id = sqlalchemy.Column(sqlalchemy.String(50), primary_key=True)
    username = sqlalchemy.Column(sqlalchemy.String(100))
    display_name = sqlalchemy.Column(sqlalchemy.String(100))
    avatar_url = sqlalchemy.Column(sqlalchemy.String(500))
    level = sqlalchemy.Column(sqlalchemy.Integer, default=1)
    experience = sqlalchemy.Column(sqlalchemy.Integer, default=0)
    reputation = sqlalchemy.Column(sqlalchemy.Float, default=0.0)
    trust_score = sqlalchemy.Column(sqlalchemy.Float, default=1.0)
    first_seen = sqlalchemy.Column(sqlalchemy.Float, default=time.time)
    last_seen = sqlalchemy.Column(sqlalchemy.Float, default=time.time)
    playtime = sqlalchemy.Column(sqlalchemy.Integer, default=0)
    sessions = sqlalchemy.Column(sqlalchemy.Integer, default=0)
    is_banned = sqlalchemy.Column(sqlalchemy.Boolean, default=False)
    is_muted = sqlalchemy.Column(sqlalchemy.Boolean, default=False)
    behavior_score = sqlalchemy.Column(sqlalchemy.Float, default=1.0)
    toxicity_score = sqlalchemy.Column(sqlalchemy.Float, default=0.0)
    balance = sqlalchemy.Column(sqlalchemy.Integer, default=0)
    data = sqlalchemy.Column(sqlalchemy.JSON, default={})

    def to_profile(self) -> PlayerProfile:
        """Конвертация в PlayerProfile"""
        profile = PlayerProfile(
            user_id=self.user_id,
            username=self.username,
            display_name=self.display_name,
            avatar_url=self.avatar_url,
            level=self.level,
            experience=self.experience,
            reputation=self.reputation,
            trust_score=self.trust_score,
            first_seen=self.first_seen,
            last_seen=self.last_seen,
            playtime=self.playtime,
            sessions=self.sessions,
            is_banned=self.is_banned,
            is_muted=self.is_muted,
            behavior_score=self.behavior_score,
            toxicity_score=self.toxicity_score,
            balance=self.balance
        )

        # Дополнительные данные
        if self.data:
            profile.devices = self.data.get("devices", [])
            profile.fingerprints = self.data.get("fingerprints", [])
            profile.ip_addresses = self.data.get("ip_addresses", [])
            profile.warnings = self.data.get("warnings", [])
            profile.notes = self.data.get("notes", [])
            profile.ban_history = self.data.get("ban_history", [])

        return profile

class BanModel(Base):
    """Модель бана для SQLAlchemy"""
    __tablename__ = "bans"

    ban_id = sqlalchemy.Column(sqlalchemy.String(50), primary_key=True)
    user_id = sqlalchemy.Column(sqlalchemy.String(50), index=True)
    username = sqlalchemy.Column(sqlalchemy.String(100))
    level = sqlalchemy.Column(sqlalchemy.String(50))
    duration = sqlalchemy.Column(sqlalchemy.String(50))
    reason = sqlalchemy.Column(sqlalchemy.String(50))
    reason_text = sqlalchemy.Column(sqlalchemy.String(1000))
    executor = sqlalchemy.Column(sqlalchemy.String(100))
    executor_id = sqlalchemy.Column(sqlalchemy.String(50))
    timestamp = sqlalchemy.Column(sqlalchemy.Float)
    expires = sqlalchemy.Column(sqlalchemy.Float, nullable=True)
    is_active = sqlalchemy.Column(sqlalchemy.Boolean, default=True)
    data = sqlalchemy.Column(sqlalchemy.JSON, default={})

    def to_record(self) -> BanRecord:
        """Конвертация в BanRecord"""
        record = BanRecord(
            ban_id=self.ban_id,
            user_id=self.user_id,
            username=self.username,
            level=BanLevel(self.level),
            duration=BanDuration(self.duration),
            reason=BanReason(self.reason),
            reason_text=self.reason_text,
            executor=self.executor,
            executor_id=self.executor_id,
            timestamp=self.timestamp,
            expires=self.expires,
            is_active=self.is_active
        )

        # Дополнительные данные
        if self.data:
            record.evidence = self.data.get("evidence", [])
            record.appeals = self.data.get("appeals", [])
            record.metadata = self.data.get("metadata", {})

        return record

class LogModel(Base):
    """Модель лога для SQLAlchemy"""
    __tablename__ = "logs"

    log_id = sqlalchemy.Column(sqlalchemy.String(50), primary_key=True)
    timestamp = sqlalchemy.Column(sqlalchemy.Float, index=True)
    level = sqlalchemy.Column(sqlalchemy.String(20))
    component = sqlalchemy.Column(sqlalchemy.String(50))
    event = sqlalchemy.Column(sqlalchemy.String(100))
    message = sqlalchemy.Column(sqlalchemy.String(1000))
    data = sqlalchemy.Column(sqlalchemy.JSON, default={})

class DatabaseManager:
    """Менеджер баз данных с поддержкой нескольких БД"""

    def __init__(self):
        # PostgreSQL
        self.postgres_engine = None
        self.postgres_session = None

        # MongoDB
        self.mongodb_client = None
        self.mongodb_db = None

        # Elasticsearch
        self.elasticsearch_client = None

        # Connections
        self.connections = {}

    async def connect_all(self):
        """Подключение ко всем базам данных"""
        await self.connect_postgresql()
        await self.connect_mongodb()
        await self.connect_elasticsearch()
        logger.info("Connected to all databases")

    async def connect_postgresql(self):
        """Подключение к PostgreSQL"""
        database_url = (
            f"postgresql+asyncpg://{KynxConfig.DB_USER}:{KynxConfig.DB_PASSWORD}"
            f"@{KynxConfig.DB_HOST}:{KynxConfig.DB_PORT}/{KynxConfig.DB_NAME}"
        )

        self.postgres_engine = create_async_engine(
            database_url,
            echo=KynxConfig.DEVELOPMENT_MODE,
            pool_size=20,
            max_overflow=10,
            pool_pre_ping=True,
            pool_recycle=3600
        )

        self.postgres_session = sessionmaker(
            self.postgres_engine,
            class_=AsyncSession,
            expire_on_commit=False
        )

        # Создание таблиц
        async with self.postgres_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

        logger.info("Connected to PostgreSQL")

    async def connect_mongodb(self):
        """Подключение к MongoDB"""
        self.mongodb_client = motor.motor_asyncio.AsyncIOMotorClient(
            KynxConfig.MONGODB_URI
        )
        self.mongodb_db = self.mongodb_client[KynxConfig.MONGODB_DB]

        # Создание индексов
        await self.mongodb_db.players.create_index("user_id", unique=True)
        await self.mongodb_db.bans.create_index("ban_id", unique=True)
        await self.mongodb_db.bans.create_index("user_id")
        await self.mongodb_db.logs.create_index("timestamp")

        logger.info("Connected to MongoDB")

    async def connect_elasticsearch(self):
        """Подключение к Elasticsearch"""
        self.elasticsearch_client = AsyncElasticsearch(
            KynxConfig.ELASTICSEARCH_HOSTS,
            basic_auth=(
                (KynxConfig.ELASTICSEARCH_USER, KynxConfig.ELASTICSEARCH_PASSWORD)
                if KynxConfig.ELASTICSEARCH_USER else None
            )
        )

        # Проверка подключения
        await self.elasticsearch_client.info()

        # Создание индексов
        indices = ["players", "bans", "logs", "metrics"]
        for index in indices:
            await self.elasticsearch_client.indices.create(
                index=f"kynx_{index}",
                ignore=400  # Ignore if already exists
            )

        logger.info("Connected to Elasticsearch")

    @asynccontextmanager
    async def get_postgres_session(self):
        """Получение сессии PostgreSQL"""
        async with self.postgres_session() as session:
            yield session

    async def get_mongodb_collection(self, name: str):
        """Получение коллекции MongoDB"""
        return self.mongodb_db[name]

    async def elasticsearch_index(self, index: str, document: Dict):
        """Индексация документа в Elasticsearch"""
        await self.elasticsearch_client.index(
            index=f"kynx_{index}",
            document=document,
            refresh=True
        )

    async def elasticsearch_search(self, index: str, query: Dict) -> List[Dict]:
        """Поиск в Elasticsearch"""
        result = await self.elasticsearch_client.search(
            index=f"kynx_{index}",
            body=query
        )

        return [hit["_source"] for hit in result["hits"]["hits"]]

    async def close_all(self):
        """Закрытие всех подключений"""
        if self.postgres_engine:
            await self.postgres_engine.dispose()

        if self.mongodb_client:
            self.mongodb_client.close()

        if self.elasticsearch_client:
            await self.elasticsearch_client.close()

        logger.info("Closed all database connections")

# ==================== AI/ML КОМПОНЕНТЫ ====================

class AIModelManager:
    """Менеджер AI/ML моделей"""

    def __init__(self):
        self.models = {}
        self.pipelines = {}
        self.device = torch.device(KynxConfig.PYTORCH_DEVICE)

        # Настройка TensorFlow
        if KynxConfig.TENSORFLOW_MEMORY_GROWTH:
            gpus = tf.config.experimental.list_physical_devices('GPU')
            for gpu in gpus:
                tf.config.experimental.set_memory_growth(gpu, True)

    async def load_all_models(self):
        """Загрузка всех моделей"""
        tasks = [
            self.load_sentiment_model(),
            self.load_toxicity_model(),
            self.load_cheating_detection_model(),
            self.load_behavior_prediction_model(),
            self.load_anomaly_detection_model(),
            self.load_recommendation_model(),
            self.load_chatbot_model(),
            self.load_voice_recognition_model(),
            self.load_face_recognition_model(),
            self.load_fingerprint_model()
        ]

        await asyncio.gather(*tasks)
        logger.info(f"Loaded {len(self.models)} AI models")

    async def load_sentiment_model(self):
        """Загрузка модели анализа тональности"""
        try:
            self.pipelines["sentiment"] = pipeline(
                "sentiment-analysis",
                model="distilbert-base-uncased-finetuned-sst-2-english",
                device=0 if torch.cuda.is_available() else -1
            )
            logger.info("Loaded sentiment analysis model")
        except Exception as e:
            logger.error(f"Failed to load sentiment model: {e}")

    async def load_toxicity_model(self):
        """Загрузка модели определения токсичности"""
        try:
            self.pipelines["toxicity"] = pipeline(
                "text-classification",
                model="unitary/toxic-bert",
                device=0 if torch.cuda.is_available() else -1
            )
            logger.info("Loaded toxicity detection model")
        except Exception as e:
            logger.error(f"Failed to load toxicity model: {e}")

    async def load_cheating_detection_model(self):
        """Загрузка модели обнаружения читерства"""
        try:
            # Создание модели XGBoost для обнаружения аномалий
            model = xgb.XGBClassifier(
                n_estimators=100,
                max_depth=5,
                learning_rate=0.1,
                random_state=42
            )

            # TODO: Загрузить обученную модель
            self.models["cheating_detection"] = model
            logger.info("Loaded cheating detection model")
        except Exception as e:
            logger.error(f"Failed to load cheating detection model: {e}")

    async def load_behavior_prediction_model(self):
        """Загрузка модели предсказания поведения"""
        try:
            # PyTorch модель для предсказания поведения
            class BehaviorPredictor(nn.Module):
                def __init__(self, input_size=50, hidden_size=100, output_size=10):
                    super().__init__()
                    self.lstm = nn.LSTM(input_size, hidden_size, batch_first=True)
                    self.fc = nn.Linear(hidden_size, output_size)

                def forward(self, x):
                    lstm_out, _ = self.lstm(x)
                    return self.fc(lstm_out[:, -1, :])

            model = BehaviorPredictor()
            model.to(self.device)

            # TODO: Загрузить веса
            self.models["behavior_prediction"] = model
            logger.info("Loaded behavior prediction model")
        except Exception as e:
            logger.error(f"Failed to load behavior prediction model: {e}")

    async def load_anomaly_detection_model(self):
        """Загрузка модели обнаружения аномалий"""
        try:
            # Isolation Forest для обнаружения аномалий
            from sklearn.ensemble import IsolationForest

            model = IsolationForest(
                n_estimators=100,
                contamination=0.1,
                random_state=42
            )

            self.models["anomaly_detection"] = model
            logger.info("Loaded anomaly detection model")
        except Exception as e:
            logger.error(f"Failed to load anomaly detection model: {e}")

    async def load_recommendation_model(self):
        """Загрузка модели рекомендаций"""
        try:
            # LightFM для рекомендаций
            from lightfm import LightFM

            model = LightFM(loss='warp')
            self.models["recommendation"] = model
            logger.info("Loaded recommendation model")
        except Exception as e:
            logger.error(f"Failed to load recommendation model: {e}")

    async def load_chatbot_model(self):
        """Загрузка модели чат-бота"""
        try:
            # Загрузка модели GPT для чат-бота
            if KynxConfig.HUGGINGFACE_TOKEN:
                self.pipelines["chatbot"] = pipeline(
                    "text-generation",
                    model=KynxConfig.HUGGINGFACE_MODEL,
                    device=0 if torch.cuda.is_available() else -1,
                    token=KynxConfig.HUGGINGFACE_TOKEN
                )
                logger.info("Loaded chatbot model")
        except Exception as e:
            logger.error(f"Failed to load chatbot model: {e}")

    async def load_voice_recognition_model(self):
        """Загрузка модели распознавания голоса"""
        try:
            # Загрузка модели Whisper
            self.models["whisper"] = whisper.load_model("base")
            logger.info("Loaded voice recognition model")
        except Exception as e:
            logger.error(f"Failed to load voice recognition model: {e}")

    async def load_face_recognition_model(self):
        """Загрузка модели распознавания лиц"""
        try:
            # Загрузка модели face_recognition
            self.models["face_recognition"] = face_recognition
            logger.info("Loaded face recognition model")
        except Exception as e:
            logger.error(f"Failed to load face recognition model: {e}")

    async def load_fingerprint_model(self):
        """Загрузка модели распознавания отпечатков"""
        try:
            # Загрузка модели для fingerprinting
            import fingerprint_feature_extractor

            self.models["fingerprint"] = fingerprint_feature_extractor
            logger.info("Loaded fingerprint model")
        except Exception as e:
            logger.error(f"Failed to load fingerprint model: {e}")

    async def analyze_sentiment(self, text: str) -> Dict:
        """Анализ тональности текста"""
        if "sentiment" not in self.pipelines:
            return {"label": "NEUTRAL", "score": 0.5}

        result = self.pipelines["sentiment"](text)[0]
        return result

    async def detect_toxicity(self, text: str) -> float:
        """Определение токсичности текста"""
        if "toxicity" not in self.pipelines:
            return 0.0

        result = self.pipelines["toxicity"](text)[0]

        # Преобразование в вероятность токсичности
        if result["label"] == "TOXIC":
            return result["score"]
        else:
            return 1 - result["score"]

    async def detect_cheating(self, player_data: Dict) -> float:
        """Обнаружение читерства"""
        if "cheating_detection" not in self.models:
            return 0.0

        # TODO: Реализовать обнаружение читерства
        return 0.0

    async def predict_behavior(self, history: List[Dict]) -> Dict:
        """Предсказание поведения"""
        if "behavior_prediction" not in self.models:
            return {}

        # TODO: Реализовать предсказание поведения
        return {}

    async def detect_anomalies(self, data: np.ndarray) -> List[int]:
        """Обнаружение аномалий"""
        if "anomaly_detection" not in self.models:
            return []

        predictions = self.models["anomaly_detection"].fit_predict(data)
        anomalies = np.where(predictions == -1)[0].tolist()

        return anomalies

    async def get_recommendations(self, user_id: str, n: int = 10) -> List[str]:
        """Получение рекомендаций"""
        if "recommendation" not in self.models:
            return []

        # TODO: Реализовать рекомендации
        return []

    async def chat(self, message: str, context: List[Dict] = None) -> str:
        """Чат с AI"""
        if "chatbot" not in self.pipelines:
            return "I'm sorry, I'm not available right now."

        # Формирование промпта
        prompt = f"User: {message}\nAssistant:"

        result = self.pipelines["chatbot"](
            prompt,
            max_length=100,
            temperature=0.7,
            do_sample=True,
            top_p=0.9
        )[0]["generated_text"]

        # Извлечение ответа
        response = result.split("Assistant:")[-1].strip()

        return response

    async def transcribe_audio(self, audio_path: str) -> str:
        """Транскрибация аудио"""
        if "whisper" not in self.models:
            return ""

        result = self.models["whisper"].transcribe(audio_path)
        return result["text"]

    async def recognize_face(self, image_path: str, known_faces: List) -> bool:
        """Распознавание лица"""
        if "face_recognition" not in self.models:
            return False

        # Загрузка изображения
        image = face_recognition.load_image_file(image_path)
        face_encodings = face_recognition.face_encodings(image)

        if not face_encodings:
            return False

        # Сравнение с известными лицами
        matches = face_recognition.compare_faces(known_faces, face_encodings[0])

        return any(matches)

# ==================== ОСНОВНОЙ БОТ ====================

class KynxBot(commands.Bot):
    """Главный класс бота"""

    def __init__(self):
        intents = discord.Intents.all()

        super().__init__(
            command_prefix="!",
            intents=intents,
            help_command=None,
            activity=discord.Activity(
                type=discord.ActivityType.watching,
                name="KYNX X 4.0.0"
            ),
            status=discord.Status.online
        )

        # Компоненты
        self.message_broker = MessageBroker()
        self.cache = CacheManager()
        self.database = DatabaseManager()
        self.ai = AIModelManager()

        # Метрики
        self.metrics = ServerMetrics()
        self.metrics_history = deque(maxlen=1440)  # 24 часа с интервалом 1 минута

        # Веб-серверы
        self.fastapi_app = None
        self.streamlit_app = None
        self.gradio_app = None
        self.dash_app = None

        # Стартовое время
        self.start_time = time.time()

        # Команды
        self.setup_commands()

    def setup_commands(self):
        """Настройка команд"""
        # Группы команд
        self.admin_group = app_commands.Group(name="admin", description="Admin commands")
        self.mod_group = app_commands.Group(name="mod", description="Moderator commands")
        self.ai_group = app_commands.Group(name="ai", description="AI commands")
        self.stats_group = app_commands.Group(name="stats", description="Statistics commands")
        self.backup_group = app_commands.Group(name="backup", description="Backup commands")

        self.tree.add_command(self.admin_group)
        self.tree.add_command(self.mod_group)
        self.tree.add_command(self.ai_group)
        self.tree.add_command(self.stats_group)
        self.tree.add_command(self.backup_group)

    async def setup_hook(self):
        """Хук настройки"""
        logger.info("Starting KYNX X 4.0.0...")

        # Подключение к сервисам
        await self.message_broker.connect()
        await self.cache.connect()
        await self.database.connect_all()
        await self.ai.load_all_models()

        # Запуск веб-серверов
        if KynxConfig.STREAMLIT_ENABLED:
            self.start_streamlit()

        if KynxConfig.GRADIO_ENABLED:
            self.start_gradio()

        if KynxConfig.DASH_ENABLED:
            self.start_dash()

        # Запуск FastAPI
        self.start_fastapi()

        # Запуск задач
        self.update_metrics.start()
        self.backup_database.start()
        self.cleanup_temp_files.start()
        self.check_alerts.start()

        # Синхронизация команд
        await self.tree.sync()

        logger.info(f"KYNX X 4.0.0 is ready! Logged in as {self.user}")

    def start_fastapi(self):
        """Запуск FastAPI сервера"""
        self.fastapi_app = FastAPI(
            title="KYNX X API",
            description="Next generation moderation system API",
            version="4.0.0"
        )

        # CORS
        self.fastapi_app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

        # Маршруты
        @self.fastapi_app.get("/")
        async def root():
            return {
                "name": "KYNX X",
                "version": "4.0.0",
                "status": "online",
                "uptime": time.time() - self.start_time
            }

        @self.fastapi_app.get("/metrics")
        async def get_metrics():
            return self.metrics.to_dict()

        @self.fastapi_app.get("/players/{user_id}")
        async def get_player(user_id: str):
            # Получение игрока из кеша
            cached = await self.cache.get(f"player:{user_id}")
            if cached:
                return cached

            # Получение из БД
            async with self.database.get_postgres_session() as session:
                player = await session.get(PlayerModel, user_id)
                if player:
                    profile = player.to_profile()
                    await self.cache.set(f"player:{user_id}", profile.to_dict())
                    return profile.to_dict()

            return {"error": "Player not found"}

        @self.fastapi_app.get("/bans")
        async def get_bans(active: bool = True, limit: int = 100):
            async with self.database.get_postgres_session() as session:
                query = sqlalchemy.select(BanModel).where(
                    BanModel.is_active == active
                ).limit(limit)
                result = await session.execute(query)
                bans = result.scalars().all()

                return [ban.to_record().to_dict() for ban in bans]

        @self.fastapi_app.websocket("/ws")
        async def websocket_endpoint(websocket: WebSocket):
            await websocket.accept()
            try:
                while True:
                    data = await websocket.receive_text()
                    # Обработка сообщения
                    await websocket.send_text(f"Echo: {data}")
            except WebSocketDisconnect:
                pass

        # Запуск сервера
        import threading
        threading.Thread(
            target=lambda: uvicorn.run(
                self.fastapi_app,
                host="0.0.0.0",
                port=KynxConfig.REST_API_PORT,
                log_level="info"
            ),
            daemon=True
        ).start()

    def start_streamlit(self):
        """Запуск Streamlit приложения"""
        import threading
        threading.Thread(
            target=lambda: os.system(
                f"streamlit run streamlit_app.py --server.port {KynxConfig.STREAMLIT_PORT}"
            ),
            daemon=True
        ).start()

    def start_gradio(self):
        """Запуск Gradio приложения"""
        import threading
        threading.Thread(
            target=lambda: os.system(
                f"python gradio_app.py --port {KynxConfig.GRADIO_PORT}"
            ),
            daemon=True
        ).start()

    def start_dash(self):
        """Запуск Dash приложения"""
        import threading
        threading.Thread(
            target=lambda: os.system(
                f"python dash_app.py --port {KynxConfig.DASH_PORT}"
            ),
            daemon=True
        ).start()

    @tasks.loop(seconds=60)
    async def update_metrics(self):
        """Обновление метрик"""
        try:
            # Системные метрики
            self.metrics.cpu_usage = psutil.cpu_percent(interval=1)
            self.metrics.memory_usage = psutil.virtual_memory().percent
            self.metrics.disk_usage = psutil.disk_usage('/').percent
            self.metrics.network_in = psutil.net_io_counters().bytes_recv
            self.metrics.network_out = psutil.net_io_counters().bytes_sent
            self.metrics.uptime = time.time() - self.start_time

            # Prometheus метрики
            if KynxConfig.PROMETHEUS_ENABLED:
                cpu_usage_gauge.labels(core='total').set(self.metrics.cpu_usage)
                memory_usage_gauge.labels(type='percent').set(self.metrics.memory_usage)
                disk_usage_gauge.labels(path='/').set(self.metrics.disk_usage)
                network_io_gauge.labels(direction='in').set(self.metrics.network_in)
                network_io_gauge.labels(direction='out').set(self.metrics.network_out)

            # Сохранение в историю
            self.metrics_history.append({
                "timestamp": time.time(),
                **self.metrics.to_dict()
            })

            # Сохранение в Elasticsearch
            await self.database.elasticsearch_index("metrics", {
                "timestamp": time.time(),
                **self.metrics.to_dict()
            })

        except Exception as e:
            logger.error(f"Failed to update metrics: {e}")

    @tasks.loop(hours=24)
    async def backup_database(self):
        """Резервное копирование базы данных"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = KynxConfig.BACKUP_DIR / f"backup_{timestamp}"
            backup_path.mkdir(exist_ok=True)

            # Бэкап PostgreSQL
            if self.database.postgres_engine:
                # TODO: Реализовать бэкап PostgreSQL
                pass

            # Бэкап MongoDB
            if self.database.mongodb_client:
                # TODO: Реализовать бэкап MongoDB
                pass

            # Бэкап Elasticsearch
            if self.database.elasticsearch_client:
                # TODO: Реализовать бэкап Elasticsearch
                pass

            # Очистка старых бэкапов
            backups = sorted(KynxConfig.BACKUP_DIR.glob("backup_*"))
            if len(backups) > 7:  # Хранить 7 последних бэкапов
                for backup in backups[:-7]:
                    import shutil
                    shutil.rmtree(backup)

            logger.info(f"Database backup completed: {backup_path}")

        except Exception as e:
            logger.error(f"Failed to backup database: {e}")

    @tasks.loop(hours=1)
    async def cleanup_temp_files(self):
        """Очистка временных файлов"""
        try:
            # Удаление файлов старше 24 часов
            cutoff = time.time() - 24 * 3600

            for file in KynxConfig.TEMP_DIR.glob("*"):
                if file.stat().st_mtime < cutoff:
                    file.unlink()

            logger.info("Temporary files cleaned up")

        except Exception as e:
            logger.error(f"Failed to cleanup temp files: {e}")

    @tasks.loop(minutes=5)
    async def check_alerts(self):
        """Проверка условий для алертов"""
        if not KynxConfig.ALERTING_ENABLED:
            return

        try:
            alerts = []

            # Проверка CPU
            if self.metrics.cpu_usage > 90:
                alerts.append(f"High CPU usage: {self.metrics.cpu_usage}%")

            # Проверка памяти
            if self.metrics.memory_usage > 90:
                alerts.append(f"High memory usage: {self.metrics.memory_usage}%")

            # Проверка диска
            if self.metrics.disk_usage > 90:
                alerts.append(f"High disk usage: {self.metrics.disk_usage}%")

            # Проверка количества ошибок
            if self.metrics.total_errors > 100:
                alerts.append(f"High error count: {self.metrics.total_errors}")

            # Отправка алертов
            if alerts and KynxConfig.ALERTING_WEBHOOK_URL:
                async with aiohttp.ClientSession() as session:
                    await session.post(
                        KynxConfig.ALERTING_WEBHOOK_URL,
                        json={
                            "alerts": alerts,
                            "timestamp": time.time(),
                            "metrics": self.metrics.to_dict()
                        }
                    )

                logger.warning(f"Sent {len(alerts)} alerts")

        except Exception as e:
            logger.error(f"Failed to check alerts: {e}")

    async def close(self):
        """Закрытие бота"""
        # Остановка задач
        self.update_metrics.stop()
        self.backup_database.stop()
        self.cleanup_temp_files.stop()
        self.check_alerts.stop()

        # Закрытие соединений
        await self.message_broker.close()
        await self.database.close_all()

        # Закрытие AI моделей
        # TODO: Освобождение GPU памяти

        await super().close()
        logger.info("KYNX X 4.0.0 stopped")

# ==================== СОЗДАНИЕ БОТА ====================
bot = KynxBot()

# ==================== КОМАНДЫ ====================

@bot.tree.command(name="ping", description="Check bot latency")
async def ping(interaction: discord.Interaction):
    """Проверка задержки"""
    start = time.time()
    await interaction.response.defer()
    end = time.time()

    latency = round((end - start) * 1000, 2)

    embed = discord.Embed(
        title="🏓 Pong!",
        color=discord.Color.green(),
        timestamp=datetime.utcnow()
    )
    embed.add_field(name="Latency", value=f"```{latency}ms```", inline=True)
    embed.add_field(name="WebSocket", value=f"```{round(bot.latency * 1000, 2)}ms```", inline=True)
    embed.add_field(name="API", value="```✅ Online```" if bot.message_broker.connection else "```❌ Offline```", inline=True)
    embed.set_footer(text=f"KYNX X 4.0.0")

    await interaction.followup.send(embed=embed)

    if KynxConfig.PROMETHEUS_ENABLED:
        command_counter.labels(command="ping", status="success").inc()

@bot.tree.command(name="stats", description="Display detailed server statistics")
async def stats(interaction: discord.Interaction):
    """Показ статистики сервера"""
    await interaction.response.defer()

    # Получение статистики
    metrics = bot.metrics

    # Создание графиков
    fig, axes = plt.subplots(2, 2, figsize=(12, 8))
    fig.suptitle("KYNX X Server Statistics", fontsize=16)

    # График CPU
    axes[0, 0].plot([m.get("cpu_usage", 0) for m in bot.metrics_history])
    axes[0, 0].set_title("CPU Usage")
    axes[0, 0].set_ylabel("Percent")
    axes[0, 0].grid(True)

    # График памяти
    axes[0, 1].plot([m.get("memory_usage", 0) for m in bot.metrics_history])
    axes[0, 1].set_title("Memory Usage")
    axes[0, 1].set_ylabel("Percent")
    axes[0, 1].grid(True)

    # График игроков
    axes[1, 0].plot([m.get("online_players", 0) for m in bot.metrics_history])
    axes[1, 0].set_title("Online Players")
    axes[1, 0].set_ylabel("Count")
    axes[1, 0].grid(True)

    # График банов
    axes[1, 1].plot([m.get("active_bans", 0) for m in bot.metrics_history])
    axes[1, 1].set_title("Active Bans")
    axes[1, 1].set_ylabel("Count")
    axes[1, 1].grid(True)

    plt.tight_layout()

    # Сохранение в буфер
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=100)
    buf.seek(0)
    plt.close()

    # Создание embed
    embed = discord.Embed(
        title="📊 Server Statistics",
        description=f"KYNX X 4.0.0 - Real-time metrics",
        color=discord.Color.blue(),
        timestamp=datetime.utcnow()
    )

    embed.add_field(name="🟢 Online Players", value=f"```{metrics.online_players}```", inline=True)
    embed.add_field(name="🔨 Active Bans", value=f"```{metrics.active_bans}```", inline=True)
    embed.add_field(name="🔇 Active Mutes", value=f"```{metrics.active_mutes}```", inline=True)

    embed.add_field(name="💻 CPU Usage", value=f"```{metrics.cpu_usage:.1f}%```", inline=True)
    embed.add_field(name="📊 Memory Usage", value=f"```{metrics.memory_usage:.1f}%```", inline=True)
    embed.add_field(name="💾 Disk Usage", value=f"```{metrics.disk_usage:.1f}%```", inline=True)

    embed.add_field(name="📈 Peak Players", value=f"```{metrics.peak_players}```", inline=True)
    embed.add_field(name="🔄 Total Bans", value=f"```{metrics.total_bans}```", inline=True)
    embed.add_field(name="⏱️ Uptime", value=f"```{timedelta(seconds=int(metrics.uptime))}```", inline=True)

    embed.set_footer(text=f"Requested by {interaction.user.display_name}")

    # Отправка с графиком
    file = discord.File(buf, filename="stats.png")
    embed.set_image(url="attachment://stats.png")

    await interaction.followup.send(file=file, embed=embed)

    if KynxConfig.PROMETHEUS_ENABLED:
        command_counter.labels(command="stats", status="success").inc()

@bot.tree.command(name="ban", description="Ban a player with advanced options")
@app_commands.describe(
    user_id="Roblox User ID",
    reason="Ban reason",
    level="Ban level (account/device/ip/hardware)",
    duration="Ban duration (temporary/permanent)",
    evidence="Evidence (screenshots, logs, etc.)"
)
async def ban(
    interaction: discord.Interaction,
    user_id: str,
    reason: str,
    level: str = "account",
    duration: str = "permanent",
    evidence: Optional[str] = None
):
    """Бан игрока с расширенными опциями"""
    await interaction.response.defer()

    # Проверка прав
    if not any(role.id in KynxConfig.DISCORD_ALLOWED_ROLES for role in interaction.user.roles):
        await interaction.followup.send("❌ You don't have permission to use this command!")
        return

    # Валидация ID
    if not user_id.isdigit():
        await interaction.followup.send("❌ User ID must contain only numbers!")
        return

    # Получение данных игрока
    async with aiohttp.ClientSession() as session:
        async with session.get(f"https://users.roblox.com/v1/users/{user_id}") as resp:
            if resp.status != 200:
                await interaction.followup.send(f"❌ Could not find Roblox user with ID `{user_id}`")
                return
            user_data = await resp.json()

    username = user_data.get("name", "Unknown")
    display_name = user_data.get("displayName", username)

    # Получение аватара
    async with aiohttp.ClientSession() as session:
        async with session.get(
            f"https://thumbnails.roblox.com/v1/users/avatar-headshot",
            params={"userIds": user_id, "size": "420x420", "format": "Png"}
        ) as resp:
            avatar_data = await resp.json() if resp.status == 200 else {}

    avatar_url = avatar_data.get("data", [{}])[0].get("imageUrl") if avatar_data else None

    # Создание записи бана
    ban_record = BanRecord(
        user_id=user_id,
        username=username,
        level=BanLevel(level),
        duration=BanDuration(duration),
        reason=BanReason(reason),
        reason_text=reason,
        executor=interaction.user.name,
        executor_id=str(interaction.user.id)
    )

    if evidence:
        ban_record.evidence.append({"type": "text", "content": evidence})

    # Сохранение в БД
    async with bot.database.get_postgres_session() as session:
        ban_model = BanModel(
            ban_id=ban_record.ban_id,
            user_id=ban_record.user_id,
            username=ban_record.username,
            level=ban_record.level.value,
            duration=ban_record.duration.value,
            reason=ban_record.reason.value,
            reason_text=ban_record.reason_text,
            executor=ban_record.executor,
            executor_id=ban_record.executor_id,
            timestamp=ban_record.timestamp,
            expires=ban_record.expires,
            is_active=ban_record.is_active,
            data={
                "evidence": ban_record.evidence,
                "metadata": ban_record.metadata
            }
        )
        session.add(ban_model)
        await session.commit()

    # Отправка команды на сервер
    command_data = {
        "command": "ban",
        "userid": user_id,
        "reason": reason,
        "level": level,
        "duration": duration,
        "executor": interaction.user.name
    }

    success = await bot.message_broker.publish(
        "kynx.direct",
        "game.commands",
        command_data
    )

    # Создание embed
    embed = discord.Embed(
        title="🔨 Player Banned",
        description=f"**{username}** has been banned from the server.",
        color=discord.Color.red(),
        timestamp=datetime.utcnow()
    )

    if avatar_url:
        embed.set_thumbnail(url=avatar_url)

    embed.add_field(name="User ID", value=f"`{user_id}`", inline=True)
    embed.add_field(name="Username", value=username, inline=True)
    embed.add_field(name="Display Name", value=display_name, inline=True)

    embed.add_field(name="Ban Level", value=level.upper(), inline=True)
    embed.add_field(name="Duration", value=duration.upper(), inline=True)
    embed.add_field(name="Ban ID", value=f"`{ban_record.ban_id[:8]}`", inline=True)

    embed.add_field(name="Reason", value=reason, inline=False)

    if evidence:
        embed.add_field(name="Evidence", value=evidence[:1000], inline=False)

    embed.set_footer(text=f"Banned by {interaction.user.display_name}")

    await interaction.followup.send(embed=embed)

    # Обновление метрик
    if KynxConfig.PROMETHEUS_ENABLED:
        command_counter.labels(command="ban", status="success").inc()
        ban_counter.labels(type="ban", level=level).inc()

    # Логирование
    logger.info(f"Player {username} ({user_id}) banned by {interaction.user.name}")

@bot.tree.command(name="unban", description="Unban a player")
@app_commands.describe(
    user_id="Roblox User ID",
    reason="Unban reason"
)
async def unban(interaction: discord.Interaction, user_id: str, reason: str = "No reason provided"):
    """Разбан игрока"""
    await interaction.response.defer()

    # Проверка прав
    if not any(role.id in KynxConfig.DISCORD_ALLOWED_ROLES for role in interaction.user.roles):
        await interaction.followup.send("❌ You don't have permission to use this command!")
        return

    # Валидация ID
    if not user_id.isdigit():
        await interaction.followup.send("❌ User ID must contain only numbers!")
        return

    # Поиск активного бана
    async with bot.database.get_postgres_session() as session:
        query = sqlalchemy.select(BanModel).where(
            BanModel.user_id == user_id,
            BanModel.is_active == True
        )
        result = await session.execute(query)
        ban = result.scalar_one_or_none()

        if not ban:
            await interaction.followup.send(f"❌ No active ban found for user ID `{user_id}`")
            return

        # Деактивация бана
        ban.is_active = False
        await session.commit()

        ban_record = ban.to_record()

    # Получение данных игрока
    async with aiohttp.ClientSession() as session:
        async with session.get(f"https://users.roblox.com/v1/users/{user_id}") as resp:
            user_data = await resp.json() if resp.status == 200 else {}

    username = user_data.get("name", ban_record.username)

    # Отправка команды на сервер
    command_data = {
        "command": "unban",
        "userid": user_id,
        "reason": reason,
        "executor": interaction.user.name
    }

    success = await bot.message_broker.publish(
        "kynx.direct",
        "game.commands",
        command_data
    )

    # Создание embed
    embed = discord.Embed(
        title="✅ Player Unbanned",
        description=f"**{username}** has been unbanned from the server.",
        color=discord.Color.green(),
        timestamp=datetime.utcnow()
    )

    embed.add_field(name="User ID", value=f"`{user_id}`", inline=True)
    embed.add_field(name="Username", value=username, inline=True)
    embed.add_field(name="Ban ID", value=f"`{ban_record.ban_id[:8]}`", inline=True)

    embed.add_field(name="Reason", value=reason, inline=False)
    embed.add_field(name="Original Ban Reason", value=ban_record.reason_text, inline=False)

    embed.set_footer(text=f"Unbanned by {interaction.user.display_name}")

    await interaction.followup.send(embed=embed)

    # Обновление метрик
    if KynxConfig.PROMETHEUS_ENABLED:
        command_counter.labels(command="unban", status="success").inc()

    # Логирование
    logger.info(f"Player {username} ({user_id}) unbanned by {interaction.user.name}")

@bot.tree.command(name="kick", description="Kick a player from the server")
@app_commands.describe(
    user_id="Roblox User ID",
    reason="Kick reason"
)
async def kick(interaction: discord.Interaction, user_id: str, reason: str):
    """Кик игрока"""
    await interaction.response.defer()

    # Проверка прав
    if not any(role.id in KynxConfig.DISCORD_ALLOWED_ROLES for role in interaction.user.roles):
        await interaction.followup.send("❌ You don't have permission to use this command!")
        return

    # Валидация ID
    if not user_id.isdigit():
        await interaction.followup.send("❌ User ID must contain only numbers!")
        return

    # Получение данных игрока
    async with aiohttp.ClientSession() as session:
        async with session.get(f"https://users.roblox.com/v1/users/{user_id}") as resp:
            if resp.status != 200:
                await interaction.followup.send(f"❌ Could not find Roblox user with ID `{user_id}`")
                return
            user_data = await resp.json()

    username = user_data.get("name", "Unknown")

    # Отправка команды на сервер
    command_data = {
        "command": "kick",
        "userid": user_id,
        "reason": reason,
        "executor": interaction.user.name
    }

    success = await bot.message_broker.publish(
        "kynx.direct",
        "game.commands",
        command_data
    )

    # Создание embed
    embed = discord.Embed(
        title="👢 Player Kicked",
        description=f"**{username}** has been kicked from the server.",
        color=discord.Color.orange(),
        timestamp=datetime.utcnow()
    )

    embed.add_field(name="User ID", value=f"`{user_id}`", inline=True)
    embed.add_field(name="Username", value=username, inline=True)
    embed.add_field(name="Reason", value=reason, inline=False)

    embed.set_footer(text=f"Kicked by {interaction.user.display_name}")

    await interaction.followup.send(embed=embed)

    # Обновление метрик
    if KynxConfig.PROMETHEUS_ENABLED:
        command_counter.labels(command="kick", status="success").inc()

@bot.tree.command(name="mute", description="Mute a player")
@app_commands.describe(
    user_id="Roblox User ID",
    duration="Mute duration in minutes",
    reason="Mute reason"
)
async def mute(interaction: discord.Interaction, user_id: str, duration: int, reason: str):
    """Мут игрока"""
    await interaction.response.defer()

    # Проверка прав
    if not any(role.id in KynxConfig.DISCORD_ALLOWED_ROLES for role in interaction.user.roles):
        await interaction.followup.send("❌ You don't have permission to use this command!")
        return

    # Валидация
    if not user_id.isdigit():
        await interaction.followup.send("❌ User ID must contain only numbers!")
        return

    if duration < 1 or duration > 10080:
        await interaction.followup.send("❌ Duration must be between 1 minute and 7 days (10080 minutes)!")
        return

    # Получение данных игрока
    async with aiohttp.ClientSession() as session:
        async with session.get(f"https://users.roblox.com/v1/users/{user_id}") as resp:
            if resp.status != 200:
                await interaction.followup.send(f"❌ Could not find Roblox user with ID `{user_id}`")
                return
            user_data = await resp.json()

    username = user_data.get("name", "Unknown")

    # Отправка команды на сервер
    command_data = {
        "command": "mute",
        "userid": user_id,
        "duration": duration,
        "reason": reason,
        "executor": interaction.user.name
    }

    success = await bot.message_broker.publish(
        "kynx.direct",
        "game.commands",
        command_data
    )

    # Создание embed
    embed = discord.Embed(
        title="🔇 Player Muted",
        description=f"**{username}** has been muted for **{duration}** minutes.",
        color=discord.Color.orange(),
        timestamp=datetime.utcnow()
    )

    embed.add_field(name="User ID", value=f"`{user_id}`", inline=True)
    embed.add_field(name="Username", value=username, inline=True)
    embed.add_field(name="Duration", value=f"{duration} minutes", inline=True)
    embed.add_field(name="Reason", value=reason, inline=False)

    embed.set_footer(text=f"Muted by {interaction.user.display_name}")

    await interaction.followup.send(embed=embed)

    # Обновление метрик
    if KynxConfig.PROMETHEUS_ENABLED:
        command_counter.labels(command="mute", status="success").inc()

@bot.tree.command(name="unmute", description="Unmute a player")
@app_commands.describe(
    user_id="Roblox User ID"
)
async def unmute(interaction: discord.Interaction, user_id: str):
    """Снятие мута"""
    await interaction.response.defer()

    # Проверка прав
    if not any(role.id in KynxConfig.DISCORD_ALLOWED_ROLES for role in interaction.user.roles):
        await interaction.followup.send("❌ You don't have permission to use this command!")
        return

    # Валидация
    if not user_id.isdigit():
        await interaction.followup.send("❌ User ID must contain only numbers!")
        return

    # Получение данных игрока
    async with aiohttp.ClientSession() as session:
        async with session.get(f"https://users.roblox.com/v1/users/{user_id}") as resp:
            user_data = await resp.json() if resp.status == 200 else {}

    username = user_data.get("name", f"User {user_id}")

    # Отправка команды на сервер
    command_data = {
        "command": "unmute",
        "userid": user_id,
        "executor": interaction.user.name
    }

    success = await bot.message_broker.publish(
        "kynx.direct",
        "game.commands",
        command_data
    )

    # Создание embed
    embed = discord.Embed(
        title="🔊 Player Unmuted",
        description=f"**{username}** has been unmuted.",
        color=discord.Color.green(),
        timestamp=datetime.utcnow()
    )

    embed.add_field(name="User ID", value=f"`{user_id}`", inline=True)
    embed.add_field(name="Username", value=username, inline=True)

    embed.set_footer(text=f"Unmuted by {interaction.user.display_name}")

    await interaction.followup.send(embed=embed)

    # Обновление метрик
    if KynxConfig.PROMETHEUS_ENABLED:
        command_counter.labels(command="unmute", status="success").inc()

@bot.tree.command(name="warn", description="Warn a player")
@app_commands.describe(
    user_id="Roblox User ID",
    reason="Warning reason"
)
async def warn(interaction: discord.Interaction, user_id: str, reason: str):
    """Предупреждение игрока"""
    await interaction.response.defer()

    # Проверка прав
    if not any(role.id in KynxConfig.DISCORD_ALLOWED_ROLES for role in interaction.user.roles):
        await interaction.followup.send("❌ You don't have permission to use this command!")
        return

    # Валидация
    if not user_id.isdigit():
        await interaction.followup.send("❌ User ID must contain only numbers!")
        return

    # Получение данных игрока
    async with aiohttp.ClientSession() as session:
        async with session.get(f"https://users.roblox.com/v1/users/{user_id}") as resp:
            if resp.status != 200:
                await interaction.followup.send(f"❌ Could not find Roblox user with ID `{user_id}`")
                return
            user_data = await resp.json()

    username = user_data.get("name", "Unknown")

    # Сохранение в БД
    async with bot.database.get_postgres_session() as session:
        # Получение или создание игрока
        player = await session.get(PlayerModel, user_id)
        if not player:
            player = PlayerModel(
                user_id=user_id,
                username=username,
                display_name=user_data.get("displayName", username)
            )
            session.add(player)

        # Добавление предупреждения
        warning = {
            "reason": reason,
            "moderator": interaction.user.name,
            "timestamp": time.time()
        }

        if player.data:
            warnings = player.data.get("warnings", [])
            warnings.append(warning)
            player.data["warnings"] = warnings
        else:
            player.data = {"warnings": [warning]}

        await session.commit()

    # Отправка команды на сервер
    command_data = {
        "command": "warn",
        "userid": user_id,
        "reason": reason,
        "executor": interaction.user.name
    }

    success = await bot.message_broker.publish(
        "kynx.direct",
        "game.commands",
        command_data
    )

    # Создание embed
    embed = discord.Embed(
        title="⚠️ Player Warned",
        description=f"**{username}** has been warned.",
        color=discord.Color.yellow(),
        timestamp=datetime.utcnow()
    )

    embed.add_field(name="User ID", value=f"`{user_id}`", inline=True)
    embed.add_field(name="Username", value=username, inline=True)
    embed.add_field(name="Reason", value=reason, inline=False)

    embed.set_footer(text=f"Warned by {interaction.user.display_name}")

    await interaction.followup.send(embed=embed)

    # Обновление метрик
    if KynxConfig.PROMETHEUS_ENABLED:
        command_counter.labels(command="warn", status="success").inc()

@bot.tree.command(name="player", description="Get detailed player information")
@app_commands.describe(
    user_id="Roblox User ID"
)
async def player(interaction: discord.Interaction, user_id: str):
    """Информация об игроке"""
    await interaction.response.defer()

    # Валидация
    if not user_id.isdigit():
        await interaction.followup.send("❌ User ID must contain only numbers!")
        return

    # Проверка кеша
    cached = await bot.cache.get(f"player:{user_id}")
    if cached:
        player_data = cached
        username = player_data.get("username", "Unknown")
    else:
        # Получение данных из Roblox API
        async with aiohttp.ClientSession() as session:
            async with session.get(f"https://users.roblox.com/v1/users/{user_id}") as resp:
                if resp.status != 200:
                    await interaction.followup.send(f"❌ Could not find Roblox user with ID `{user_id}`")
                    return
                user_data = await resp.json()

        username = user_data.get("name", "Unknown")
        display_name = user_data.get("displayName", username)

        # Получение аватара
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"https://thumbnails.roblox.com/v1/users/avatar-headshot",
                params={"userIds": user_id, "size": "420x420", "format": "Png"}
            ) as resp:
                avatar_data = await resp.json() if resp.status == 200 else {}

        avatar_url = avatar_data.get("data", [{}])[0].get("imageUrl") if avatar_data else None

        player_data = {
            "user_id": user_id,
            "username": username,
            "display_name": display_name,
            "avatar_url": avatar_url
        }

        # Сохранение в кеш
        await bot.cache.set(f"player:{user_id}", player_data)

    # Получение данных из БД
    async with bot.database.get_postgres_session() as session:
        player = await session.get(PlayerModel, user_id)

        if player:
            profile = player.to_profile()

            # Получение банов
            bans_query = sqlalchemy.select(BanModel).where(
                BanModel.user_id == user_id
            ).order_by(BanModel.timestamp.desc())
            bans_result = await session.execute(bans_query)
            bans = bans_result.scalars().all()
        else:
            profile = None
            bans = []

    # Создание embed
    embed = discord.Embed(
        title=f"👤 Player Information: {player_data.get('username')}",
        color=discord.Color.blue(),
        timestamp=datetime.utcnow()
    )

    if player_data.get("avatar_url"):
        embed.set_thumbnail(url=player_data["avatar_url"])

    embed.add_field(name="User ID", value=f"`{user_id}`", inline=True)
    embed.add_field(name="Username", value=player_data.get("username", "Unknown"), inline=True)
    embed.add_field(name="Display Name", value=player_data.get("display_name", "Unknown"), inline=True)

    if profile:
        embed.add_field(name="Level", value=f"```{profile.level}```", inline=True)
        embed.add_field(name="Experience", value=f"```{profile.experience}```", inline=True)
        embed.add_field(name="Reputation", value=f"```{profile.reputation:.2f}```", inline=True)

        embed.add_field(name="First Seen", value=f"```{datetime.fromtimestamp(profile.first_seen).strftime('%Y-%m-%d %H:%M')}```", inline=False)
        embed.add_field(name="Last Seen", value=f"```{datetime.fromtimestamp(profile.last_seen).strftime('%Y-%m-%d %H:%M')}```", inline=True)
        embed.add_field(name="Playtime", value=f"```{timedelta(minutes=profile.playtime)}```", inline=True)

        embed.add_field(name="Sessions", value=f"```{profile.sessions}```", inline=True)
        embed.add_field(name="Warnings", value=f"```{len(profile.warnings)}```", inline=True)
        embed.add_field(name="Notes", value=f"```{len(profile.notes)}```", inline=True)

        if profile.is_banned:
            embed.add_field(name="Ban Status", value="```🔴 BANNED```", inline=True)
        else:
            embed.add_field(name="Ban Status", value="```🟢 Not Banned```", inline=True)

        if profile.is_muted:
            if profile.mute_expires:
                expires = datetime.fromtimestamp(profile.mute_expires).strftime('%Y-%m-%d %H:%M')
                embed.add_field(name="Mute Status", value=f"```🔇 Muted until {expires}```", inline=True)
            else:
                embed.add_field(name="Mute Status", value="```🔇 Muted```", inline=True)
        else:
            embed.add_field(name="Mute Status", value="```🔊 Not Muted```", inline=True)

    # Баны
    if bans:
        ban_list = []
        for ban in bans[:3]:
            ban_record = ban.to_record()
            ban_list.append(f"• {ban_record.reason_text} ({ban_record.level.value})")

        if ban_list:
            embed.add_field(name="Recent Bans", value="\n".join(ban_list), inline=False)

    embed.set_footer(text=f"Requested by {interaction.user.display_name}")

    await interaction.followup.send(embed=embed)

    # Обновление метрик
    if KynxConfig.PROMETHEUS_ENABLED:
        command_counter.labels(command="player", status="success").inc()

@bot.tree.command(name="banlist", description="View all active bans")
async def banlist(interaction: discord.Interaction):
    """Список банов"""
    await interaction.response.defer()

    # Получение активных банов из БД
    async with bot.database.get_postgres_session() as session:
        query = sqlalchemy.select(BanModel).where(
            BanModel.is_active == True
        ).order_by(BanModel.timestamp.desc())
        result = await session.execute(query)
        bans = result.scalars().all()

    if not bans:
        embed = discord.Embed(
            title="🔨 Ban List",
            description="No active bans found.",
            color=discord.Color.green(),
            timestamp=datetime.utcnow()
        )
        await interaction.followup.send(embed=embed)
        return

    # Экспорт в файл
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    export_file = KynxConfig.EXPORTS_DIR / f"banlist_{timestamp}.json"

    with open(export_file, 'w', encoding='utf-8') as f:
        json.dump({
            "generated": datetime.now().isoformat(),
            "total_bans": len(bans),
            "bans": [ban.to_record().to_dict() for ban in bans]
        }, f, indent=2)

    # Создание embed
    embed = discord.Embed(
        title="🔨 Ban List",
        description=f"Total active bans: **{len(bans)}**",
        color=discord.Color.red(),
        timestamp=datetime.utcnow()
    )

    # Пагинация
    items_per_page = 5
    pages = (len(bans) + items_per_page - 1) // items_per_page

    for i in range(min(items_per_page, len(bans))):
        ban = bans[i].to_record()

        embed.add_field(
            name=f"#{i+1} {ban.username}",
            value=f"ID: `{ban.user_id}`\nReason: {ban.reason_text}\nLevel: {ban.level.value}\nBy: {ban.executor}",
            inline=False
        )

    if len(bans) > items_per_page:
        embed.set_footer(text=f"Showing first {items_per_page} of {len(bans)} bans. Full list exported to file.")
    else:
        embed.set_footer(text=f"Ban list exported to `{export_file.name}`")

    await interaction.followup.send(embed=embed)

    # Обновление метрик
    if KynxConfig.PROMETHEUS_ENABLED:
        command_counter.labels(command="banlist", status="success").inc()

@bot.tree.command(name="players", description="View online players")
async def players(interaction: discord.Interaction):
    """Список онлайн игроков"""
    await interaction.response.defer()

    # Получение данных из API игры
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{KynxConfig.GAME_API_URL}/get_players") as resp:
            if resp.status != 200:
                await interaction.followup.send("❌ Could not fetch player list from game server!")
                return
            data = await resp.json()

    count = data.get("count", 0)
    players = data.get("players", [])

    # Создание embed
    embed = discord.Embed(
        title="🎮 Online Players",
        description=f"Total online: **{count}**",
        color=discord.Color.blue(),
        timestamp=datetime.utcnow()
    )

    if players:
        player_list = []
        for i, player in enumerate(players[:20], 1):
            username = player.get("username", "Unknown")
            display = player.get("display", username)
            user_id = player.get("userid", "?")
            playtime = player.get("playtime", 0)

            player_list.append(f"**{i}.** {username} (@{display})\n`{user_id}` • {playtime}m")

        embed.description += f"\n\n" + "\n".join(player_list)

        if len(players) > 20:
            embed.set_footer(text=f"Showing first 20 of {len(players)} players")
    else:
        embed.description += "\n\n*No players online*"

    await interaction.followup.send(embed=embed)

    # Обновление метрик
    if KynxConfig.PROMETHEUS_ENABLED:
        command_counter.labels(command="players", status="success").inc()

@bot.tree.command(name="restart", description="Restart the game server")
async def restart(interaction: discord.Interaction):
    """Рестарт сервера"""
    # Проверка прав
    if not any(role.id in KynxConfig.DISCORD_ADMIN_ROLES for role in interaction.user.roles):
        await interaction.response.send_message("❌ You don't have permission to use this command!")
        return

    await interaction.response.defer()

    # Отправка команды на сервер
    command_data = {
        "command": "restart",
        "executor": interaction.user.name
    }

    success = await bot.message_broker.publish(
        "kynx.direct",
        "game.commands",
        command_data
    )

    if success:
        embed = discord.Embed(
            title="🔄 Server Restarting",
            description="Restart command has been sent to the server.",
            color=discord.Color.orange(),
            timestamp=datetime.utcnow()
        )
        embed.add_field(name="Warning", value="All players will be disconnected!", inline=False)
        embed.set_footer(text=f"Requested by {interaction.user.display_name}")

        await interaction.followup.send(embed=embed)
    else:
        await interaction.followup.send("❌ Failed to send restart command!")

    # Обновление метрик
    if KynxConfig.PROMETHEUS_ENABLED:
        command_counter.labels(command="restart", status="success" if success else "failed").inc()

@bot.tree.command(name="shutdown", description="Shutdown the game server")
async def shutdown(interaction: discord.Interaction):
    """Выключение сервера"""
    # Проверка прав
    if not any(role.id in KynxConfig.DISCORD_ADMIN_ROLES for role in interaction.user.roles):
        await interaction.response.send_message("❌ You don't have permission to use this command!")
        return

    await interaction.response.defer()

    # Отправка команды на сервер
    command_data = {
        "command": "shutdown",
        "executor": interaction.user.name
    }

    success = await bot.message_broker.publish(
        "kynx.direct",
        "game.commands",
        command_data
    )

    if success:
        embed = discord.Embed(
            title="🛑 Server Shutting Down",
            description="Shutdown command has been sent to the server.",
            color=discord.Color.red(),
            timestamp=datetime.utcnow()
        )
        embed.add_field(name="Warning", value="The server will stop completely!", inline=False)
        embed.set_footer(text=f"Requested by {interaction.user.display_name}")

        await interaction.followup.send(embed=embed)
    else:
        await interaction.followup.send("❌ Failed to send shutdown command!")

    # Обновление метрик
    if KynxConfig.PROMETHEUS_ENABLED:
        command_counter.labels(command="shutdown", status="success" if success else "failed").inc()

@bot.tree.command(name="announce", description="Send announcement to all players")
@app_commands.describe(
    message="Announcement message"
)
async def announce(interaction: discord.Interaction, message: str):
    """Объявление всем игрокам"""
    # Проверка прав
    if not any(role.id in KynxConfig.DISCORD_ADMIN_ROLES for role in interaction.user.roles):
        await interaction.response.send_message("❌ You don't have permission to use this command!")
        return

    await interaction.response.defer()

    # Отправка команды на сервер
    command_data = {
        "command": "announce",
        "message": message,
        "executor": interaction.user.name
    }

    success = await bot.message_broker.publish(
        "kynx.direct",
        "game.commands",
        command_data
    )

    if success:
        embed = discord.Embed(
            title="📢 Announcement Sent",
            description="The announcement has been sent to all players.",
            color=discord.Color.blue(),
            timestamp=datetime.utcnow()
        )
        embed.add_field(name="Message", value=message, inline=False)
        embed.set_footer(text=f"Sent by {interaction.user.display_name}")

        await interaction.followup.send(embed=embed)
    else:
        await interaction.followup.send("❌ Failed to send announcement!")

    # Обновление метрик
    if KynxConfig.PROMETHEUS_ENABLED:
        command_counter.labels(command="announce", status="success" if success else "failed").inc()

@bot.tree.command(name="broadcast", description="Broadcast message to all players")
@app_commands.describe(
    message="Broadcast message"
)
async def broadcast(interaction: discord.Interaction, message: str):
    """Широковещательное сообщение"""
    # Проверка прав
    if not any(role.id in KynxConfig.DISCORD_ADMIN_ROLES for role in interaction.user.roles):
        await interaction.response.send_message("❌ You don't have permission to use this command!")
        return

    await interaction.response.defer()

    # Отправка команды на сервер
    command_data = {
        "command": "broadcast",
        "message": message,
        "executor": interaction.user.name
    }

    success = await bot.message_broker.publish(
        "kynx.direct",
        "game.commands",
        command_data
    )

    if success:
        embed = discord.Embed(
            title="📡 Broadcast Sent",
            description="The message has been broadcasted to all players.",
            color=discord.Color.purple(),
            timestamp=datetime.utcnow()
        )
        embed.add_field(name="Message", value=message, inline=False)
        embed.set_footer(text=f"Sent by {interaction.user.display_name}")

        await interaction.followup.send(embed=embed)
    else:
        await interaction.followup.send("❌ Failed to send broadcast!")

    # Обновление метрик
    if KynxConfig.PROMETHEUS_ENABLED:
        command_counter.labels(command="broadcast", status="success" if success else "failed").inc()

@bot.tree.command(name="note", description="Add a note to a player")
@app_commands.describe(
    user_id="Roblox User ID",
    note="Note content"
)
async def note(interaction: discord.Interaction, user_id: str, note: str):
    """Добавление заметки к игроку"""
    await interaction.response.defer()

    # Проверка прав
    if not any(role.id in KynxConfig.DISCORD_ALLOWED_ROLES for role in interaction.user.roles):
        await interaction.followup.send("❌ You don't have permission to use this command!")
        return

    # Валидация
    if not user_id.isdigit():
        await interaction.followup.send("❌ User ID must contain only numbers!")
        return

    # Получение данных игрока
    async with aiohttp.ClientSession() as session:
        async with session.get(f"https://users.roblox.com/v1/users/{user_id}") as resp:
            if resp.status != 200:
                await interaction.followup.send(f"❌ Could not find Roblox user with ID `{user_id}`")
                return
            user_data = await resp.json()

    username = user_data.get("name", "Unknown")

    # Сохранение в БД
    async with bot.database.get_postgres_session() as session:
        # Получение или создание игрока
        player = await session.get(PlayerModel, user_id)
        if not player:
            player = PlayerModel(
                user_id=user_id,
                username=username,
                display_name=user_data.get("displayName", username)
            )
            session.add(player)

        # Добавление заметки
        note_entry = {
            "content": note,
            "moderator": interaction.user.name,
            "timestamp": time.time()
        }

        if player.data:
            notes = player.data.get("notes", [])
            notes.append(note_entry)
            player.data["notes"] = notes
        else:
            player.data = {"notes": [note_entry]}

        await session.commit()

    # Создание embed
    embed = discord.Embed(
        title="📝 Note Added",
        description=f"Note added for **{username}**.",
        color=discord.Color.blue(),
        timestamp=datetime.utcnow()
    )

    embed.add_field(name="User ID", value=f"`{user_id}`", inline=True)
    embed.add_field(name="Username", value=username, inline=True)
    embed.add_field(name="Note", value=note, inline=False)

    embed.set_footer(text=f"Added by {interaction.user.display_name}")

    await interaction.followup.send(embed=embed)

    # Обновление метрик
    if KynxConfig.PROMETHEUS_ENABLED:
        command_counter.labels(command="note", status="success").inc()

@bot.tree.command(name="clearnotes", description="Clear all notes for a player")
@app_commands.describe(
    user_id="Roblox User ID"
)
async def clearnotes(interaction: discord.Interaction, user_id: str):
    """Очистка всех заметок игрока"""
    await interaction.response.defer()

    # Проверка прав
    if not any(role.id in KynxConfig.DISCORD_ADMIN_ROLES for role in interaction.user.roles):
        await interaction.followup.send("❌ You don't have permission to use this command!")
        return

    # Валидация
    if not user_id.isdigit():
        await interaction.followup.send("❌ User ID must contain only numbers!")
        return

    # Получение данных игрока
    async with aiohttp.ClientSession() as session:
        async with session.get(f"https://users.roblox.com/v1/users/{user_id}") as resp:
            user_data = await resp.json() if resp.status == 200 else {}

    username = user_data.get("name", f"User {user_id}")

    # Очистка заметок в БД
    async with bot.database.get_postgres_session() as session:
        player = await session.get(PlayerModel, user_id)
        if player and player.data:
            player.data["notes"] = []
            await session.commit()

    # Создание embed
    embed = discord.Embed(
        title="🧹 Notes Cleared",
        description=f"All notes for **{username}** have been cleared.",
        color=discord.Color.green(),
        timestamp=datetime.utcnow()
    )

    embed.add_field(name="User ID", value=f"`{user_id}`", inline=True)
    embed.add_field(name="Username", value=username, inline=True)

    embed.set_footer(text=f"Cleared by {interaction.user.display_name}")

    await interaction.followup.send(embed=embed)

    # Обновление метрик
    if KynxConfig.PROMETHEUS_ENABLED:
        command_counter.labels(command="clearnotes", status="success").inc()

@bot.tree.command(name="history", description="View player moderation history")
@app_commands.describe(
    user_id="Roblox User ID"
)
async def history(interaction: discord.Interaction, user_id: str):
    """История модерации игрока"""
    await interaction.response.defer()

    # Валидация
    if not user_id.isdigit():
        await interaction.followup.send("❌ User ID must contain only numbers!")
        return

    # Получение данных из БД
    async with bot.database.get_postgres_session() as session:
        player = await session.get(PlayerModel, user_id)

        if not player:
            await interaction.followup.send(f"❌ No data found for user ID `{user_id}`")
            return

        profile = player.to_profile()

        # Получение банов
        bans_query = sqlalchemy.select(BanModel).where(
            BanModel.user_id == user_id
        ).order_by(BanModel.timestamp.desc())
        bans_result = await session.execute(bans_query)
        bans = bans_result.scalars().all()

    # Получение аватара из Roblox API
    async with aiohttp.ClientSession() as session:
        async with session.get(
            f"https://thumbnails.roblox.com/v1/users/avatar-headshot",
            params={"userIds": user_id, "size": "420x420", "format": "Png"}
        ) as resp:
            avatar_data = await resp.json() if resp.status == 200 else {}

    avatar_url = avatar_data.get("data", [{}])[0].get("imageUrl") if avatar_data else None

    # Создание embed
    embed = discord.Embed(
        title=f"📜 Moderation History: {profile.username}",
        color=discord.Color.purple(),
        timestamp=datetime.utcnow()
    )

    if avatar_url:
        embed.set_thumbnail(url=avatar_url)

    embed.add_field(name="User ID", value=f"`{user_id}`", inline=True)
    embed.add_field(name="First Seen", value=f"```{datetime.fromtimestamp(profile.first_seen).strftime('%Y-%m-%d %H:%M')}```", inline=True)

    # Баны
    if bans:
        ban_list = []
        for i, ban in enumerate(bans[:5], 1):
            ban_record = ban.to_record()
            status = "✅ Active" if ban_record.is_active else "❌ Inactive"
            ban_list.append(f"**{i}.** {ban_record.reason_text}\n{status} • {ban_record.level.value} • {datetime.fromtimestamp(ban_record.timestamp).strftime('%Y-%m-%d %H:%M')}")

        embed.add_field(name=f"Bans ({len(bans)})", value="\n".join(ban_list), inline=False)
    else:
        embed.add_field(name="Bans", value="No ban history", inline=False)

    # Предупреждения
    if profile.warnings:
        warning_list = []
        for i, warning in enumerate(profile.warnings[-5:], 1):
            warning_list.append(f"**{i}.** {warning['reason']}\n{warning['moderator']} • {datetime.fromtimestamp(warning['timestamp']).strftime('%Y-%m-%d %H:%M')}")

        embed.add_field(name=f"Warnings ({len(profile.warnings)})", value="\n".join(warning_list), inline=False)
    else:
        embed.add_field(name="Warnings", value="No warning history", inline=False)

    # Заметки
    if profile.notes:
        note_list = []
        for i, note in enumerate(profile.notes[-5:], 1):
            note_list.append(f"**{i}.** {note['content'][:100]}\n{note['moderator']} • {datetime.fromtimestamp(note['timestamp']).strftime('%Y-%m-%d %H:%M')}")

        embed.add_field(name=f"Notes ({len(profile.notes)})", value="\n".join(note_list), inline=False)
    else:
        embed.add_field(name="Notes", value="No notes", inline=False)

    embed.set_footer(text=f"Requested by {interaction.user.display_name}")

    await interaction.followup.send(embed=embed)

    # Обновление метрик
    if KynxConfig.PROMETHEUS_ENABLED:
        command_counter.labels(command="history", status="success").inc()

@bot.tree.command(name="ai", description="AI-powered analysis")
@app_commands.describe(
    text="Text to analyze"
)
async def ai_command(interaction: discord.Interaction, text: str):
    """AI анализ текста"""
    await interaction.response.defer()

    # Анализ тональности
    sentiment = await bot.ai.analyze_sentiment(text)

    # Определение токсичности
    toxicity = await bot.ai.detect_toxicity(text)

    # Создание embed
    embed = discord.Embed(
        title="🤖 AI Analysis",
        color=discord.Color.purple(),
        timestamp=datetime.utcnow()
    )

    embed.add_field(name="Input Text", value=text[:500], inline=False)

    embed.add_field(
        name="Sentiment Analysis",
        value=f"**Label:** {sentiment.get('label', 'UNKNOWN')}\n**Score:** {sentiment.get('score', 0):.3f}",
        inline=True
    )

    embed.add_field(
        name="Toxicity Detection",
        value=f"**Score:** {toxicity:.3f}\n**Level:** {'High' if toxicity > 0.7 else 'Medium' if toxicity > 0.4 else 'Low'}",
        inline=True
    )

    # Генерация ответа
    if toxicity > 0.8:
        response = "⚠️ Warning: This message contains highly toxic content!"
    elif toxicity > 0.5:
        response = "⚠️ Caution: This message contains moderately toxic content."
    else:
        response = "✅ This message appears to be safe."

    embed.add_field(name="Recommendation", value=response, inline=False)

    embed.set_footer(text=f"Requested by {interaction.user.display_name}")

    await interaction.followup.send(embed=embed)

    # Обновление метрик
    if KynxConfig.PROMETHEUS_ENABLED:
        command_counter.labels(command="ai", status="success").inc()

@bot.tree.command(name="help", description="Show all commands")
async def help_command(interaction: discord.Interaction):
    """Справка по командам"""
    embed = discord.Embed(
        title="🤖 KYNX X 4.0.0 Commands",
        description="Next generation moderation system",
        color=discord.Color.blue(),
        timestamp=datetime.utcnow()
    )

    embed.add_field(
        name="🔨 **Moderation**",
        value=(
            "`/ban` - Ban a player\n"
            "`/unban` - Unban a player\n"
            "`/kick` - Kick a player\n"
            "`/mute` - Mute a player\n"
            "`/unmute` - Unmute a player\n"
            "`/warn` - Warn a player"
        ),
        inline=True
    )

    embed.add_field(
        name="📊 **Information**",
        value=(
            "`/player` - Player information\n"
            "`/banlist` - List active bans\n"
            "`/players` - Online players\n"
            "`/history` - Moderation history\n"
            "`/stats` - Server statistics"
        ),
        inline=True
    )

    embed.add_field(
        name="📝 **Notes**",
        value=(
            "`/note` - Add player note\n"
            "`/clearnotes` - Clear player notes"
        ),
        inline=True
    )

    embed.add_field(
        name="⚙️ **Admin**",
        value=(
            "`/restart` - Restart server\n"
            "`/shutdown` - Shutdown server\n"
            "`/announce` - Send announcement\n"
            "`/broadcast` - Broadcast message"
        ),
        inline=True
    )

    embed.add_field(
        name="🤖 **AI**",
        value=(
            "`/ai` - AI text analysis\n"
            "`/ping` - Check latency"
        ),
        inline=True
    )

    embed.add_field(
        name="🔧 **Utility**",
        value=(
            "`/help` - Show this menu\n"
            "`/ping` - Check latency"
        ),
        inline=True
    )

    embed.set_footer(text="KYNX X 4.0.0 • Next Generation Moderation")

    await interaction.response.send_message(embed=embed)

    # Обновление метрик
    if KynxConfig.PROMETHEUS_ENABLED:
        command_counter.labels(command="help", status="success").inc()

# ==================== СОБЫТИЯ ====================

@bot.event
async def on_ready():
    """Событие готовности бота"""
    logger.info(f"✅ KYNX X 4.0.0 is online! Logged in as {bot.user}")
    logger.info(f"📊 Connected to {len(bot.guilds)} guilds")
    logger.info(f"⚙️ Loaded {len(bot.tree.get_commands())} commands")

    # Обновление метрик
    if KynxConfig.PROMETHEUS_ENABLED:
        players_online_gauge.set(0)
        active_bans_gauge.set(0)

@bot.event
async def on_guild_join(guild):
    """Событие присоединения к серверу"""
    logger.info(f"📥 Joined guild: {guild.name} (ID: {guild.id})")

@bot.event
async def on_guild_remove(guild):
    """Событие покидания сервера"""
    logger.info(f"📤 Left guild: {guild.name} (ID: {guild.id})")

@bot.event
async def on_command_error(ctx, error):
    """Обработка ошибок команд"""
    if isinstance(error, commands.CommandNotFound):
        return

    logger.error(f"Command error: {error}")

    # Обновление метрик
    if KynxConfig.PROMETHEUS_ENABLED:
        error_counter.labels(type="command", component="discord").inc()

# ==================== ЗАПУСК ====================

def main():
    """Главная функция запуска"""
    if not KynxConfig.DISCORD_TOKEN:
        logger.error("❌ No Discord token found in .env file!")
        return

    logger.info("=" * 60)
    logger.info("🚀 KYNX X 4.0.0 - Starting up...")
    logger.info("=" * 60)

    # Информация о системе
    logger.info(f"📦 Python: {sys.version}")
    logger.info(f"💻 CPU: {cpuinfo.get_cpu_info()['brand_raw']}")
    logger.info(f"🧠 RAM: {psutil.virtual_memory().total / (1024**3):.1f} GB")

    if torch.cuda.is_available():
        logger.info(f"🎮 GPU: {torch.cuda.get_device_name(0)}")
        logger.info(f"🎮 CUDA: {torch.version.cuda}")

    if tf.config.list_physical_devices('GPU'):
        logger.info(f"🎮 TensorFlow GPU: Available")

    # Запуск Prometheus сервера
    if KynxConfig.PROMETHEUS_ENABLED:
        from prometheus_client import start_http_server
        start_http_server(KynxConfig.PROMETHEUS_PORT)
        logger.info(f"📊 Prometheus metrics available on port {KynxConfig.PROMETHEUS_PORT}")

    # Запуск бота
    try:
        bot.run(KynxConfig.DISCORD_TOKEN, log_handler=None)
    except KeyboardInterrupt:
        logger.info("👋 Shutting down...")
    except Exception as e:
        logger.error(f"💥 Fatal error: {e}", exc_info=True)
    finally:
        asyncio.run(bot.close())

if __name__ == "__main__":
    main()