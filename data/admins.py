# ============================================
# 🔹 data/admins.py — administratorlar ro'yxati
# ============================================

# Administratorlarning IDlari (o'zingizniki bilan almashtiring)
ADMINS = [
    7296673831,    # Администратор
    5523530887,    # Директор
]

# Гуруҳ администраторлари учун функция
def is_admin(user_id: int) -> bool:
    """Foydalanuvchi administratormi tekshirish"""
    return user_id in ADMINS

def is_group_admin(user_id: int, group_id: int) -> bool:
    """Фойдаланувчи гуруҳ администраторими ёки йўқми"""
    # Бу функция group_moderation.py да базадан текширилади
    return False