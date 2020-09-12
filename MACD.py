from get_agg import get_agg
#import sys
"""
                                ---MACD---
1. Definations
    1.1 MA
    1.2 MAcalculation
    1.3 showdata
    1.4 showEdata(Exponential)

                            ---Flow Of CODE---
2.1 Configerations are received from trading Script
2.2 GET Aggregated Candles
2.3 Call MA() to calculate MA1,MA2,MACD,SIGNAL,EMA1,EMA2,E-MACD,E-SIGNAL
2.4 Return a list of Objects of MACD class

"""
class MACD():
    
    def __init__(self,period=None,ma1=None,ma2=None,sp=None,macd1=None,ema1=None,ema2=None,emacd1=None,esp=None):
        self.period=period
        #For SMA's
        self.ma1=ma1
        self.ma2=ma2
        self.sp=sp
        self.macd1=macd1
        #for EMA's
        self.ema1=ema1
        self.ema2=ema2
        self.esp=esp
        self.emacd1=emacd1
        
        
    def MA(self,period_data,fast_period,slow_period,signal_period):
        counter_for_ma=0        
        counter_for_macd_list=0
        #constant for multiplying in macd formula
        k1=2.0/(fast_period+1)
        k2=2.0/(slow_period+1)
        k3=2.0/(signal_period+1)
        
        sp=0.0
        ma1=0.0
        ma2=0.0
        
        ema1=0.0
        ema2=0.0

        ema_calculation_signal=0
        ema2_calculation_signal=0
        esp2_calculation_signal=0

        ma2_calculation_list=[0.0]*(slow_period)
        ma_calculation_list=[0.0]*(fast_period)

        Calculated_answer=[]

        tmacd=0.0
        temacd=0
        time_end=''
        macd=[0.0]*(signal_period)
        emacd=[0.0]*(signal_period)    

        counter=0
        counter1=0
        counter3_esp=0
        counter_for_esp_calculaton=0
        
        for current_item in period_data:
            current_close_price=current_item.close
            #keep the list of the size of WINDOW so extra memory is not USED
            ma_calculation_list[counter_for_ma%(fast_period)]=current_close_price
            ma2_calculation_list[counter_for_ma%(slow_period)]=current_close_price            
            """-----------------Simple Moving Average-------------------""" 
            #------------------------------------------------MA1--------------------------------
            if counter_for_ma>=(fast_period-1):
                ma1=sum(ma_calculation_list)/fast_period
                ema_calculation_signal=1
            else:
                ma1=0
          
            #-------------------------------------------MA2-------------------------------
            if counter_for_ma>=(slow_period-1):
                ma2=sum(ma2_calculation_list)/slow_period

                tmacd=ma1-ma2

                time_end=str(current_item.time_end)
                macd[counter_for_macd_list%(signal_period)]=tmacd

                ema2_calculation_signal=1
                counter_for_macd_list=counter_for_macd_list+1
            else:
                ma2=0
            #---------------------------------------Signal--------------------------
            if counter_for_macd_list>=(signal_period-1) and ema2_calculation_signal==1:
                sp=sum(macd)/signal_period
            else:
                sp=0
            """-----------------Exponential Moving Average-------------------"""
            #----------------------------------------EMA1---------------------------
            if ema_calculation_signal==1:
                #for EMA1
                if counter==0:
                   ema1=ma1
                else:
                    ema1=ema1+k1*(current_close_price-ema1)
                counter+=1
            else:
                ema1=0
            #--------------------------------------EMA2-----------------------------
            if ema2_calculation_signal==1:
                #for EMA2
                if counter1==0:
                    ema2=ma2
                else:
                    ema2=ema2+k2*(current_close_price-ema2)
                counter1+=1
                
                temacd=ema1-ema2
                emacd[counter_for_esp_calculaton%signal_period]=temacd
                esp2_calculation_signal=1
                counter_for_esp_calculaton=counter_for_esp_calculaton+1
            else:
                ema2=0
            #----------------------------------E-Signal----------------------------
            if esp2_calculation_signal==1 and counter_for_esp_calculaton>=signal_period:
                if counter3_esp==0:
                    esp=temacd
                else:
                    esp=esp+k3*(tmacd-esp)
                counter3_esp+=1
            else:
                esp=0
            #-----------------------------final ANSWER-----------------------------
            counter_for_ma=counter_for_ma+1
            #print ema1,ema2,tmacd,temacd
            MACD_class_object=MACD(current_item,ma1,ma2,sp,tmacd,ema1,ema2,temacd,esp)
            Calculated_answer.append(MACD_class_object)
        return Calculated_answer            
        
    def showdata(self):
        #self.period.show()
        print"____________________________"
        print 'MA1'
        print self.ma1
        print "MA2"
        print self.ma2
        print "MACD"
        print self.macd1
        print "Signal Value"
        print self.sp
        print "+++++++++++++++++++++++++++"
        
    def showEdata(self):
        #self.period.show()
        print"____________________________"
        print 'EMA1'
        print self.ema1
        print "EMA2"
        print self.ema2
        print "EMACD"
        print self.emacd1
        print "E ignal Value"
        print self.esp
        print "+++++++++++++++++++++++++++"
        
    def MAcalculation(self,data,datatype,date1,date2,pro,kname,session):
        
        period_data=get_agg(data[0],datatype,date1,date2,pro,kname,session)
        Calculated_MA=self.MA(period_data,data[1],data[2],data[3])
        return Calculated_MA
    
        
