class Transform:
    def __init__(self, df):
        self.df = df

    def data_cleaning(self):
        shape1 = self.df.shape[0]
        data=self.df.drop_duplicates()
        data=data.dropna()
        data.reset_index(drop=True, inplace=True)
        shape2 = data.shape[0]
        if (shape1 - shape2)/shape1 > 0.1:
            print(f"Warning: {(shape1 - shape2)*100/shape1} % of the data was removed during cleaning.")
        print(f"Data cleaned: {(shape1 - shape2)*100/shape1} % rows removed.")
        return data
    def outlier_treatment(self):
        data=self.data_cleaning()
        numeric_columns = data.select_dtypes(include=['number']).columns
        for column in numeric_columns:
            data = self._treat_outliers_iqr(data, column)
        return data
    def _treat_outliers_iqr(self, data, column):
        Q1 = data[column].quantile(0.25)
        Q3 = data[column].quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        before_rows = data.shape[0]
        data = data[(data[column] >= lower_bound) & (data[column] <= upper_bound)]
        after_rows = data.shape[0]
        print(f"Outlier treatment on '{column}': {(before_rows - after_rows)*100/before_rows} % rows removed.")
        return data
    def normalization(self):
        data=self.outlier_treatment()
        numeric_columns = data.select_dtypes(include=['number']).columns
        for column in numeric_columns:
            min_val = data[column].min()
            max_val = data[column].max()
            data[column] = (data[column] - min_val) / (max_val - min_val)
        print("Normalization completed using Min-Max scaling.")
        return data