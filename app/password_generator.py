# 密码生成器核心模块
import random
import string
import math

UPPERCASE = string.ascii_uppercase
LOWERCASE = string.ascii_lowercase
DIGITS = string.digits
SPECIAL_CHARS = "!@#$%^&*()_+-=[]{}|;:,.<>?"
SIMILAR_CHARS = "1lI0Oo"


def estimate_strength(password):
    length = len(password)
    pool_size = 0
    if any(c in string.ascii_uppercase for c in password):
        pool_size += 26
    if any(c in string.ascii_lowercase for c in password):
        pool_size += 26
    if any(c in string.digits for c in password):
        pool_size += 10
    if any(c in SPECIAL_CHARS for c in password):
        pool_size += len(SPECIAL_CHARS)
    if pool_size == 0:
        pool_size = 1
    entropy = length * math.log2(pool_size) if pool_size > 1 else 0
    score = min(100, int((length / 64) * 30 + (pool_size / 4 if pool_size < 4 else 4) * 7.5 + (entropy / 128) * 40))
    if score >= 80:
        return score, "强", "#2ECC71"
    elif score >= 50:
        return score, "中", "#F39C12"
    else:
        return score, "弱", "#E74C3C"


def generate_password(
    length=16,
    use_upper=True,
    use_lower=True,
    use_digits=True,
    use_special=True,
    custom_chars="",
    exclude_similar=False,
    custom_mode="only",      # "only"=只用自定义字符集, "include"=必须包含自定义字符集
    shuffle_custom=True,     # 是否打乱自定义字符集中的字符顺序
):
    if length < 4:
        length = 4
    if length > 128:
        length = 128

    char_pool = ""
    mandatory_pools = []

    for chars, enabled in [
        (UPPERCASE, use_upper),
        (LOWERCASE, use_lower),
        (DIGITS, use_digits),
        (SPECIAL_CHARS, use_special),
    ]:
        if enabled:
            if exclude_similar:
                chars = "".join(c for c in chars if c not in SIMILAR_CHARS)
            if chars:
                char_pool += chars
                mandatory_pools.append(chars)

    custom = custom_chars.strip()
    if custom:
        if exclude_similar:
            custom = "".join(c for c in custom if c not in SIMILAR_CHARS)
        if not custom:
            return ""
        custom = "".join(dict.fromkeys(custom))  # 去重保留顺序
        if custom_mode == "only":
            # 只用自定义字符集
            char_pool = custom
            mandatory_pools = []
            if shuffle_custom:
                # 打乱自定义字符集中字符的顺序来生成密码
                char_pool_list = list(custom)
                random.shuffle(char_pool_list)
                char_pool = "".join(char_pool_list)
        elif custom_mode == "include":
            # 必须包含自定义字符集中的字符
            mandatory_pools.append(custom)
            if shuffle_custom:
                char_pool_list = list(custom)
                random.shuffle(char_pool_list)
                custom = "".join(char_pool_list)
            char_pool += custom

    if not char_pool:
        return ""

    password = [random.choice(p) for p in mandatory_pools]
    remaining = length - len(password)
    if remaining > 0:
        password.extend(random.choices(char_pool, k=remaining))
    random.shuffle(password)
    return "".join(password)
