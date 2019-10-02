import enum, random
from time import struct_time, gmtime, mktime


class Car(object):
    def __init__(self, reg_no: str, color: str):
        self.__reg_no: str = reg_no
        self.__color: str = color

    def __repr__(self):
        return f"Car registration number: {self.__reg_no}. Color: {self.__color}"


class SpotType(enum.Enum):
    carpool = 1
    handicap = 2
    regular = 3


class Spot(object):
    def __init__(self, distance_from_gate: int, slot_type: SpotType, description: str):
        self.distance_from_gate = distance_from_gate
        self.slot_type = slot_type
        self.description = description

    def __repr__(self):
        return f"Spot distance from gate: {self.distance_from_gate}. " \
               f"Type: {self.slot_type}, Description={self.description}"


class Ticket(object):
    def __init__(self, spot: Spot, car: Car, start_time_utc: struct_time):
        self.__spot = spot;
        self.__car = car;
        self.__start_time_utc = start_time_utc;

    @property
    def spot(self):
        return self.__spot

    @property
    def car(self):
        return self.__car

    @property
    def start_time_utc(self):
        return self.__start_time_utc

    def __repr__(self):
        return f"Ticket: {self.__car} was parked at {self.spot} starting {self.start_time_utc}"


class Fare(object):
    def __init__(self, ticket: Ticket, end_time_utc: struct_time = gmtime()):
        self.__ticket = ticket;
        self.__end_time_utc = end_time_utc;
        self.__money_to_pay = (mktime(self.__end_time_utc) - mktime(self.__ticket.start_time_utc) + 300) * 0.1

    @property
    def money_to_pay(self) -> int:
        return self.__money_to_pay

    def __repr__(self):
        return f"Fare: {self.money_to_pay} for {self.__ticket}"


class Spots(object):
    def __init__(self):
        self.__spots = []

    # region Write/update APIs
    def sort(self):
        self.__spots.sort(key=lambda spot: spot.distance_from_gate)

    def remove_spot(self, spot: Spot):
        self.__spots.remove(spot)
        self.sort()

    def add_spot(self, spot: Spot):
        self.__spots.append(spot)
        self.sort()

    # this would be required when taking car out.
    def remove_spot_by_description(self, description: str):
        found_slot: Spot = self.find_slot_by_description(description)
        if found_slot is not None:
            self.__spots.remove(found_slot)
            self.sort()

    # endregion

    # region Query APIs
    def find_slot_by_description(self, description: str) -> Spot:
        return next(filter(lambda slot: slot.description == description, self.__spots), None)

    def count_of_slot_by_type(self, slot_type: SpotType) -> int:
        return sum(1 for s in self.__spots if s.slot_type == slot_type)

    def find_nearest_spot_by_type(self, spot_type: SpotType) -> Spot:
        found_spot = None
        for spot in self.__spots:
            if spot.slot_type == spot_type:
                found_spot = spot
                break
        return found_spot;

    def find_nearest_slot(self) -> Spot:
        return self.__spots[0] if len(self.__spots) > 0 else None

    def __repr__(self) -> str:
        return (f"{self.count_of_slot_by_type(SpotType.regular)} regular slots, "
                f"{self.count_of_slot_by_type(SpotType.carpool)} carpool slots, "
                f"{self.count_of_slot_by_type(SpotType.handicap)} handicap slots,  ")
    # endregion


class Lot(object):
    """
    Run this code from python console

    from parkinglot.src.parking import *
    lot = Lot.create_lot()
    print(f"Can park at regular spot? {lot.can_park(SpotType.regular)}")
    ticket = lot.park(SpotType.regular, Car("James Bond", "Red"))
    print(ticket)
    fare = lot.exit(ticket)
    print(fare)

    """

    def __init__(self):
        self.__available: Spots = Spots()
        self.__occupied: Spots = Spots()

    # region Lot construction

    @staticmethod
    def create_lot():
        lot = Lot()
        lot.add_spots()
        lot.lot_status()
        return lot

    def add_spots(self, num_floor: str = 3, num_carpool: str = 10, num_handicap: str = 5,
                  num_regular: str = 100):
        for floor in range(int(num_floor)):
            [self.__available.add_spot(
                Spot(self.calculate_distance(floor, x), SpotType.carpool, self.create_description(floor, x)))
                for x in range(int(num_carpool))]
            [self.__available.add_spot(
                Spot(self.calculate_distance(floor, x), SpotType.handicap, self.create_description(floor, x)))
                for x in range(int(num_handicap))]
            [self.__available.add_spot(
                Spot(self.calculate_distance(floor, x), SpotType.regular, self.create_description(floor, x)))
                for x in range(int(num_regular))]

    def lot_status(self):
        print(f"available slot = {self.__available}")

    @staticmethod
    def calculate_distance(num_floor, position_from_entry):
        return position_from_entry * int(num_floor) + 1

    @staticmethod
    def create_description(floor, position_from_entry):
        return f"{floor}.{position_from_entry}.carpool.{random.randint(1, 101)}"

    # endregion

    # region Parking APIs
    def can_park(self, spot_type: SpotType) -> bool:
        return True if self.__available.find_nearest_spot_by_type(spot_type) is not None else False

    def park(self, spot_type: SpotType, car: Car, start_time_utc: struct_time = gmtime()) -> Ticket:
        # find a spot
        spot = self.__available.find_nearest_spot_by_type(spot_type)
        if spot is None:
            raise Exception('Parking lot is full')

        # park
        self.move_spot(spot, self.__available, self.__occupied)

        # create and return ticket
        return Ticket(spot, car, start_time_utc)

    @staticmethod
    def move_spot(spot_to_move: Spot, src: Spots, destination: Spots):
        src.remove_spot(spot_to_move)
        destination.add_spot(spot_to_move)

    def exit(self, ticket: Ticket) -> Fare:
        self.move_spot(ticket.spot, self.__occupied, self.__available)
        fare = Fare(ticket)
        return fare

    # endregion
