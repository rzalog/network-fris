import signal
import time
import socket, sys
from SF_9DOF import IMU

HOST, PORT = "169.232.241.140", 8080

SYS_TICK_TIME = .05
NUM_GYRO_TICKS = 20
START_THROW_THRESHOLD = 20
END_THROW_THRESHOLD = 20
FREQ_THRESHOLD = 0.5

gyroThrowReadings = []
curGyroReadingIndex = 0

oldIsThrowing = False
isThrowing = False
isThrowingCounter = 0

curTimeStamp = time.time()

allThrows = []

# Gyro stuff
imu = IMU()

# Network stuff

class Throw:
	def __init__(self, gyroReadings, timestamp):
		self.gyroReadings = list(gyroReadings)	# Gyro readings are in Hz
		self.timestamp = timestamp
		self.dt = SYS_TICK_TIME

def initGyro():
	imu.initialize()
	imu.enable_gyro()
	imu.gyro_range('245DPS')
	return

def systick(s, f):
	gyroReading = getGyroReading()

	if not isThrowing:
		if gyroReading > FREQ_THRESHOLD:
			isThrowingCounter += 1
			if isThrowingCounter >= START_THROW_THRESHOLD:
				startThrow()
				isThrowingCounter = 0
		else:
			isThrowingCounter = 0
	elif isThrowing:
		if gyroReading < FREQ_THRESHOLD:
			isThrowingCounter += 1
			if isThrowingCounter >= END_THROW_THRESHOLD:
				endThrow()
				isThrowingCounter = 0
		else:
			isThrowingCounter = 0

		gyroThrowReadings[curGyroReadingIndex] = gyroReading
		curGyroReadingIndex += 1

	oldIsThrowing = isThrowing

def setupInterrupt():
	signal.signal(signal.SIGALRM, systick)
	signal.setitimer(signal.ITIMER_REAL, SYS_TICK_TIME, SYS_TICK_TIME)

def getGyroReading():
	imu.read_gyro()
	return imu.gz / 360.0

def startThrow():
	isThrowing = True
	gyroThrowReadings = []
	curTimeStamp = time.time()

def endThrow():
	isThrowing = false

	throw = Throw(gyroThrowReadings, curTimeStamp);
	allThrows.append(throw)

	sendThrowData(throw)

def sendThrowData():
	signal.setitimer(signal.ITIMER_REAL, 0, 0)

	data = 'hello'

	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

	sock.connect( (HOST, PORT) )
	sock.sendall(data + '\n')

	sock.close()

	signal.setitimer(signal.ITIMER_REAL, SYS_TICK_TIME, SYS_TICK_TIME)

if __name__ == "__main__":
	initGyro()
	setupInterrupt()
	while True:
		if oldIsThrowing and not isThrowing:
			sendThrowData()
			oldIsThrowing = isThrowing