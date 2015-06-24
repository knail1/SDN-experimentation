if __name__ == '__main__':

    dpid='00-00-00-00-00-01'
    destMac='00:00:00:00:00:03'
    destPort='80'

    portmap = {
                ('00-00-00-00-00-01', '00:00:00:00:01:01', '00:00:00:00:00:03', 80): '00-00-00-00-00-03',
                ('00-00-00-00-00-01', '00:00:00:00:01:55', '00:00:00:00:00:99', 80): '00-00-00-00-00-03',
                }
    thisTuple = ('00-00-00-00-00-01', '00:00:00:00:01:01', '00:00:00:00:00:03', 80)

    #print portmap[thisTuple]
    print portmap




'''  for row in returnedList:
        if ((row[1] == dangerSource) & (row[2] == dangerDest)):
            print "we have a problem"
            print row[1] , row[2]
'''