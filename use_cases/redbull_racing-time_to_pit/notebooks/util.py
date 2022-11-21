import pandas as pd
import numpy as np
import json

def historical_json_file_to_DF(input_file_name, ouput_file_name):

    # Opening JSON file
    f = open(input_file_name)
  
    # returns JSON object as a dictionary
    jsonStr = json.load(f)

    ses_num = 0
    df = []

    for evnt in jsonStr['events']: 
        for ses in evnt['sessions']:
    #         print('ses_number= ',ses_num,'\n')
            ses_num+=1
            for ii in range(len(ses['drivers']) ):
                info = ses['drivers'][ii]['info']
    #             print(info,'\n')
                for jj in range(len(ses['drivers'][ii]['runs'])):
                    tyres = ses['drivers'][ii]['runs'][jj]['tyres']
                    laps = ses['drivers'][ii]['runs'][jj]['laps']
    #                 print('tyers',ii, jj,'\n', tyres,'\n')
    #                 print('laps',ii,jj,'\n', laps,'\n')
                    for kk in range(0,len(laps)):
                        lp_tm = np.nan
                        if laps[kk]['lapTime']!=None:
                            lp_tm = laps[kk]['lapTime']['time']
                        df.append([evnt['name'], ses['name'],
                                   evnt['name'][0:2], evnt['name'][2:-2], evnt['name'][-2:],
                                   info['fullName'], 
                                   tyres['type'],tyres['compound'],tyres['condition'],tyres['setNumber'],
                                   laps[kk]['lapNumber'], laps[kk]['lapType'], laps[kk]['runLapNumber'],lp_tm, laps[kk]['lapTime'],
                                   laps[kk]['sector1Time'], laps[kk]['sector2Time'], laps[kk]['sector3Time'], laps[kk],
                                   info, tyres,laps]) 

    df = pd.DataFrame(df, columns=['events','sessions',
                                   'year1','country', 'year2',
                                   'drivers_name', 
                                   'tyres_type', 'tyres_compond','tyres_condition','setNumber',
                                   'lapNumber', 'lapType','runLapNumber','lapTime','lapTimeDic',
                                   'sector1Time','sector2Time', 'sector3Time',
                                   'laps_details',
                                   'driver_info','tyers','laps'])

    df.to_csv(ouput_file_name,index=False)
    return df