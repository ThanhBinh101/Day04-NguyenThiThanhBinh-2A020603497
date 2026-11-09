import json
import os
from typing import List, Dict, Any
from datetime import datetime

RAW_DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "raw-data")

# ---------------------------------------------------------------------------
# Tool #1: search_product_catalog
# Đọc file product_catalog.json và lọc theo category, max_price.
# ---------------------------------------------------------------------------

def search_product_catalog(category: str, max_price: int = 999999999999) -> List[Dict[str, Any]]:
    """
    Tra cứu sản phẩm/dịch vụ Vingroup theo danh mục và giá tối đa.
    
    Args:
        category: Loại sản phẩm ('xe_dien' hoặc 'du_lich').
        max_price: Giá tối đa (VNĐ). Mặc định không giới hạn.
    
    Returns:
        Danh sách sản phẩm phù hợp điều kiện.
    """
    catalog_file = os.path.join(RAW_DATA_DIR, "product_catalog.json")
    if not os.path.exists(catalog_file):
        return [{"error": "Product catalog file not found."}]

    with open(catalog_file, "r", encoding="utf-8") as file:
        products = json.load(file)

    if not isinstance(products, list):
        raise ValueError("Product catalog must contain a JSON list.")

    normalized_category = category.strip().lower()
    return [
        product for product in products
        if isinstance(product, dict)
        and str(product.get("category", "")).lower() == normalized_category
        and product.get("price_vnd", float("inf")) <= max_price
    ]


# ---------------------------------------------------------------------------
# Tool #2: submit_support_ticket
# Tạo ticket mới và lưu vào support_tickets.json.
# ---------------------------------------------------------------------------

def submit_support_ticket(
    customer_name: str,
    issue_description: str,
    priority: str = "medium"
) -> Dict[str, Any]:
    """
    Ghi nhận yêu cầu hỗ trợ của khách hàng vào hệ thống ticket.
    
    Args:
        customer_name: Tên khách hàng.
        issue_description: Mô tả vấn đề cần hỗ trợ.
        priority: Mức độ ưu tiên ('low', 'medium', 'high'). Mặc định 'medium'.
    
    Returns:
        Thông tin ticket vừa tạo bao gồm ticket_id, status.
    """
    tickets_file = os.path.join(RAW_DATA_DIR, "support_tickets.json")
    os.makedirs(RAW_DATA_DIR, exist_ok=True)
    if os.path.exists(tickets_file):
        with open(tickets_file, "r", encoding="utf-8") as file:
            existing_tickets = json.load(file)
        if not isinstance(existing_tickets, list):
            raise ValueError("Support tickets file must contain a JSON list.")
    else:
        existing_tickets = []

    today = datetime.now().strftime("%Y%m%d")
    sequence = 0
    prefix = f"TK-{today}-"
    for ticket in existing_tickets:
        if isinstance(ticket, dict) and str(ticket.get("ticket_id", "")).startswith(prefix):
            suffix = str(ticket["ticket_id"])[len(prefix):]
            if suffix.isdigit():
                sequence = max(sequence, int(suffix))
    ticket_id = f"{prefix}{sequence + 1:03d}"
    normalized_priority = priority.strip().lower()
    if normalized_priority not in {"low", "medium", "high"}:
        raise ValueError("priority must be 'low', 'medium', or 'high'.")

    new_ticket = {
        "ticket_id": ticket_id,
        "customer_name": customer_name,
        "issue_description": issue_description,
        "priority": normalized_priority,
        "status": "open",
        "created_at": datetime.now().astimezone().isoformat(),
        "category": "general"
    }
    existing_tickets.append(new_ticket)

    with open(tickets_file, "w", encoding="utf-8") as file:
        json.dump(existing_tickets, file, indent=2, ensure_ascii=False)

    return {
        "ticket_id": ticket_id,
        "customer_name": customer_name,
        "priority": normalized_priority,
        "status": "open",
        "message": f"Ticket {ticket_id} đã được tạo thành công."
    }


# ---------------------------------------------------------------------------
# TOOL_DEFINITIONS — JSON Schemas mô tả cho LLM
# JSON Schemas mô tả các tham số của từng tool.
# ---------------------------------------------------------------------------

TOOL_DEFINITIONS = [
    {
        "name": "search_product_catalog",
        "description": "Tra cứu sản phẩm/dịch vụ Vingroup theo danh mục và giá tối đa.",
        "parameters": {
            "type": "object",
            "properties": {
                "category": {
                    "type": "string",
                    "description": "Loại sản phẩm: 'xe_dien' hoặc 'du_lich'.",
                    "enum": ["xe_dien", "du_lich"]
                },
                "max_price": {
                    "type": "integer",
                    "description": "Giá tối đa tính bằng VNĐ."
                }
            },
            "required": ["category"]
        }
    },
    {
        "name": "submit_support_ticket",
        "description": "Tạo yêu cầu hỗ trợ mới cho khách hàng.",
        "parameters": {
            "type": "object",
            "properties": {
                "customer_name": {
                    "type": "string",
                    "description": "Tên khách hàng."
                },
                "issue_description": {
                    "type": "string",
                    "description": "Mô tả vấn đề cần hỗ trợ."
                },
                "priority": {
                    "type": "string",
                    "description": "Mức độ ưu tiên của ticket.",
                    "enum": ["low", "medium", "high"]
                }
            },
            "required": ["customer_name", "issue_description"]
        }
    }
]


# ---------------------------------------------------------------------------
# TOOL_MAP — Ánh xạ tên tool → hàm thực thi
# ---------------------------------------------------------------------------

TOOL_MAP = {
    "search_product_catalog": search_product_catalog,
    "submit_support_ticket": submit_support_ticket
}