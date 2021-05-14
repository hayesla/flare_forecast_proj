from sunpy.net import Fido, attrs as a 


tstart = "2010-01-01"
tend = "2010-01-31"

result = client.search(a.Time(tstart, tend),
                       a.hek.EventType('AR'),
                       a.hek.FRM.Name == 'NOAA SWPC Observer')