import hashlib


class Checksum:
    def __init__(self, path):
        self.path = path
        self.md5_hash = hashlib.md5()

    def generate_digest(self):
        file = open(self.path, "rb")
        content = file.read()
        self.md5_hash.update(content)
        digest = self.md5_hash.hexdigest()

        return digest
