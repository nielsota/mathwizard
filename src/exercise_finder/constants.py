from exercise_finder.enums import ExamLevel, ImageType

pdf_acronym_to_level_mapping = {
    "vw": ExamLevel.VWO,
    "hv": ExamLevel.HAVO,
    "vm": ExamLevel.VMBO,
}

image_suffixes = {
    f".{ImageType.PNG.value}",
    f".{ImageType.JPG.value}",
    f".{ImageType.JPEG.value}",
    f".{ImageType.WEBP.value}",
}

# System/hidden files to ignore when processing directories
IGNORED_FILES = {
    ".DS_Store",     # macOS
    ".gitkeep",      # Git placeholder
    "Thumbs.db",     # Windows
    "desktop.ini",   # Windows
}

# Session expiration time in seconds (24 hours)
SESSION_EXPIRATION_SECONDS = 24 * 60 * 60

# Number of intro pages to skip when parsing exam PDFs (cover page, instructions, etc.)
PDF_EXAM_INTRO_PAGES_TO_SKIP = 2

# Minimum content thresholds for PDF parsing (percentage of page dimensions)
# Regions smaller than these thresholds are skipped as likely hallucinations
MIN_CONTINUATION_CONTENT_PCT = 10.0  # Minimum height for continuation regions
MIN_FIGURE_DIMENSION_PCT = 15.0       # Minimum width AND height for figures
