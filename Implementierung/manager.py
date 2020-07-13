import geopy.distance
import paho.mqtt.client as mqtt
import json


def messageHandling(message):
    jsonData = json.loads(message.payload)

    if message.topic.split("/")[2] == "users":
        name = jsonData['driver_name']
        location = jsonData['location']
        id = jsonData['id']
        reasons = jsonData['reasons']
        return name, location, id, reasons

    elif message.topic.split("/")[2] == "hospitals":
        name = jsonData['hospital_name']
        location = jsonData['location']
        id = jsonData['id']
        doctors = jsonData['doctors']
        freeRooms = jsonData['freeRooms']
        specialists = jsonData['specialists']
        return name, location, id, doctors, freeRooms, specialists
    else:
        name = jsonData['driver_name']
        location = jsonData['location']
        id = jsonData['id']
        isFree = jsonData['isFree']
        return name, location, id, isFree


def checkNadd(id, list, obj, split, location, kind):
    if len(list) == 0:
        if kind == "hosp":
            list.append(
                #   Name                Doctors     id     freeRooms   specialists
                obj(split[0], location, split[2], split[3], split[4], split[5]))
        else:
            list.append(
                obj(split[0], location, split[2], split[3]))
        return True

    else:
        for x in range(0, len(list)):
            if str(list[x].id) == str(id):
                print("There is an entity with the same id: ", id)
                return False
        if kind == "hosp":
            list.append(
                #   Name                Doctors     id     freeRooms   specialists
                obj(split[0], location, split[2], split[3], split[4], split[5]))
        else:
            list.append(
                #   Name              isFree/reason    id
                obj(split[0], location, split[2], split[3]))
        return True


def compareNupdate(message, data, location, List, allEntityList, id):
    topic = message[2]
    id = message[3]

    if topic == "ambulances":
        entity = findEntity(allEntityList[1], id, data)
        update(topic, entity, data)
    elif topic == "firefighters":
        entity = findEntity(allEntityList[0], id, data)
        update(topic, entity, data)
    elif topic == "polices":
        entity = findEntity(allEntityList[2], id, data)
        update(topic, entity, data)
    elif topic == "hospitals":
        entity = findEntity(allEntityList[4], id, data)
        update(topic, entity, data)
    elif topic == "users":
        entity = findEntity(allEntityList[3], id, data)
        update(topic, entity, data)
        decider(userReason=data[4], userLocation=location, FirefighterList=allEntityList[0],
                AmbulanceList=allEntityList[1], PoliceList=allEntityList[2], HospitalList=allEntityList[4], id=id)
    pass


def findEntity(List, id, data):
    if data[2] != id:
        print("Id does not Match Topic Id! Topic: ", id, "Id: ", data[2])
        return False
    else:
        try:
            entity = next((x for x in List if x.id == id), None)
            print("Found an Entity! ", id)
            pass
        except Exception as e:
            print(e)
            raise
        return entity


def update(topic, entity, data):
    if topic == "hospitals":
        try:
            entity.updateValues(
                hospitalName=data[0], doctors=data[5], freeRooms=data[6], specialists=data[7], id=data[2])
            pass
        except Exception as e:
            print(e)
            raise
    elif topic == "users":
        try:
            entity.updateValues(
                driverName=data[0], location=data[1], reasons=data[4])
            pass
        except Exception as e:
            print(e)
            raise
    else:
        # set the new values for pol, amb and firefighters
        try:
            entity.updateValues(
                driverName=data[0], location=data[1], isFree=data[3])
            pass
        except Exception as e:
            print(e)
            raise


def calcDistance(Location1, Location2):
    # (latitude, longitude)!!
    try:
        distance = geopy.distance.vincenty(Location1, Location2).km
        pass
    except Exception as e:
        print(e)
        raise
    return distance


def getClosest(userLocation=None, FirefighterList=None, AmbulanceList=None, PoliceList=None, HospitalList=None, specialist=None):
    closestList = []

    if userLocation != None:
        # Check if there is a given User Location
        if FirefighterList != None:
            closestList.append(findClosest(
                FirefighterList, userLocation, "firefighters"))
        if AmbulanceList != None:
            closestList.append(findClosest(
                AmbulanceList, userLocation, "ambulances"))
        if PoliceList != None:
            closestList.append(findClosest(
                PoliceList, userLocation, "polices"))

        # Hospital needs different handling because of the user reason !
        # First the right specialist must be found.
        # If there are more Hospitals with the same specialist, find the closest one.

        if HospitalList != None:
            # indices = [i for i, x in enumerate(my_list) if x == "specialist"]
            closestList.append(findClosest(
                HospitalList, userLocation, "hospitals"))
    else:
        print("No User Location found!")
    return closestList


def findClosest(List, userLocation, kindOfEntity):
    tempDistList = []
    if len(List) > 1:
        for entity in List:
            # Check if entity is avaiable
            if entity.isFree == True:
                # Calculate Distance
                dist = calcDistance(userLocation, entity.location)
                # Save Distance and id in tempDistList
                # Save the Dist first, because its more easy to find the smalest value
                tempDistList.append([dist, entity.id, kindOfEntity])
            # If everey distance is calculated find the smalest one
            index = tempDistList.index(min(tempDistList))
            return tempDistList[index]
    elif len(List) == 1:
        dist = calcDistance(userLocation, List[0].location)
        tempDistList.append([dist, List[0].id, kindOfEntity])
        return tempDistList

    elif len(List) == 0:
        print("There arent any", kindOfEntity, "generated by now!")


def decider(userReason=None, userLocation=None, FirefighterList=None, AmbulanceList=None, PoliceList=None, HospitalList=None, id=None):
    # the decider is used to decide which entity needs to be informed
    if userReason == "heart_attack":
        alarmList = getClosest(userLocation=userLocation,
                               AmbulanceList=AmbulanceList,
                               HospitalList=HospitalList,
                               specialist="HeartDoc")
        alarm(alarmList, userReason, userLocation, id)

    elif userReason == "accident":
        alarmList = getClosest(userLocation=userLocation,
                               FirefighterList=FirefighterList,
                               AmbulanceList=AmbulanceList,
                               PoliceList=PoliceList,
                               HospitalList=HospitalList,
                               specialist="AccidentDoc")
        alarm(alarmList, userReason, userLocation, id)

    elif userReason == "accident_fire":
        alarmList = getClosest(userLocation=userLocation,
                               FirefighterList=FirefighterList,
                               AmbulanceList=AmbulanceList,
                               PoliceList=PoliceList,
                               HospitalList=HospitalList,
                               specialist="AccidentDoc")
        alarm(alarmList, userReason, userLocation, id)

    elif userReason == "accident_oil":
        alarmList = getClosest(userLocation=userLocation,
                               FirefighterList=FirefighterList)
        alarm(alarmList, userReason, userLocation, id)

    elif userReason == "light_accident":
        alarmList = getClosest(userLocation=userLocation,
                               PoliceList=PoliceList)
        alarm(alarmList, userReason, userLocation, id)

    elif userReason == "hard_accident":
        alarmList = getClosest(userLocation=userLocation,
                               FirefighterList=FirefighterList,
                               AmbulanceList=AmbulanceList,
                               PoliceList=PoliceList,
                               HospitalList=HospitalList,
                               specialist="AccidentDoc")
        alarm(alarmList, userReason, userLocation, id)

    elif userReason == "police":
        alarmList = getClosest(userLocation=userLocation,
                               PoliceList=PoliceList)
        alarm(alarmList, userReason, userLocation, id)

    elif userReason == "ambulance":
        alarmList = getClosest(userLocation=userLocation,
                               AmbulanceList=AmbulanceList,
                               HospitalList=HospitalList,
                               specialist="AccidentDoc")
        alarm(alarmList, userReason, userLocation, id)

    elif userReason == "hospital":
        alarmList = getClosest(userLocation=userLocation,
                               HospitalList=HospitalList,
                               specialist="someDoc")
        alarm(alarmList, userReason, userLocation, id)

    elif userReason == "None":
        pass
    pass


def alarm(alarmList, userReason, userLocation, userId):
    # the alarm actually alarms the entitys over MQTT
    # also it sets the isFree value of an alarmed entity to Flase
    # alarmList -> [Distance, EntityID, kindOfEntity]
    # [[[3339.6181455116725, 'abc1', 'ambulances']], [[4221.03859127204, 'hops1', 'hospitals']]]
    # for some weird reason, the list is nested unnecessary complicated, as you can see above. The First step is to simplify it

    alarmData = []
    for data in alarmList:
        temp = data[0]
        alarmData.append(temp)

    # Now the Data is simplifyed and stored in alarmData
    for data in alarmData:
        try:
            topic = "/hshl/" + data[2] + "/" + data[1]
            message = {
                "reasons": userReason,
                "location": userLocation,
                "distance": data[0]
            }
            # The Message the Entitys Recive should look someting like this
            # {
            # 'reasons': 'accident',
            # 'location': [51.3, 23.22],
            # 'distance': 889.4124848067089
            # }
            # The NEWclient is only used to send infomartion to the entites.
            NEWclient.publish(topic, json.dumps(message))
            print("Send: ", message, " to: ", topic)
            pass
        except Exception as e:
            print(e)
            raise

    userTopic = "/hshl/users/" + str(userId)
    UserMessage = {
        "message": "Help is on the Way!"
    }
    NEWclient.publish(userTopic, json.dumps(UserMessage))
    print("Send: ", UserMessage, " to: ", userTopic)
    pass


# setup another MQTT Client to send alarm messages

BROKER_ADDRESS = "mr2mbqbl71a4vf.messaging.solace.cloud"  # Adresse des MQTT Brokers
NEWclient = mqtt.Client()
# Benutzernamen und Passwort zur Verbindung setzen
NEWclient.username_pw_set("solace-cloud-client", "nbsse0pkvpkvhpeh3ll5j7rpha")
NEWclient.connect(BROKER_ADDRESS, port=20614)  # Verbindung zum Broker aufbauen
print("Connected to MQTT Broker: " + BROKER_ADDRESS)