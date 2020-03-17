from typing import Type, Any, Dict, Optional


class RegistryItem:
    def __init__(self, type: Type, value: Any) -> None:
        self.type = type
        self.value = value


class TypesRegistry:
    def __init__(self):
        self.__data: Dict[Type, RegistryItem] = {}
        self.__by_name: Dict[str, RegistryItem] = {}

    def set(
        self,
        obj: Any,
        type_definition: Type = None,
        param_name: Optional[str] = None,
    ) -> None:
        self.__data[obj.__class__] = RegistryItem(type=obj.__class__, value=obj)
        if param_name:
            self.__by_name[param_name] = RegistryItem(
                type=obj.__class__, value=obj
            )

    def get(self, _type: Type, param_name: str = None) -> Optional[Any]:
        if param_name:
            try:
                if self.__by_name[param_name].type == _type:
                    return self.__by_name[param_name].value
            except KeyError:
                return None

        try:
            return self.__data[_type].value
        except KeyError:
            return None
