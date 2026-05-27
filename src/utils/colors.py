"""Paleta de cores premium do dashboard."""

COLORS = {
    "bg_primary":   "#0B0F19",
    "bg_secondary": "#111827",
    "bg_tertiary":  "#1F2937",
    "text_primary": "#F9FAFB",
    "text_muted":   "#9CA3AF",
    "border":       "#374151",
    "accent":       "#3B82F6",
    "success":      "#10B981",
    "warning":      "#F59E0B",
    "danger":       "#EF4444",
    "info":         "#06B6D4",
    "purple":       "#8B5CF6",
    "pink":         "#EC4899",
}

CHANNEL_COLORS = {
    "loja_fisica": "#1F4E79",
    "ecommerce":   "#06B6D4",
}

COMPETITOR_COLORS = {
    "Amazon":        "#FF9900",
    "Magalu":        "#0046BE",
    "Mercado Livre": "#FFE600",
    "Shopee":        "#EE4D2D",
}

SEQUENTIAL_BLUE  = ["#0B1E3A", "#1E3A5F", "#2C5282", "#3B82F6", "#60A5FA", "#93C5FD"]
DIVERGING_RDYLGN = ["#EF4444", "#F87171", "#FCA5A5", "#E5E7EB", "#86EFAC", "#10B981", "#059669"]


def status_color(delta: float, neutral_threshold: float = 0.0) -> str:
    if delta > neutral_threshold:
        return COLORS["success"]
    if delta < -neutral_threshold:
        return COLORS["danger"]
    return COLORS["text_muted"]
