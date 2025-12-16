class ETL:
    def __init__(self, source,destination):
        self.source = source
        self.destination = destination
    def extract(self):
        try:
            with open(self.source, 'r') as file:
                data = file.read()
            return data
        except Exception as e:
            print(f"Error reading file: {e}")
            return None
    def transform(self, data):
        if data:
            transformed_data = data.lower()
            return transformed_data
        return None
    def load(self, data, destination):
        try:
            with open(destination, 'w') as file:
                file.write(data)
            print("Data loaded successfully.")
        except Exception as e:
            print(f"Error writing to file: {e}")
if __name__ == "__main__":
    etl = ETL('source.txt', 'destination.txt')
    data = etl.extract()
    transformed_data = etl.transform(data)
    etl.load(transformed_data, etl.destination)