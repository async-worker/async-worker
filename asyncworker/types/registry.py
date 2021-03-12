from typing import Type, Any, Dict, Optional, Tuple

from asyncworker.typing import get_args, get_origin


class RegistryItem:
    def __init__(self, type: Type, value: Any, type_args: Tuple = None) -> None:
        self.type = type
        self.value = value
        self.type_args = type_args


class TypesRegistry:
    def __init__(self):
        self._data: Dict[Tuple, RegistryItem] = {}
        self.__by_name: Dict[str, RegistryItem] = {}

    def set(
        self,
        obj: Any,
        type_definition: Type = None,
        param_name: Optional[str] = None,
    ) -> None:
        has_type_args = get_args(type_definition)
        origin = get_origin(obj) or obj.__class__

        self._data[(origin, has_type_args)] = RegistryItem(
            type=origin, value=obj, type_args=has_type_args
        )
        if param_name:
            self.__by_name[param_name] = RegistryItem(
                type=obj.__class__, value=obj
            )

    def get(
        self, _type: Type, param_name: str = None, type_args=None
    ) -> Optional[Any]:
        origin = get_origin(_type) or _type
        if param_name:
            try:
                if self.__by_name[param_name].type == _type:
                    return self.__by_name[param_name].value
            except KeyError:
                return None

        try:
            return self._data[(origin, get_args(_type))].value
        except KeyError:
            return None
