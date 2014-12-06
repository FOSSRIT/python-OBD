
import obd
from obd.utils import Response
from obd.commands import OBDCommand
from obd.decoders import noop


def test_is_connected():
	o = obd.Obd("/dev/null")
	assert not o.is_connected()

	# todo


def test_query():
	# we don't need an actual serial connection
	o = obd.Obd("/dev/null")
	# forge our own command, to control the output
	cmd = OBDCommand("", "", "01", "23", 2, noop)

	# forge IO from the car by overwriting the get/send functions
	
	# buffers
	toCar = [""] # needs to be inside mutable object to allow assignment in closure
	fromCar = ""

	def send(cmd):
		toCar[0] = cmd

	o.is_connected = lambda *args: True
	o.port.send = send
	o.port.get = lambda *args: fromCar

	# make sure unsupported commands don't send
	fromCar = "41 23 AB CD\r\r"
	r = o.query(cmd)
	assert toCar[0] == ""
	assert r.is_null()

	# a correct command transaction
	fromCar = "41 23 AB CD\r\r"  # preset the response
	r = o.query(cmd, force=True)       # run
	assert toCar[0] == "0123"    # verify that the command was sent correctly
	assert r.raw_data == fromCar # verify that raw_data was stored in the Response
	assert r.value == "ABCD"     # verify that the response was parsed correctly

	# response of greater length
	fromCar = "41 23 AB CD EF\r\r"
	r = o.query(cmd, force=True)
	assert toCar[0] == "0123"
	assert r.raw_data == fromCar
	assert r.value == "ABCD"

	# response of greater length
	fromCar = "41 23 AB\r\r"
	r = o.query(cmd, force=True)
	assert toCar[0] == "0123"
	assert r.raw_data == fromCar
	assert r.value == "AB00"

	# NO DATA response
	fromCar = "NO DATA"
	r = o.query(cmd, force=True)
	assert r.raw_data == fromCar
	assert r.is_null()

	# malformed response
	fromCar = "totaly not hex!@#$"
	r = o.query(cmd, force=True)
	assert r.raw_data == fromCar
	assert r.is_null()

	# no response
	fromCar = ""
	r = o.query(cmd, force=True)
	assert r.raw_data == fromCar
	assert r.is_null()


def test_load_commands():
	pass
