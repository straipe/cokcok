

class FileNotFoundException(FileNotFoundError):
    def __init__(self, file_url):
        super().__init__(f"File not found: {file_url}")
        self.file_url = file_url

class InvalidFileError(ValueError):
    def __init__(self, file_url, additional_info=""):
        message = f"Invalid file: {file_url}. {additional_info}"
        super().__init__(message)
        self.file_url = file_url
        self.additional_info = additional_info