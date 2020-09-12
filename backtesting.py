import csv
import MACD as macd
import State as st
import Technical_indicators as ti
from cassandra.cluster import Cluster
import numpy as np
"""
                        ---BackTesting---
This script is ment for testing if we are generating Correct Values of Different
Signals and Indicators

Just Comment out the unnecessary parts of the script and product results in an csv file

use this when you want to cross check multiple Indicator as well as Candle Values values
            

"""
cluster = Cluster()
session = cluster.connect('try1')
candle_type='Time'
start_date='2018-02-01'
end_date='2018-02-03'
date_start='2018-02-01'
date_end='2018-02-03'
product='FGBLH8'
keyspace_name='try1'
f=open('I:\YASH\Instructions\results\backtesting_Emacd_volume.csv','w')
#macd
#volume=[]
#MACD_Class_Object=macd.MACD()
#MACD_Values=MACD_Class_Object.MAcalculation([5,5,13,9],candle_type,date_start,date_end,product,keyspace_name,session)
#for item in MACD_Values:
    #stri=str(item.period.date1)+' '+str(item.period.time_start)+','+str(item.period.open1)+','+str(item.period.high)+','+str(item.period.low)+','+str(item.period.close)+','+str(item.esp)+'\n'
    #volume.append(item.period.volume)
    #f.write(stri)
#f.close()
#print volume
#print np.array(volume)
#State
#h=st.State()
#state_data=h.state_main(1,candle_type,date_start,date_end,product,keyspace_name)

#BB
obj=ti.Tech_indicator()
data=obj.calculation(3,'get_volume_slow_ema.txt',session)
for item in data:
    stri=str(item.period.date1)+' '+str(item.period.time_start)+','+str(item.ema)+'\n'
    #print item.period.time_start,item.period.time_end,item.ema
    f.write(stri)
f.close()
#for item in MACD_Values:
    #stri=str(item.period.date1)+' '+str(item.period.time_start)+','+str(item.period.open1)+','+str(item.period.high)+','+str(item.period.low)+','+str(item.period.close)+','+str(item.emacd1)+'\n'
    #f.write(stri)
#print 'Done!!'

#for item in state_data:
    #stri=str(item.period.date1)+' '+str(item.period.time_start)+','+str(item.period.open1)+','+str(item.period.high)+','+str(item.period.low)+','+str(item.period.close)+','+str(item.state)+'\n'
    #f.write(stri)

print "Done"
