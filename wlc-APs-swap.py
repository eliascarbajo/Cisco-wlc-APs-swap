"""
    Cisco Catalyst 9800 Wireless.  Swapping APs between primary and secondary controllers.
    Python script connecting through netconf to Cisco Catalyst 9800 controllers.
    Configure the primary a secondary controllers on selected APs, in order to 
    move APs between both controllers.

    Tested with IOS-XE 17.6.4 ,  executing out the box with python 3.6 , and 
    also tested inside Catalyst 9800, using GUESTSHELL (python 3.8).

    Edit this script and modify WLC1 and WLC2 with the names and IPs of your controllers.
    Execute with these options:
    -u : username
    -c : wlc1to2 or wlc2to1 . With wlc1to2 the script connects to WLC1 and 
         configure selected APs with WLC2 as primary and WLC1 as secondary, and opposite
         with option wlc2to1.
    -f : filter for AP selection. You can put the name of an AP, or a regex for selecting
         multiple APs, or .*  for all APS.

    Example:
    python3 wlc-APs-swap.py -c wlc1to2 -u admin -f AProom1-003 

    After executing, it prompts for the password.
"""


__author__ = "Elias Carbajo"
__date__ = "2023/02/19"


import getpass
from argparse import ArgumentParser
from ncclient import manager
import xml.dom.minidom
import lxml.etree as et
import re

###   Edit these 2 lines with your controller's names and IPs. 
WLC1 = ["wlcMadrid","10.22.22.5"]
WLC2 = ["wlcBarcelona","10.33.33.5"]
###

if __name__ == '__main__':
    parser = ArgumentParser(description='Usage:')
    parser.add_argument('-c', '--command', type=str, required=True, help="Command: wlc1to2 or wlc2to1")
    parser.add_argument('-u', '--user', type=str, required=True, help="Netconf User on WLC")
    parser.add_argument('-f', '--ap_filter', type=str, required=True, help="AP Filter: AP name or regexp. For all APs,  use .* ")
    args = parser.parse_args()

    password = getpass.getpass()

    if args.command == "wlc1to2":
        wlc_pri_name = WLC2[0]
        wlc_pri_ip = WLC2[1]
        wlc_sec_name = WLC1[0]
        wlc_sec_ip = WLC1[1]
    elif args.command == "wlc2to1":
        wlc_pri_name = WLC1[0]
        wlc_pri_ip = WLC1[1]
        wlc_sec_name = WLC2[0]
        wlc_sec_ip = WLC2[1]
    else:
        print ("Error")
        exit(1)


    sesion = manager.connect(host=wlc_sec_ip, port=830, username=args.user, password=password, hostkey_verify=False)

    get_ap_list_filter = """
    <filter xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
        <access-point-oper-data xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-wireless-access-point-oper">
            <ap-name-mac-map>
            </ap-name-mac-map>
        </access-point-oper-data>
    </filter>"""

    result = sesion.get(get_ap_list_filter)
    resultxml = xml.dom.minidom.parseString(result.xml)
    ap_list = resultxml.getElementsByTagName("wtp-name")

    print ("Swapping APs:")
    for ap in ap_list:
        ap_name = (ap.firstChild.data)
        if re.search(args.ap_filter,ap_name):
            print (ap_name)

            # format data with f-string to insert the variable between {}
            # first delete secondary because can't coexist same name as primary and secondary

            payload_delete_sec = f"""
                <set-ap-controller xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-wireless-access-point-cfg-rpc">
                  <mode>controller-name-disable</mode>
                  <index>index-secondary</index>
                  <ap-name>{ap_name}</ap-name>
                </set-ap-controller>
                """
            result = sesion.dispatch(et.fromstring(payload_delete_sec))

            payload_config_pri = f"""
                <set-ap-controller xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-wireless-access-point-cfg-rpc">
                  <mode>controller-name-enable</mode>
                  <controller-name>{wlc_pri_name}</controller-name>
                  <index>index-primary</index>
                  <ipaddr>{wlc_pri_ip}</ipaddr>
                  <ap-name>{ap_name}</ap-name>
                </set-ap-controller>
                """
            result = sesion.dispatch(et.fromstring(payload_config_pri))

            payload_config_sec = f"""
                <set-ap-controller xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-wireless-access-point-cfg-rpc">
                  <mode>controller-name-enable</mode>
                  <controller-name>{wlc_sec_name}</controller-name>
                  <index>index-secondary</index>
                  <ipaddr>{wlc_sec_ip}</ipaddr>
                  <ap-name>{ap_name}</ap-name>
                </set-ap-controller>
                """
            result = sesion.dispatch(et.fromstring(payload_config_sec))
