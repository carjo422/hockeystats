import pandas as pd

def evaluate_scoring_model(indata):

    ev = [[0] * 3 for i in range(15)]

    for j in range(0,15):
        ev[j][0]=j/100+1/100

    for i in range(0,len(indata)):

        for j in range(0,15):



            if float(j)/100 < indata.iloc[i][0] and indata.iloc[i][0] < float(j+1)/100:
                ev[j][1] += 1
                ev[j][2] += indata.iloc[i][1]


    evd = pd.DataFrame(ev, columns = ['exp','n','act'])

    evd['act%'] = evd['act']/evd['n']
    evd['err'] = (evd['act%'] - evd['exp'])**2


    print(evd)

    print(evd['err'].sum())

