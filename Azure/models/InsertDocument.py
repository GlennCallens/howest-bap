class InsertDocument:
    def __init__(self, file_name, content, explanation):
        self.file_name = file_name
        self.content = content
        self.explanation = explanation

    def to_string(self):
        return f"File Name: {self.file_name}\nContent: {self.content}\nExplanation: {self.explanation}"
