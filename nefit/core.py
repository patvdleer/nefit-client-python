import base64
import hashlib
import json
from multiprocessing import Event
import logging

from pyaes import AESModeOfOperationECB, Encrypter, Decrypter, PADDING_NONE
from sleekxmpp import ClientXMPP
from sleekxmpp.xmlstream import tostring
from ssl import PROTOCOL_SSLv23

from .exceptions import NefitResponseException

_LOGGER = logging.getLogger(__name__)


class AESCipher(object):
    def __init__(self, magic, access_key, password):
        self.bs = 16
        self.key = hashlib.md5(bytearray(access_key, "utf8") + magic).digest() + \
                   hashlib.md5(magic + bytearray(password, "utf8")).digest()

    def encrypt(self, raw):
        if len(raw) % self.bs != 0:
            raw = self._pad(raw)
        cipher = Encrypter(AESModeOfOperationECB(self.key), padding=PADDING_NONE)
        ciphertext = cipher.feed(raw) + cipher.feed()

        return base64.b64encode(ciphertext)

    def decrypt(self, enc):
        # trying to decrypt empty data fails
        if not enc:
            return ""
        enc = base64.b64decode(enc)
        cipher = Decrypter(AESModeOfOperationECB(self.key), padding=PADDING_NONE)
        decrypted = cipher.feed(enc) + cipher.feed()
        return decrypted.decode("utf8").rstrip(chr(0))

    def _pad(self, s):
        return s + (self.bs - len(s) % self.bs) * chr(0)


class NefitCore(object):
    _accesskey_prefix = 'Ct7ZR03b_'
    _rrc_contact_prefix = 'rrccontact_'
    _rrc_gateway_prefix = 'rrcgateway_'
    _magic = bytearray.fromhex("58f18d70f667c9c79ef7de435bf0f9b1553bbb6e61816212ab80e5b0d351fbb1")

    serial_number = None
    access_key = None
    password = None
    use_ssl = False
    use_tls = False

    jid = None
    _from = None
    _to = None
    client = None
    encryption = None

    event = None
    container = {}

    def __init__(self, serial_number, access_key, password, host="wa2-mz36-qrmzh6.bosch.de", sasl_mech="SCRAM-SHA-1",
                 use_ssl=False, use_tls=False):
        """

        :param serial_number:
        :param access_key:
        :param password:
        :param host:
        :param sasl_mech:
        :param use_ssl:
        :param use_tls:
        """
        serial_number = str(serial_number)
        self.serial_number = serial_number
        self.access_key = access_key
        self.password = password
        self.use_ssl = use_ssl
        self.use_tls = use_tls

        self.encryption = AESCipher(self._magic, access_key, password)

        identifier = serial_number + "@" + host
        self.jid = jid = self._from = self._rrc_contact_prefix + identifier
        self._to = self._rrc_gateway_prefix + identifier

        self.client = ClientXMPP(
            jid=jid,
            password=self._accesskey_prefix + access_key,
            sasl_mech=sasl_mech
        )
        self.client.ssl_version = PROTOCOL_SSLv23
        self.client.add_event_handler("session_start", self.session_start)
        self.client.register_plugin('xep_0199')

    @staticmethod
    def set_verbose():
        import logging
        logging.basicConfig(filename="debug.log", level=logging.DEBUG)

    def message(self, msg):
        if msg['type'] in ('chat', 'normal'):
            headers = msg['body'].split("\n")[:-1]
            body = msg['body'].split("\n")[-1:][0]
            if 'HTTP/1.0 400 Bad Request' in headers:
                return
            response = self.decrypt(body)
            if 'Content-Type: application/json' in headers:
                _LOGGER.debug("response='{}'".format(response))
                response = response.strip()
                if len(response) > 1:
                    response = json.loads(response.strip())
            self.container[id(self.event)] = response
        self.event.set()

    def connect(self, block=False, use_ssl=None, use_tls=None, **kwargs):
        self.client.connect(
            use_ssl=use_ssl if use_ssl is not None else self.use_ssl,
            use_tls=use_tls if use_tls is not None else self.use_tls,
            **kwargs
        )
        self.client.process(block=block)

    def session_start(self, event):
        self.client.send_presence()
        self.client.get_roster()

    def disconnect(self, wait=None, send_close=False):
        self.client.disconnect(reconnect=False, wait=wait, send_close=send_close)

    def force_disconnect(self):
        self.disconnect(wait=False, send_close=False)
        self.client.abort()

    def get(self, uri, timeout=10):
        self.event = Event()
        self.client.add_event_handler("message", self.message)
        self.send("GET %s HTTP/1.1\rUser-Agent: NefitEasy\r\r" % uri)
        self.event.wait(timeout=timeout)
        self.client.del_event_handler("message", self.message)
        if id(self.event) not in self.container.keys():
            raise NefitResponseException("Unable to get %s" % uri)
        return self.container[id(self.event)]

    def put(self, uri, data, timeout=10):
        data = data if isinstance(data, str) else json.dumps(data, separators=(',', ':'))
        encrypted_data = self.encrypt(data).decode("utf8")
        body = "\r".join([
            'PUT %s HTTP/1.1' % uri,
            'Content-Type: application/json',
            'Content-Length: %i' % len(encrypted_data),
            'User-Agent: NefitEasy\r',
            encrypted_data
        ])
        self.event = Event()
        self.client.add_event_handler("message", self.message)
        self.send(body)
        self.event.wait(timeout=timeout)
        self.client.del_event_handler("message", self.message)

    def send(self, body):
        # this horrible piece of code breaks xml syntax but does actually work...
        body = body.replace("\r", "&#13;\n")
        message = self.client.make_message(mto=self._to, mfrom=self._from, mbody=body)
        message['lang'] = None
        str_data = tostring(message.xml, xmlns=message.stream.default_ns,
                            stream=message.stream,
                            top_level=True)
        str_data = str_data.replace("&amp;#13;", "&#13;")
        return message.stream.send_raw(str_data)

    def encrypt(self, data):
        return self.encryption.encrypt(data)

    def decrypt(self, data):
        return self.encryption.decrypt(data)

    def get_display_code(self):
        return self.get('/system/appliance/displaycode')

    def get_status(self):
        return self.get('/ecus/rrc/uiStatus')

    def get_location(self):
        return self.get('/system/location/latitude'), self.get('/system/location/longitude')

    def get_outdoor(self):
        return self.get('/system/sensors/temperatures/outdoor_t1')

    def get_pressure(self):
        return self.get('/system/appliance/systemPressure')

    def get_program(self):
        return (
            self.get('/ecus/rrc/userprogram/activeprogram'),
            self.get('/ecus/rrc/userprogram/program1'),
            self.get('/ecus/rrc/userprogram/program2'),
        )

    def get_year_total(self):
        return self.get('/ecus/rrc/recordings/yearTotal')

    def set_temperature(self, temperature):
        self.put('/heatingCircuits/hc1/temperatureRoomManual', {'value': float(temperature)})
        self.put('/heatingCircuits/hc1/manualTempOverride/status', {'value': 'on'})
        self.put('/heatingCircuits/hc1/manualTempOverride/temperature', {'value': float(temperature)})

    def get_actualSupplyTemperature(self):
        return self.get('/heatingCircuits/hc1/actualSupplyTemperature')


class NefitClient(NefitCore):
    display_codes = {
        '-H': 'central heating active',
        '=H': 'hot water active',
        '0C': 'system starting',
        '0L': 'system starting',
        '0U': 'system starting',
        '0E': 'system waiting',
        '0H': 'system standby',
        '0A': 'system waiting (boiler cannot transfer heat to central heating)',
        '0Y': 'system waiting (boiler cannot transfer heat to central heating)',
        '2E': 'boiler water pressure too low',
        'H07': 'boiler water pressure too low',
        '2F': 'sensors measured abnormal temperature',
        '2L': 'sensors measured abnormal temperature',
        '2P': 'sensors measured abnormal temperature',
        '2U': 'sensors measured abnormal temperature',
        '4F': 'sensors measured abnormal temperature',
        '4L': 'sensors measured abnormal temperature',
        '6A': 'burner doesn\'t ignite',
        '6C': 'burner doesn\'t ignite',
        'rE': 'system restarting',
    }

    def get_display_code(self):
        data = super(NefitClient, self).get_display_code()
        if data['value'] in self.display_codes.keys():
            return self.display_codes[data['value']]
        return "Unknown"

    def get_status(self):
        data = super(NefitClient, self).get_status()
        if data is None:
            return ""
        _LOGGER.debug("get_status/data={}".format(data))
        data.update(data['value'])
        return {
            'user mode': data['UMD'],
            'clock program': data['CPM'],
            'in house status': data['IHS'],
            'in house temp': float(data['IHT']),
            'boiler indicator': {
                'CH': 'central heating',
                'HW': 'hot water',
                'No': 'off'
            }[data['BAI']],
            'control': data['CTR'],
            'temp override duration': float(data['TOD']),
            'current switchpoint': float(data['CSP']),
            'ps active': data['ESI'].lower() == "true",
            'fp active': data['FPA'].lower() == "true",
            'temp override': data['TOR'].lower() == "true",
            'holiday mode': data['HMD'].lower() == "true",
            'boiler block': data['BBE'].lower() == "true",
            'boiler lock': data['BLE'].lower() == "true",
            'boiler maintainance': data['BMR'].lower() == "true",
            'temp setpoint': float(data['TSP']),
            'temp override temp setpoint': float(data['TOT']),
            'temp manual setpoint': float(data['MMT']),
            'hed enabled': data['HED_EN'].lower() == "true",
            'hed device at home': data['HED_DEV'].lower() == "true",
        }

    def get_location(self):
        lat, long = super(NefitClient, self).get_location()
        return lat['value'], long['value']

    def get_outdoor(self):
        data = super(NefitClient, self).get_outdoor()
        return data['value'], data['unitOfMeasure']

    def get_pressure(self):
        data = super(NefitClient, self).get_pressure()
        return data['value'], data['unitOfMeasure']

    def get_program(self):
        data = super(NefitClient, self).get_program()
        return {
            "active_program": data[0]['value']
        }

    def get_actualSupplyTemperature(self):
        data = super(NefitClient, self).get_actualSupplyTemperature()
        return {"actual_temp": data['value']}

    def get_year_total(self):
        data = super(NefitClient, self).get_year_total()
        return data['value'], data['unitOfMeasure']


class NefitClientCli(NefitClient):
    def get_status(self):
        data = super(NefitClientCli, self).get_status()
        s = ""
        for k, v in data.items():
            if isinstance(v, bool):
                s += "%s: %s\n" % (k, "Yes" if v else "No")
            else:
                s += "%s: %s\n" % (k, v)
        return s

    def get_location(self):
        return "Latitude: %s Longitude: %s" % super(NefitClientCli, self).get_location()

    def get_outdoor(self):
        value, unit_of_measure = super(NefitClientCli, self).get_outdoor()
        return "%3.1f %s" % (value, unit_of_measure)

    def get_pressure(self):
        value, unit_of_measure = super(NefitClientCli, self).get_pressure()
        return "%3.1f %s" % (value, unit_of_measure)

    def get_program(self):
        data = super(NefitClient, self).get_program()
        return {
            "active_program": data[0]['value']
        }
