from pathlib import Path

ROOT = Path(__file__).parent.parent


RESOURCES_DIR = ROOT / "resources"
WATER_MARK_TEMPLATE_IMAGE_PATH = RESOURCES_DIR / "watermark_template.png"

WATER_MARK_DETECT_YOLO_WEIGHTS = RESOURCES_DIR / "best.pt"

OUTPUT_DIR = ROOT / "output"

OUTPUT_DIR.mkdir(exist_ok=True, parents=True)

# 水印检测精度配置
DETECTION_MIN_CONFIDENCE = 0.25  # 提高置信度阈值，减少误检
DETECTION_HIGH_CONFIDENCE = 0.6  # 高置信度阈值，用于稳定检测
DETECTION_TEMPORAL_CONSISTENCY_WINDOW = 3  # 时序一致性检查窗口
DETECTION_MIN_CONSISTENT_FRAMES = 2  # 最少连续检测帧数
DETECTION_MAX_JUMP_DISTANCE = 50  # 最大跳跃距离（像素）
# 模板匹配辅助检测
TEMPLATE_MATCH_SCALES = (0.85, 0.9, 0.95, 1.0, 1.05, 1.1)
TEMPLATE_MATCH_MIN_SCORE = 0.55
TEMPLATE_SEARCH_EXPANSION_RATIO = 0.6

# 边界框处理配置
BBOX_PADDING_RATIO = 0.3  # 增加填充比例，确保完整覆盖
BBOX_MIN_EDGE_PX = 32
BBOX_SMOOTHING_WINDOW = 7  # 增加平滑窗口大小
BBOX_STABILITY_THRESHOLD = 0.8  # 边界框稳定性阈值

# 掩码处理配置
MASK_DILATION_KERNEL_SIZE = 11  # 增加膨胀核大小
MASK_DILATION_ITERATIONS = 2  # 增加膨胀迭代次数

DEFAULT_WATERMARK_REMOVE_MODEL = "lama"

WORKING_DIR = ROOT / "working_dir"
WORKING_DIR.mkdir(exist_ok=True, parents=True)

LOGS_PATH = ROOT / "logs"
LOGS_PATH.mkdir(exist_ok=True, parents=True)

DATA_PATH = ROOT / "data"
DATA_PATH.mkdir(exist_ok=True, parents=True)

SQLITE_PATH = DATA_PATH / "db.sqlite3"

# 性能优化配置
BATCH_SIZE = 8  # 批处理大小（降低以避免内存问题）
USE_FP16 = True  # 半精度推理
ENABLE_BATCH_PROCESSING = True  # 启用批处理
FRAME_BUFFER_SIZE = 100  # 帧缓冲区大小
ENCODING_PRESET = "medium"  # FFmpeg 编码预设 (slow/medium/fast/faster)
ENABLE_HW_ACCEL = True  # 启用硬件编码加速
MAX_WORKERS = 4  # 多进程数量
