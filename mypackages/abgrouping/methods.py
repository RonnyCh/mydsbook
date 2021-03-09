
def main(a):
   
    # main function to run others step by step
    user = userTbl(a)
    csv = getCSV()
    
    # add new group
    tbl = add(user)
    csv = csv.append(tbl)
    
    # remove all
    csv = removeAll(csv,user)
    
    # remove parent
    csv = removeParent(csv,user)
    csv = removeBoth(csv,user)
    
    return csv

def userTbl(a):
    # get parameters from users
    from pandas import DataFrame
    usertbl = DataFrame(a)
    usertbl.columns=(['Action','Element','Parent'])
    return usertbl

def getCSV():
    import pandas as pd
    df = pd.read_csv(r'H:\Desktop\AB Detail Reporting Centre.csv')
    #df.to_csv(r'H:\Desktop\AB Detail Reporting Centre Prior Month.csv')
    new = df.dropna(how='all')   # remove all blank rows
    new = new[new['Action']!='Unwind']     # remove previous unwind
    return new

def add(user):
    # add new grouping 
    import pandas as pd
    pd.set_option('mode.chained_assignment',None)
    add = user[user['Action']=='Add']
    add['Element Type'] = 'C'
    add['Weighting'] = 1
    return add

def removeAll(new,usertbl):
    #pd.set_option('mode.chained_assignment',None)
    # remove the whole grouping, new = the csv table and usertbl  = user parms
    mylist = usertbl[(usertbl['Parent'] != '*') & (usertbl['Element'] == '*')]['Parent'].tolist()
    remove = new[(~new['Parent'].isin(mylist)) & (~new['Element'].isin(mylist))]  # not in
    unwind = new[(new['Element'].isin(mylist)) | (new['Parent'].isin(mylist)) ]   # is in
    unwind.loc[:,'Action'] = 'Unwind'
    unwind.dropna(subset=['Parent'],inplace=True)
    new = remove.append(unwind)
    return new


def removeParent(new,usertbl):
    # this is how to remove parent keys and create unwind
    mylist = usertbl[(usertbl['Parent'] == '*') & (usertbl['Element'] != '*')]['Element'].tolist()
    remove = new[~new['Element'].isin(mylist)]
    unwind = new[new['Element'].isin(mylist)]
    unwind.loc[:,'Action'] = 'Unwind'
    new = remove.append(unwind)
    return new


def removeBoth(new,usertbl):
    # this is removing specific elements to specific grouping
    mylist = usertbl[(usertbl['Parent'] != '*') & (usertbl['Element'] != '*') & (usertbl['Action'] == 'Remove')]
    remove = new[~new['Element'].isin(mylist['Element'])]
    unwind = new[new['Element'].isin(mylist['Element'])]
    unwind.loc[:,'Action'] = 'Unwind'
    new = remove.append(unwind)
    return new

