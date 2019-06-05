import pandas as pd


class CoagmetData:
    
    def __init__(self, df=None):
        self.df = df
        
    def columns(self):
        return self.df.columns.tolist()
        
    def get(self, columns=None):
        if columns:
            return self.df[columns]
        else:
            return self.df
    
    def request(self):
        raise NotImplementedError
    
    def read_csv(self, filename, *args, **kwargs):
        self.df = pd.read_csv(filename, *args, **kwargs)
    
    def to_csv(self, filename, *args, **kwargs):
        self.df.to_csv(filename, *args, **kwargs)
