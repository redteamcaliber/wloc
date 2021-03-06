#!/usr/bin/env python2


def conv_strength(stp):
    # Converting strength percents to RSSI (dBm)...
    return '%.0f' % (stp / 2 - 100)


def fetch_networks():
    # Importing Network Manager from GI repository and other modules...
    import gi, warnings
    gi.require_version('NetworkManager', '1.0')
    gi.require_version('NMClient', '1.0')
    from gi.repository import NetworkManager, NMClient

    # Creating new list for networks...
    netlist = []

    # Ignoring warnings on new Python versions...
    warnings.filterwarnings('ignore')

    # Connecting to Network Manager...
    nmclient = NMClient.Client.new()
    nmdevices = nmclient.get_devices()

    # Retrieving available networks...
    for nmdevice in nmdevices:
        if nmdevice.get_device_type() == NetworkManager.DeviceType.WIFI:
            for accesspoint in nmdevice.get_access_points():
                netlist.append([accesspoint.get_bssid(), conv_strength(accesspoint.get_strength())])

    # Returning result...
    return netlist


def query_yandex():
    # Importing required modules...
    import xml.etree.cElementTree as et
    import requests as rq

    # Setting constants...
    apikey = ''
    apiuri = 'https://api.lbs.yandex.net/geolocation'

    # Generating base XML structure...
    xml = et.Element('ya_lbs_request')

    # Filling API Keys...
    common = et.SubElement(xml, 'common')
    et.SubElement(common, 'version').text = '1.0'
    et.SubElement(common, 'api_key').text = apikey

    # Creating wifi_networks element...
    networks = et.SubElement(xml, 'wifi_networks')

    # Retrieving available networks...
    for arr in fetch_networks():
        network = et.SubElement(networks, 'network')
        et.SubElement(network, 'mac').text = arr[0]
        et.SubElement(network, 'signal_strength').text = arr[1]

    try:
        # Sending our XML file to API...
        r = rq.post(apiuri, data={'xml': et.tostring(xml, 'utf8')})

        # Parsing XML response...
        result = et.fromstring(r.content).findall('./position/')

        # Returning result...
        return [result[0].text, result[1].text]

    except:
        # Exception detected...
        print('Server returned code: %s.\n\nRaw output:\n%s\n' % (r.status_code, r.text))


def main():
    try:
        # Querying Yandex...
        coords = query_yandex()

        # Showing result...
        print('Latitude: %s\nLongitude: %s\n' % (coords[0], coords[1]))

    except:
        # Exception detected...
        print('An error occurred while querying backend.')


if __name__ == '__main__':
    main()
