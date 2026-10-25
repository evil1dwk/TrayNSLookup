from PyQt6.QtCore import QThread, pyqtSignal
import dns.resolver

class DNSLookupThread(QThread):
    finished = pyqtSignal(str, str)

    def __init__(self, query, record_type, server):
        super().__init__()
        self.query = query
        self.record_type = record_type
        self.server = server

    def run(self):
        resolver = dns.resolver.Resolver()
        if self.server:
            resolver.nameservers = [self.server]
        resolver.lifetime = 5
        resolver.timeout = 3
        try:
            answers = resolver.resolve(self.query, self.record_type)
            result = "\n".join(r.to_text() for r in answers)
        except Exception as e:
            result = f"Error: {e}"
        self.finished.emit(self.query, result)
