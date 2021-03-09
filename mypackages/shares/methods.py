


def main():
    
    mystock = margin()['Code']
    mylist = createString(mystock)
    df = dlYahoo(mylist)
    return df


def margin():
    import pandas as pd
    # new code to pick up from csv instead with more details
    mycsv = 'https://raw.githubusercontent.com/RonnyCh/mydsbook/master/margin.csv'
    mycsv = pd.read_csv(mycsv)
    mycsv = mycsv[['ASX Code','Security Name','LVR','Industry','Valuation']]
    mycsv = mycsv.rename(columns = {'ASX Code':'Code'})
    
    # add some indexes and other codes manually here
    lastrow = mycsv.shape[0]
    addList = ['^AORD','^DJI','^FTSE','CL=F','Z1P.AX']
    addName = ['Ordinaries','Dow Jones','Footsie','Petrol','ZIP Payment']

    for i, desc in enumerate(addList):
        mycsv.loc[lastrow+i,'Code'] = desc
        mycsv.loc[lastrow+i,'Security Name'] = addName[i]
        mycsv.loc[lastrow+i,'LVR'] = 0
        mycsv.loc[lastrow+i,'Industry'] = 'Index'
        mycsv.loc[lastrow+i,'Valuation'] = 0
    
    return mycsv


def createString(mystock):
    # convert to string to make it better with dowloanding tracker
    mystring = ''
    mylist = []
    
    for i in mystock:
        if i in ['^AORD','^DJI','^FTSE','CL=F']:     # indexes no need to add .AX
            mystring = mystring + ' ' + i
            mylist.append(i)
        else:
            mystring = mystring + ' ' + i + '.AX'
            mylist.append(i+'.AX')
    return mylist




def MAC(MACD,Trigger,MACDiff,Movement,Vol):
    
    # rule 1 looking for buying point (MACDiff trending up - positive)
    
    if MACD >= Trigger:   # logic for MACD > Trigger
        if MACD <= 0:     # below x axis (negative MACD) 
            action = 'Buy Confirm'
        elif MACD > 0:    # above x axis (positive MACD)  
            if MACDiff > 0:
                action = 'Hold'
            else:
                action = 'Time to Sell'
    elif MACD < Trigger:  # logic for MACD < Trigger
        if MACD <=0:      # below x axis (negative MACD)
            if MACDiff > 0:
                action = 'Buy Accumulate'
            elif Movement > 0 and Vol > 0:
                action = 'Market Buying'
            else:
                action = 'Time to Sell'
        elif MACD > 0:    # above x axis (positive MACD)
            if MACDiff > 0:
                action = 'Hold'
            elif Movement < 0 and Vol > 0:
                action = 'Market Selling'
            else:
                action = 'Time to Sell'
    else:
        action='Nothing'
            
    return action




def dlYahoo(mylist):
    import yfinance as yf
    import pandas as pd
    
    # download data 
    data = yf.download(mylist, start='2021-03-1', end='2021-03-9', group_by="ticker")

    # create columns for dataframe and the dataframe itself
    mycol = []
    mytbl = pd.DataFrame(columns=mycol)


    # looping through the list to modify table
    for i in mylist:
        #df = web.DataReader(i, 'yahoo', start, end)[['Close','Volume']]    # old code using datareader (not working well)
        #df = yf.download(i, start=start, end=end)[['Close','Volume']]      # old Yfinance code

        df = data[i][['Close','Volume']]     # new one using Yfinance
        df['Code'] = i
        ma_day = [5, 10, 30]    # avg using 5, 10 and 30 days
        for ma in ma_day:
            column_name = f"Avg-{ma}days"
            df[column_name] = df['Close'].ewm(span=ma).mean()
        df['P/30Days'] = df['Close']/df['Avg-30days']
        df['Mov-3Days'] = df['Close'].diff(1)
        df['MACD'] = df.iloc[:,3] - df.iloc[:,4]    # column 5 - columns 4 (Long - Short Avg)    
        df['Trigger'] = df.MACD.rolling(window=3).mean()
        df['MACD_Diff'] = df['MACD'].diff(1)
        df['Vol_Diff'] = df['Volume'].diff(1)
        df['Advice'] = df.apply(lambda x:MAC(x['MACD'],x['Trigger'],x['MACD_Diff'],x['Mov-3Days'],x['Vol_Diff']),axis=1)
        mytbl = mytbl.append(df)
       


    # Tidy Up the table by dropping null values for close
    mytbl = mytbl.dropna(subset=['Close'])
    mytbl = mytbl.reset_index()
    mytbl = mytbl.rename(columns={'index':'Date'})
    return mytbl