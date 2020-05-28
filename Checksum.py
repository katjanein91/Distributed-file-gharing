import hashlib


class Checksum:
    def __init__(self, path):
        #self.path = r"C:\Users\Tobi\Desktop\test.txt"
        self.path = path
        self.md5_hash = hashlib.md5()

    def generate_digest(self):
        file = open(self.path, "rb")
        content = file.read()
        self.md5_hash.update(content)
        digest = self.md5_hash.hexdigest()
        print(digest)
        return digest
