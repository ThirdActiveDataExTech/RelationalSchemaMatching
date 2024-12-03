class TestCase:
    def __init__(self, name: str, data: any, expect: any):
        self.name = name
        self.data = data
        self.expect = expect

    def __str__(self):
        return f"(case='{self.name}', data={self.data}, expect={self.expect})"

    def __repr__(self):
        return self.__str__()
