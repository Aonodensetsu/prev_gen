class LazyloadError(AttributeError):
    """Attribute was not assigned a value during object creation and does not support lazy loading"""
    def __init__(self, item):
        super().__init__(f'({item}) ' + self.__doc__)
