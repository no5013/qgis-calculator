import csv
import math

def get_max_pci(row):
    if(row[3] != "" and row[4] != ""):
        max = None
        max_id = None
        for i in range(5, len(row)):
            if(row[i] != ""):
                if((max is None) or (int(row[i]) > int(max))):
                    max = row[i]
                    max_id = i
        if(max != None):
            return max_id

    return False

def format_pci_header(headers):
    format_headers = headers
    for i in range(5, len(headers)):
        splited = headers[i].split('_')
        format_headers[i] = splited[len(splited)-1]
    return format_headers

def find_antenna(pci_id, lat_p, long_p, antenna_list):
    min_distance = None
    min_distance_antenna = None
    for antenna in antenna_list:
        if str(antenna[4]) == str(pci_id):
            distance = distance_between_point(float(antenna[2]), float(antenna[1]), lat_p, long_p)
            if(min_distance is None or distance < min_distance):
                min_distance = distance
                min_distance_antenna = antenna
    return min_distance_antenna

def calculate_rsrp(lat_ant, long_ant, height_ant, freq, lat_p, long_p):
    distance = distance_between_point(lat_ant, long_ant, lat_p, long_p)
    ah = (1.11*math.log10(freq)-0.7)*1-(1.56*math.log10(freq)-0.8)
    lu = 46.3+(33.9*math.log10(freq))-13.82*math.log10(height_ant)+((44.9-6.55*math.log10(1))*math.log10(distance))
    pl = lu-ah
    rsrp = 18.228787 - pl
    return distance

def distance_between_point(lat_ant,long_ant,lat_p,long_p):
    a = math.pow(math.sin(math.fabs(lat_p-lat_ant)*math.pi/180/2),2)+math.cos(lat_ant*math.pi/180)*math.cos(lat_p*math.pi/180)*math.pow(math.sin(math.fabs(long_p-long_ant)*math.pi/180/2),2)
    c = 2*math.atan2(math.sqrt(a), math.sqrt(1-a))
    distance = 6371*c
    return distance

f = open('site data.csv', 'rt', encoding='utf8')
reader = csv.reader(f)
antenna_data = []
index = 0
for row in reader:
    antenna_data.append(row)
    index+=1

f = open('bfa.csv', 'rt', encoding='utf8')
reader = csv.reader(f)
index = 0
headers = []
for row in reader:
    if(index == 0):
        headers = format_pci_header(row)
    else:
        pci_id = get_max_pci(row)
        if(pci_id != False):
            antenna = find_antenna(headers[pci_id], float(row[4]), float(row[3]), antenna_data)
            print(row)
            rsrp = calculate_rsrp(float(antenna[2]), float(antenna[1]), float(antenna[3]), float(antenna[6]), float(row[4]), float(row[3]))
            print(rsrp)
    index+=1
