from typing import Optional, Tuple, Any, Type


def get_args(_type: Type) -> Optional[Tuple]:
    if _type and hasattr(_type, "__args__"):
        return _type.__args__

    return None


def get_origin(_type: Type) -> Optional[Type]:
    if _type and hasattr(_type, "__origin__"):
        return _type.__origin__

    return None
