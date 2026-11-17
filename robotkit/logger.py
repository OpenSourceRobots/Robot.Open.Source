import csv


class CsvLogger:
    def __init__(self, path, fields):
        self.fields = list(fields)
        self.file = open(path, "w", newline="")
        self.writer = csv.writer(self.file)
        self.writer.writerow(self.fields)

    def log(self, **values):
        self.writer.writerow([values[field] for field in self.fields])

    def close(self):
        self.file.close()

    def __enter__(self):
        return self

    def __exit__(self, *error):
        self.close()
