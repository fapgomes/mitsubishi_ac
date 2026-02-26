#!/usr/bin/python3

import requests
import argparse
import sys
from functools import partial
from xmltodict import parse
from xml.etree.ElementTree import Element, SubElement, tostring


# XML Builder

def current_database(data):
    return parse(data)['Packet']['DatabaseManager']

def dict_to_xml_subelement(xml_formatted_dict, element_for_inserting):
    if type(xml_formatted_dict) == type({}) and xml_formatted_dict != {}:

        keys_list = list(xml_formatted_dict.keys())

        for i in keys_list:

            if i[0] == '#':
                if type(element_for_inserting.text) == type(''):
                    element_for_inserting.text += xml_formatted_dict[i]
                else:
                    element_for_inserting.text = xml_formatted_dict[i]

            elif i[0] != '@' and i[0] != '':

                attrib_dict = {}
                if type(xml_formatted_dict[i]) == type({}):
                    keys_list_attrib = list(xml_formatted_dict[i].keys())

                    for k in keys_list_attrib:
                        if k[0] == '@':
                            attrib_dict[k[1:]] = xml_formatted_dict[i][k]

                if attrib_dict != {}:
                    sub_elem = SubElement(element_for_inserting, i, attrib=attrib_dict)
                else:
                    sub_elem = SubElement(element_for_inserting, i)

                if type(xml_formatted_dict[i]) == type({}) and xml_formatted_dict != {}:
                    dict_to_xml_subelement(xml_formatted_dict[i], sub_elem)

    else:
        raise UserWarning("xml_formatted_dict is not a dictionary",
                          xml_formatted_dict)


def create_dict_of_attributes_with_group(group_number, list_of_attributes):
    dict_of_attributes = {'@' + x: '*' for x in list_of_attributes}
    dict_of_attributes['@Group'] = group_number
    return dict_of_attributes

class XmlRequest:
    def __init__(self, request_type, prolog='<?xml version="1.0" encoding="UTF-8"?>'):

        self.xml_prolog = prolog

        if request_type == "get" or request_type == "set":
            self.request_type = request_type
        else:
            raise UserWarning("request type must be set to 'get' or 'set', it was set to " + request_type, request_type)

        self.xml_packet = Element("Packet")
        self.xml_command = SubElement(self.xml_packet, "Command")
        self.xml_command.text = request_type + "Request"
        self.xml_database_manager = SubElement(self.xml_packet, "DatabaseManager")

    def build_full(self):
        return self.xml_prolog + tostring(self.xml_packet).decode()


class XmlGetRequest:
    def __init__(self, database_manager_content={}):
        self.xml_base = XmlRequest(request_type="get")
        dict_to_xml_subelement(database_manager_content, self.xml_base.xml_database_manager)
        self.built = self.xml_base.build_full()

class XmlGetMnetRequest:
    def __init__(self, group_number, list_of_attributes):
        self.dict_of_attributes = create_dict_of_attributes_with_group(group_number=group_number,
                                                                       list_of_attributes=list_of_attributes)
        self.built = XmlGetRequest({"Mnet": self.dict_of_attributes}).built        

class XmlSetRequest:
    def __init__(self, database_manager_content={}):
        self.xml_base = XmlRequest(request_type="set")
        dict_to_xml_subelement(database_manager_content, self.xml_base.xml_database_manager)
        self.built = self.xml_base.build_full()

class XmlSetMnetRequest:
    def __init__(self, group_number, dict_of_attributes):
        self.corrected_dict_of_attributes = {'@' + x: dict_of_attributes[x] for x in dict_of_attributes.keys()}
        self.corrected_dict_of_attributes['@Group'] = group_number
        self.built = XmlSetRequest({"Mnet": self.corrected_dict_of_attributes}).built

class BuiltXml:
    def __init__(self):
        self.get_system_data = XmlGetRequest({"SystemData": {
            "@Version": "*",
            "@TempUnit": "*",
            "@Model": "*",
            "@FilterSign": "*",
            "@ShortName": "*",
            "@DateFormat": "*"
        }}).built

        self.get_area_list = XmlGetRequest({"ControlGroup": {"AreaList": ''}}).built
        self.get_area_group_list = XmlGetRequest({"ControlGroup": {"AreaGroupList": ''}}).built
        self.get_mnet_group_list = XmlGetRequest({"ControlGroup": {"MnetGroupList": ''}}).built
        self.get_mnet_list = XmlGetRequest({"ControlGroup": {"MnetList": ''}}).built
        self.get_ddc_info_list = XmlGetRequest({"ControlGroup": {"DdcInfoList": ''}}).built
        self.get_view_info_list = XmlGetRequest({"ControlGroup": {"ViewInfoList": ''}}).built
        self.get_mc_list = XmlGetRequest({"ControlGroup": {"McList": ''}}).built
        self.get_mc_name_list = XmlGetRequest({"ControlGroup": {"McNameList": ''}}).built
        self.get_function_list = XmlGetRequest({"FunctionControl": {"FunctionList": ''}}).built

    def set_mnet_items(self, group_number, dict_of_items_to_set):
        return XmlSetMnetRequest(group_number=group_number, dict_of_attributes=dict_of_items_to_set).built

    def get_current_drive(self, group_number):
        return XmlGetMnetRequest(group_number=group_number, list_of_attributes=['Drive']).built
    
    def get_current_temperature(self, group_number):
        return XmlGetMnetRequest(group_number=group_number, list_of_attributes=['InletTemp']).built
    
    def get_current_set_temperature(self, group_number):
        return XmlGetMnetRequest(group_number=group_number, list_of_attributes=['SetTemp']).built
    
    def get_current_mode(self, group_number):
        return XmlGetMnetRequest(group_number=group_number, list_of_attributes=['Mode']).built
    

    
    
# HTTP



class SendControllerCommands:
  def __init__(self, url, path="/servlet/MIMEReceiveServlet"):
    self.url = url + path
    self.headers = {'Content-Type': 'text/xml'}

  def post_to_controller(self, post_data):
        response = requests.post(self.url, data=post_data, headers=self.headers)
        return response.text

  def set_current_temperature(self, group_number, temp):
    response = ( self.post_to_controller(
      BuiltXml().set_mnet_items(group_number=group_number, dict_of_items_to_set={"SetTemp": temp})))
    return current_database(response)

  def set_current_mode(self, group_number, mode):
    response = ( self.post_to_controller(
      BuiltXml().set_mnet_items(group_number=group_number, dict_of_items_to_set={"Mode": mode})))
    return current_database(response)

  def set_current_drive(self, group_number, drive):
    response = ( self.post_to_controller(
      BuiltXml().set_mnet_items(group_number=group_number, dict_of_items_to_set={"Drive": drive})))
    return current_database(response)

  def get_current_drive(self, group_number):
    response = ( self.post_to_controller(BuiltXml().get_current_drive(group_number=group_number)))
    return current_database(response)
  
  def get_current_mode(self, group_number):
    response = ( self.post_to_controller(BuiltXml().get_current_mode(group_number=group_number)))
    return current_database(response)

  def get_current_set_temperature(self, group_number):
    response = ( self.post_to_controller(BuiltXml().get_current_set_temperature(group_number=group_number)))
    return current_database(response) 

  def get_current_temperature(self, group_number):
    builtXML = BuiltXml()
    response = ( self.post_to_controller(builtXML.get_current_temperature(group_number=group_number)))
    # print("----------------- SYSTEM DATA-----------------")
    # print(await self.post_to_controller(builtXML.get_system_data))
    # print("------------------- AREA LIST ----------------")
    # print(await self.post_to_controller(builtXML.get_area_list))
    # print("---------------- AREA GROUP LIST --------------")
    # print(await self.post_to_controller(builtXML.get_area_group_list))
    # print("----------------- MNET GROUP LIST -------------")
    # print(await self.post_to_controller(builtXML.get_mnet_group_list))
    # print("------------------- MNET LIST ----------------")
    # print(await self.post_to_controller(builtXML.get_mnet_list))
    # print("------------------- DDC INFO LIST ----------------")
    # print(await self.post_to_controller(builtXML.get_ddc_info_list))
    # print("------------------- VIEW INFO LIST ----------------")
    # print(await self.post_to_controller(builtXML.get_view_info_list))
    # print("------------------- MC LIST ----------------")
    # print(await self.post_to_controller(builtXML.get_mc_list))
    # print("------------------- MC NAME LIST ----------------")
    # print(await self.post_to_controller(builtXML.get_mc_name_list))
    # print("------------------- FUNCTION LIST ----------------") 
    # print(await self.post_to_controller(builtXML.get_function_list)) 
    # print("----------------------------------------------")
    # print(builtXML.get_current_temperature(group_number=group_number))
    return current_database(response)


# AC SCRIPT

def getdrive(ac):
    return sendControllerCommands.get_current_drive(ac)

def getsettemp(ac):
    return sendControllerCommands.get_current_set_temperature(ac)

def gettemp(ac):
    return sendControllerCommands.get_current_temperature(ac)

def getmode(ac):
    return sendControllerCommands.get_current_mode(ac)

def setdrive(param,ac):
    return sendControllerCommands.set_current_drive(ac,param)

def settemp(param,ac):
    return sendControllerCommands.set_current_temperature(ac,param)

def setmode(param,ac):
    return sendControllerCommands.set_current_mode(ac,param)



def cli(ac,method,address,param=""):
    '''
    This script can get/set the Temperature, Mode, Drive (State) of the AC

    MODES AVAILABLE: COOL, DRY, FAN, HEAT, AUTO, HEATRECOVERY,LC_AUTO, BYPASS, AUTOHEAT, AUTOCOOL
  
    Parameters:
    ac (int): Number of the AC - group
    method (string): Permitted Values 
    
    - GETTEMP - Returns current ambient temperature for the AC

    - GETSETTEMP - Returns current set Temperature (Not precise)
    
    - GETSTATE -  Returns the ON/OFF state for the AC
    
    - GETMODE - Returns the MODE that the AC is set

    The set methods need an extra param that is passed in the flag --param

    - SETTEMP - Sets the temperature on the AC 
    
    - SETSTATE - Sets to OFF or ON the AC (Those ones are the only values for --param)
    
    - SETMODE - Sets the Mode of the AC, e.g. COOL

    
    

    Returns:
    string:an informative string

    '''
    functions = {"GETTEMP": gettemp,"GETSETTEMP": getsettemp ,"GETSTATE": getdrive,"GETMODE": getmode, "SETTEMP": partial(settemp,"%s" % param),"SETSTATE": partial(setdrive,param),"SETMODE": partial(setmode,param)}
    method_function = functions[method]
    done = method_function("%s" % ac)
    return done

def check(ac,method,address,w,c):
    '''
    This function is used to integrate the script as a Nagios Plugin

    Parameters:
    param: P
    warning (int): Warning Threshold
    critical (int): Critical Threshold


    '''
    try:
        done = cli(ac,method,address)
        map_method_to_attribute = {"GETTEMP": "@InletTemp", "GETSETTEMP": "@SetTemp"}
        str_temp = done["Mnet"][map_method_to_attribute[method]]
        float_temp = float(str_temp)
        if float_temp >= c:
            print("TEMP CRITICAL: Current temp is " + str_temp + " |temp=" + str_temp)
            sys.exit(2)
        elif float_temp >= w:
            print("TEMP WARNING: Current temp is " + str_temp + " |temp=" + str_temp)
            sys.exit(1)
        elif float_temp < w:
            print("TEMP OK: Current temp is " + str_temp + " |temp=" + str_temp)
            sys.exit(0)
        else:
            print("TEMP UNKNOWN: Could not get data")
    except Exception as e:
        print("TEMP SCRIPT FAILED: " + str(e))
        sys.exit(2) 

def main(args=None):

	parser = argparse.ArgumentParser(prog=__file__)
	parser.add_argument('ac', help='Number of the AC Group')
	parser.add_argument('method', help='Method to use: GETTEMP,GETSETTEMP')
	parser.add_argument('address', help='Hostname or address of the AC IP controller')
	parser.add_argument("-c","--critical",help="Critical Threshold",default=0)
	parser.add_argument("-w","--warning",help="Warning Treshold",default=0)
	args = parser.parse_args()

	global sendControllerCommands
	sendControllerCommands = SendControllerCommands("http://" + args.address)
	check(args.ac,args.method,args.address,int(args.warning),int(args.critical))

if __name__ == "__main__":
	main()
  
