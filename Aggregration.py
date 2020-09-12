"""
                      ----Aggregation---
1. Aggregation Class for storing and object Orienting the Code !!
2. Definations contained: __init__ and show() 
2. __init__ used to store element in the Class Object
3. show() is used to display data in the object of Class

"""
class aggregration():
    l=[]
    candle_type=''
    xric=''
    date1=''
    date2=''
    time_start=''
    time_end=''
    high=0.0
    low=0.0
    close=0.0
    open1=0.0
    marketbuy=0
    marketsell=0
    limitbuy=0
    limitsell=0
    volume=0
    
    def __init__(self,candle_type,xric,date1,date2,time_start,time_end,high,low,open1,close,marketbuy,marketsell,limitbuy,limitsell,volume):
        self.candle_type=candle_type
        self.xric=xric
        self.date1=date1
        self.date2=date2
        self.time_start=time_start
        self.time_end=time_end
        self.high=high
        self.low=low
        self.close=close
        self.open1=open1
        self.marketbuy=marketbuy
        self.marketsell=marketsell
        self.limitbuy=limitbuy
        self.limitsell=limitsell
        self.volume=volume
    def show(self):
        print "Candle Type"
        print self.candle_type
        print "XRIC"
        print self.xric
        print "Date 1"
        print self.date1
        print "Date 2"
        print self.date2
        print "Time Start"
        print self.time_start
        print "Time End"
        print self.time_end
        print "High"
        print self.high
        print "Low"
        print self.low
        print "Open"
        print self.open1
        print "Close"
        print self.close
        print "Market BUY"
        print self.marketbuy
        print "Market SELL"
        print self.marketsell
        print "Limit BUY"
        print self.limitbuy
        print "Limit SELL"
        print self.limitsell
        print "Volume"
        print self.volume
