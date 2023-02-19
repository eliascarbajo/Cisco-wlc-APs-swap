# Cisco-wlc-APs-swap
### Cisco Catalyst 9800 Wireless.  Swapping APs between primary and secondary controllers.
    Python script connecting through netconf to Cisco Catalyst 9800 controllers.
    Configure the primary a secondary controllers on selected APs, in order to 
    move APs between both controllers.

    Tested with IOS-XE 17.6.4 ,  executing out the box with python 3.6 , and 
    also tested inside Catalyst 9800, using GUESTSHELL (python 3.8)

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
