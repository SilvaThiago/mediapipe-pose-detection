import csv

class CsvFileService:
    def __init__(self, file_path):
        self.file_path = file_path

    def read_csv(self):
        """Reads the CSV file and returns its content as a list of dictionaries."""
        try:
            with open(self.file_path, mode='r', newline='', encoding='utf-8') as file:
                reader = csv.DictReader(file, delimiter=';')
                return [row for row in reader]
        except FileNotFoundError:
            print(f"File not found: {self.file_path}")
            return []
        except Exception as e:
            print(f"An error occurred while reading the file: {e}")
            return []

    def write_csv(self, header, data, fieldnames):
        """
        Writes data to the CSV file.
        
        Args:
            data (list of dict): The data to write to the file.
            fieldnames (list of str): The header row for the CSV file.
        """
        try:
            with open(self.file_path, mode='w', newline='', encoding='utf-8') as file:
                writer = csv.DictWriter(file, fieldnames=fieldnames, delimiter=';')
                writer.writerows(header)
                writer.writerows(data)
        except Exception as e:
            print(f"An error occurred while writing to the file: {e}")