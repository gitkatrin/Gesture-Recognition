# self.public
# self._protected
# self.__private


class everythingThatDrives:
    def __init__(self, driverName, location, id):
        self.driverName = driverName
        self.location = location    # Tupel Long, Lat
        self.id = id
        print("driverName: ", driverName, " location: ",
              location, " id: ", id)

    def updateValues(self, driverName=None, location=None, isFree=None):
        # Prevents the values from beeing overridden with none
        if driverName != None:
            self.driverName = driverName
            print("Driver Name is now:", driverName)
        if location != None:
            self.location = location            # Tupel Long, Lat
            print("Location is now:", location)
        if isFree != None:
            self.isFree = isFree
            print("The isFree state is now: ", isFree)


class Ambulance(everythingThatDrives):
    def __init__(self, driverName, location, isFree, id):
        super().__init__(driverName, location, id)
        self.isFree = isFree
        print("New Ambulance generated!")


class Firefighter(everythingThatDrives):
    def __init__(self, driverName, location, isFree, id):
        super().__init__(driverName, location, id)
        self.isFree = isFree
        print("New Firefighter generated!")


class Police(everythingThatDrives):
    def __init__(self, driverName, location, isFree, id):
        super().__init__(driverName, location,  id)
        self.isFree = isFree
        print("New Police generated!")


class userCar(everythingThatDrives):
    def __init__(self, driverName, location, reasons, id):
        super().__init__(driverName, location,  id)
        self.reasons = reasons
        print("Reason: ", reasons)
        print("New userCar generated!")

    def updateValues(self, reasons=None, driverName=None, location=None):
        if reasons != None:
            self.reasons = reasons
            print("Reason is : ", reasons)
        if driverName != None:
            self.driverName = driverName
            print("Driver Name is now:", driverName)
        if location != None:
            self.location = location            # Tupel Long, Lat
            print("Location is now:", location)


class Hospital:
    def __init__(self, hospitalName, location, doctors, id, freeRooms, specialists):
        self.hospitalName = hospitalName
        self.location = location        # Tupel Long, Lat
        self.doctors = doctors          # list
        self.specialists = specialists  # list
        self.freeRooms = freeRooms      # int
        self.id = id                    # string
        print("New Hospital generated!")
        print("HospitalName: ", hospitalName, " location: ",
              location, " Doctors: ", doctors, " id: ", id, " freeRooms: ", freeRooms, " specialists: ", specialists)

    def updateValues(self, hospitalName=None, doctors=None, specialists=None, freeRooms=None, id=None):
        if hospitalName != None:
            self.hospitalName = hospitalName
            print("Hospitalname is: ", hospitalName)
        if doctors != None:
            self.doctors = doctors          # list
            print("New Number of Doctors is: ", doctors)
        if specialists != None:
            self.specialists = specialists  # list
            print("Specialists avaiable are: ", specialists)
        if freeRooms != None:
            self.freeRooms = freeRooms
            print("There are : ", freeRooms, " free rooms")