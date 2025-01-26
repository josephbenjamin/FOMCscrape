import pandas as pd

def main():
    df = pd.read_csv('FOMC_dates.csv')
    print(df)

if __name__ == '__main__':
    main()