class LazySingleton:
    """通用的延遲初始化單例模板"""

    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def initialize(self):
        """初始化方法（需在子類別中實作）"""
        raise NotImplementedError("initialize() 必須在子類別中實作")

    def __getattribute__(self, name):
        """在存取任何方法或屬性前，確保已初始化"""
        if name != "initialize" and not object.__getattribute__(self, "_initialized"):
            object.__getattribute__(self, "initialize")()
        return object.__getattribute__(self, name)
