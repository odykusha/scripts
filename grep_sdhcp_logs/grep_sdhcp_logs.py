# -*- coding: utf-8 -*-
# grep sdhcp logs
# supported python 2.7, not supported python > 3.0
# how to run: grep_sdhcp_logs.py [file_name] [find_word]
# example: grep_sdhcp_logs.py dhcp_2015-05-21_1.log ff:11:22:33:45:21
import sys
import datetime
import time
import binascii
import xml.etree.ElementTree as ET

version = 'v. 1.4'

dhcp_type_dict = {1: '[1]DHCP Discover',
                  2: '[2]DHCP Offer',
                  3: '[3]DHCP Request',
                  4: '[4]DHCP Decline',
                  5: '[5]DHCP Ack',
                  6: '[6]DHCP Nak',
                  7: '[7]DHCP Release',
                  8: '[8]DHCP Inform'}


try:
    File_name = sys.argv[1]
except IndexError:
    File_name = 'dhcp_2015-05-15_0.log'    # input('Enter file name: ')
except:
    print('file {0}, exists').format(sys.argv[1])
    time.sleep(3)
    sys.exit()

try:
    Find_word = sys.argv[2]
except IndexError:
    Find_word = 'ff:11:22:33:45:21'    #input('Enter find word: ')  # 'ISKRATEL:cg-ngn-2-ik-9526 atm 8/38:'
except:
    print('find word exists')
    time.sleep(3)
    sys.exit()


print('Parsing started...')
start_time = datetime.datetime.now()


###############################################################################
def get_value(word, left_symb, right_symb):
    return word[word.find(left_symb) + len(left_symb):
                word.find(right_symb,
                word.find(left_symb) + len(left_symb))]


# parsing
def parsing(cache):
    pars = {}
    pars['date'] = cache.split(' : ')[0]

    pars['type_cache'] = get_value(cache, '] : ', ': {')
    pars['xid'] = get_value(cache, 'xid: ', ',')

    if 'type' in cache:
        pars['type_dhcp'] = dhcp_type_dict[int(get_value(cache, 'type: ', ','))]

    pars['mac'] = get_value(cache, 'mac: ', ',')
    pars['ciaddr'] = get_value(cache, 'ciaddr: ', ',')
    pars['yiaddr'] = get_value(cache, 'yiaddr: ', ',')
    pars['giaddr'] = get_value(cache, 'giaddr: ', ',')

    if 'lease' in cache:
        pars['lease'] = get_value(cache, 'lease: ', ',')

    # dhcp options
    if 'DNS_Server' in cache:
        pars['DNS_Server'] = get_value(cache, 'DNS_Server(6): [', '], ')

    if 'SubNet_Mask' in cache:
        pars['SubNet_Mask'] = get_value(cache, 'SubNet_Mask(1): ', ',')

    if 'Router' in cache:
        pars['Router'] = get_value(cache, 'Router(3): ', ',')

    # opt_82
    opt_82 = get_value(cache, 'Relay_Agent_Info(82): ', '}}')

    original_cid = opt_82.split(',')[0].split(': ')[1]
    opt82_in_ascii = binascii.unhexlify(original_cid)
    pars['Relay_Agent_Info'] = opt_82.replace(original_cid, opt82_in_ascii)
    return pars


###############################################################################
Parsing_logs = []
for line in open(File_name):
    if Find_word in line or binascii.hexlify(Find_word) in line:
        Parsing_logs.append(parsing(line))


Find_time = (datetime.datetime.now() - start_time).total_seconds()
print('Parsing stopped....{0}s').format(Find_time)
print('Finded {0} contains').format(len(Parsing_logs))
print('Save stared...')
start_time = datetime.datetime.now()


###############################################################################
# saving in XML
root = ET.Element('root')
root.set('version', str(version))
root.append(ET.Comment('Grep sdhcp logs'))
root.append(ET.Comment('File created: ' + str(datetime.datetime.now())))
root.append(ET.Comment('Original file name: ' + File_name))
root.append(ET.Comment('Find in file: ' + Find_word + '.'))
root.append(ET.Comment('Find time: ' + str(Find_time) + 's'))

for par in Parsing_logs:
    options = ET.SubElement(root, 'cache', date=par['date'])

    ET.SubElement(options, 'type_cache').text = par['type_cache']
    ET.SubElement(options, 'xid').text = par['xid']
    if 'type_dhcp' in par:
        ET.SubElement(options, 'type_dhcp').text = par['type_dhcp']
    ET.SubElement(options, 'mac').text = par['mac']
    ET.SubElement(options, 'ciaddr').text = par['ciaddr']
    ET.SubElement(options, 'yiaddr').text = par['yiaddr']
    ET.SubElement(options, 'giaddr').text = par['giaddr']
    if 'lease' in par.keys():
        ET.SubElement(options, 'lease').text = par['lease']

    options_dhcp = ET.SubElement(options, 'DHCP_options')
    if 'DNS_Server' in par.keys():
        ET.SubElement(options_dhcp, 'DNS_Server').text = par['DNS_Server']
    if 'SubNet_Mask' in par.keys():
        ET.SubElement(options_dhcp, 'SubNet_Mask').text = par['SubNet_Mask']
    if 'Router' in par.keys():
        ET.SubElement(options_dhcp, 'Router').text = par['Router']
    ET.SubElement(options_dhcp, 'Relay_Agent_Info').text = par['Relay_Agent_Info']
    options.append(ET.Comment('=' * 100))

with open(File_name.replace('log', 'xml'), 'w') as File_xml:
    ET.ElementTree(root).write(File_xml)


print('Save stopped...{0}s').format((datetime.datetime.now() -
                                   start_time).total_seconds())

time.sleep(5)
