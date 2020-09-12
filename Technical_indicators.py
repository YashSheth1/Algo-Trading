from get_agg import get_agg
import numpy as np
import talib as ta
import matplotlib.pyplot as plt
import ast
"""
1. Bolinger Bands
2. MACD
3. EMA
4. RSI

                          ---Flow of CODE---
1. Call calculation Function
2. Accoording to choice provided in the arguments the technical indicator is selected and its setting are imported frmo the config File
3. TALIB library is used to calculate the Indicator signals which are returned as List of Objects of the class Tech_Indicator

"""
class Tech_indicator():
    def __init__(self,period=None,rsi=None,macd=None,signal=None,macdhist=None,up=None,mid=None,low=None,ema=None):
        self.period=period
        self.macd=macd
        self.signal=signal
        self.macdhist=macdhist
        self.up=up
        self.mid=mid
        self.low=low
        self.ema=ema
        self.rsi=rsi
    
    def calculation(self,choice_of_indicator,data_config,session):
        ans=[]
        config_data={}
        config_data=ast.literal_eval(data_config)
        candle_type=config_data['candle_type']
        date_start=config_data['start_date']
        date_end=config_data['end_date']
        product=config_data['xric']
        keyspace_name=config_data['keyspace_name']
        
        close=[]
        counter=0
        data_timeperiod=int(config_data['data_timeperiod'])
        
        if choice_of_indicator==1:
            print "BB"
            period_data=get_agg(data_timeperiod,candle_type,date_start,date_end,product,keyspace_name,session)
            bolinger=int(config_data['bolinger'])
            for item in period_data:
                close.append(item.close)
    
            up1,mid1,low1=ta.BBANDS(np.array(close),bolinger,nbdevup=int(config_data['nbdevup']), nbdevdn=int(config_data['nbdevdn']),matype=int(config_data['matype']))
               
            for item in period_data:                
                obj=Tech_indicator(item,up=up1[counter],mid=mid1[counter],low=low1[counter])
                ans.append(obj)
                counter+=1
            
            plt.plot(close,color='yellow',label='Market')
            plt.plot(up1,color='blue',label='Upper Band')
            plt.plot(mid1,color='Black',label='Mid Band')
            plt.plot(low1,color='red',label='Lower Band')
            return ans
        if choice_of_indicator==2:
            print "MACD"
            
            period_data=get_agg(data_timeperiod,candle_type,date_start,date_end,product,keyspace_name,session)
            for item in period_data:
                close.append(item.close)
            counter=0
            
            macd1,signal1,macdhist1=ta.MACD(np.array(close),fastperiod=13,slowperiod=5,signalperiod=9)
            for item in period_data:
                obj=Tech_indicator(item,macd=macd1[counter],signal=signal1[counter],macdhist=macdhist1[counter])
                ans.append(obj)
                counter+=1
                
            plt.plot(close,color='red',label='Market')
            plt.plot(macd1,color='blue',label='macd')
            plt.plot(signal1,color='yellow',label='signal')
            return ans
        if choice_of_indicator==3:
            print "EMA"
            
            period_data=get_agg(data_timeperiod,candle_type,date_start,date_end,product,keyspace_name,session)
            timeperiod=int(config_data['timeperiod_candle_volume'])
            for item in period_data:
                close.append(item.volume*1.0)
            #print close
            counter=0
            
            ema1=ta.EMA(np.array(close),timeperiod)
            for item in period_data:
                obj=Tech_indicator(item,ema=ema1[counter])
                ans.append(obj)
                counter+=1
                
            plt.plot(ema1,color='yellow',label='EMA')
            plt.plot(close,color='blue',label='Market')
            return ans
        if choice_of_indicator==4:
            
            period_data=get_agg(data_timeperiod,candle_type,date_start,date_end,product,keyspace_name,session)
            for item in period_data:
                close.append(item.close)

            counter=0

            rsi1=ta.RSI(np.array(close),data_timeperiod)
            for item in period_data:
                obj=Tech_indicator(item,rsi=rsi1[counter])
                ans.append(obj)
                counter+=1
                
            plt.plot(rsi1,color='red',label='RSI')
            plt.plot(close,color='yellow',label='MARKET CLOSE')
            return ans
        else:
            print "Not FOUND"
