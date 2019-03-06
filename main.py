import sys
import time
import random
import pathlib
import math
import numpy as np

airports_dict = {}
airport_area = {}
airports_list = []
start_area_id = None
start_airport_code = None
number_of_areas = None
number_of_airports = None
flights = None
start_time = None
time_limit = None

def read_data():
    global airport_area
    global airports_list
    global start_airport_code
    global start_area_id
    global flights
    global time_limit
    global areas
    global number_of_areas
    global number_of_airports

    file = open('./data/test_set_1.txt', mode='r')
    lines = file.read().splitlines()
    file.close()
    line = lines[0].split()
    number_of_areas = int(line[0])

    if number_of_areas <= 20: time_limit = 2.9
    elif number_of_areas <= 100: time_limit = 4.5
    else: time_limit = 14.4

    start_airport_code = line[1]
    airport_index = 0

    for area_id in range(number_of_areas):
        airports_codes = lines[area_id*2+2].split(' ')
        for airport_code in airports_codes:
            airports_list.append(airport_code)
            airports_dict.update({airport_code : airport_index})
            airport_area.update({airport_index : area_id})
            airport_index += 1

    number_of_airports = airport_index
    start_area_id = airport_area[airports_dict[start_airport_code]]
    flights = [[{}for j in range(number_of_areas + 1)]for k in range(len(airports_list))]

    for line in lines[number_of_areas*2+1:]:
        line = line.split(' ')
        from_ = line[0]
        to = line[1]
        day = int(line[2])
        price = int(line[3])
        from_id = airports_dict[from_]
        to_id = airports_dict[to]
        to_area_id = airport_area[to_id]
        if to_area_id not in flights[from_id][day]:
            flights[from_id][day][to_area_id] = {to_id: price}
        else:
            x = flights[from_id][day][to_area_id].get(to_id)
            if x is None or x < price:
                flights[from_id][day][to_area_id][to_id] = price

def get_flights_to_specific_area(from_id, day, to_area_id):
    specific_flights = []
    if (to_area_id in flights[from_id][day]):
        specific_flights += list(flights[from_id][day].get(to_area_id).items())
    if (to_area_id in flights[from_id][0]):
        specific_flights += list(flights[from_id][0].get(to_area_id).items())
    return(specific_flights)

def get_flights_to_specific_airport(from_id, day, to_area_id, to_airport_id):
    specific_flights = []
    if (to_area_id in flights[from_id][day] and to_airport_id in flights[from_id][day][to_area_id]):
        specific_flights += [flights[from_id][day][to_area_id][to_airport_id]]
    if (to_area_id in flights[from_id][0] and to_airport_id in flights[from_id][0][to_area_id]):
        specific_flights += [flights[from_id][0][to_area_id][to_airport_id]]
    return(specific_flights)


def best_cities_to_visit_in_areas(order_of_areas):

    # BRUTE FORCE - all combinations
    cheapest_price, cheapest_road = dfs(get_flights_to_specific_area(airports_dict[start_airport_code], 1, order_of_areas[1]),
                                        start_airport_code, 1, 0, [], order_of_areas)
    return cheapest_price, cheapest_road

def adjacent_neighbor_eval(new_order_of_areas, change, old_road, cheapest_price):
    old_price_of_changed_sequence = sum(s[3] for s in old_road[(change - 1) : (change + 2)])
    current_airport_id = airports_dict[old_road[change - 1][0]]
    final_airport_id = airports_dict[old_road[change + 1][1]]
    day = change
    road = []
    new_price_of_changed_sequence = math.inf
    for flight in get_flights_to_specific_area(current_airport_id, day, new_order_of_areas[day]):
        destination1_id = flight[0]
        flight1_price = flight[1]
        for flight in get_flights_to_specific_area(destination1_id, day + 1, new_order_of_areas[day + 1]):
            destination2_id = flight[0]
            flight2_price = flight[1]
            #tu pridat if ak letim do poslednej arei
            for flight in get_flights_to_specific_airport(destination2_id,day + 2,new_order_of_areas[day + 2],final_airport_id):
                flight3_price = flight
                price = flight1_price + flight2_price + flight3_price
                if price <= new_price_of_changed_sequence:
                    new_price_of_changed_sequence = price
                    road = [(airports_list[current_airport_id],airports_list[destination1_id],day,flight1_price),
                            (airports_list[destination1_id],airports_list[destination2_id],day+1,flight2_price),
                            (airports_list[destination2_id],airports_list[final_airport_id],day+2,flight3_price)]
    if(new_price_of_changed_sequence < math.inf):
        new_road = old_road[:change - 1] + road + old_road[change + 2:]
        new_price = cheapest_price + (new_price_of_changed_sequence - old_price_of_changed_sequence)
        return new_price, new_road
    return None, None

def interexhange_neighbor_eval(new_order_of_areas, change_i, change_j, old_road, cheapest_price):
    if(abs(change_i-change_j) == 1):
        return adjacent_neighbor_eval(new_order_of_areas, min(change_i,change_j), old_road, cheapest_price)

    old_price_of_sequence_i = sum(s[3] for s in old_road[(change_i - 1) : (change_i + 1)])
    old_price_of_sequence_j = sum(s[3] for s in old_road[(change_j - 1) : (change_j + 1)])

    current_airport_id_i = airports_dict[old_road[change_i - 1][0]]
    current_airport_id_j = airports_dict[old_road[change_j - 1][0]]
    final_airport_id_i = airports_dict[old_road[change_i][1]]
    final_airport_id_j = airports_dict[old_road[change_j][1]]
    day_i = change_i
    day_j = change_j
    road_i = []
    road_j = []
    new_price_of_of_sequence_i = math.inf
    new_price_of_of_sequence_j = math.inf

    for flight in get_flights_to_specific_area(current_airport_id_i, day_i, new_order_of_areas[day_i]):
        destination1_id = flight[0]
        flight1_price = flight[1]
        for flight in get_flights_to_specific_airport(destination1_id,day_i + 1,new_order_of_areas[day_i + 1],final_airport_id_i):
            flight2_price = flight
            price = flight1_price + flight2_price
            if price <= new_price_of_of_sequence_i:
                new_price_of_of_sequence_i = price
                road_i = [(airports_list[current_airport_id_i], airports_list[destination1_id], day_i, flight1_price),
                        (airports_list[destination1_id], airports_list[final_airport_id_i], day_i + 1, flight2_price)]

    for flight in get_flights_to_specific_area(current_airport_id_j, day_j, new_order_of_areas[day_j]):
        destination1_id = flight[0]
        flight1_price = flight[1]
        for flight in get_flights_to_specific_airport(destination1_id,day_j + 1,new_order_of_areas[day_j + 1],final_airport_id_j):
            flight2_price = flight
            price = flight1_price + flight2_price
            if price <= new_price_of_of_sequence_j:
                new_price_of_of_sequence_j = price
                road_j = [(airports_list[current_airport_id_j], airports_list[destination1_id], day_j, flight1_price),
                        (airports_list[destination1_id], airports_list[final_airport_id_j], day_j + 1, flight2_price)]

    if(new_price_of_of_sequence_i + new_price_of_of_sequence_j < math.inf):
        if(change_i < change_j):
            new_road = old_road[:change_i - 1] + road_i + old_road[change_i + 1:change_j - 1] + road_j + old_road[change_j + 1:]
        else:
            new_road = old_road[:change_j - 1] + road_j + old_road[change_j + 1:change_i - 1] + road_i + old_road[change_i + 1:]
        new_price = cheapest_price + (new_price_of_of_sequence_i + new_price_of_of_sequence_j) - (old_price_of_sequence_i + old_price_of_sequence_j)
        return new_price, new_road
    return None, None

def partial_dfs(available_flights, current_airport_id, final_airport_id, day, price, road, order_of_areas):
    if len(available_flights) == 0:
        return None, None
    day +=1
    cheapest_road = []
    cheapest_price = math.inf
    for flight in available_flights:
        destination_id = flight[0]
        flight_price = flight[1]

        if(len(road) == 1):
            if final_airport_id in flights[destination_id][day][order_of_areas[day]]:
                last_flight_price = flights[destination_id][day][order_of_areas[day]][final_airport_id]
                next_price = flight_price + last_flight_price
                next_road = road  + [(airports_list[current_airport_id], airports_list[destination_id],
                                    day - 1, flight_price),
                                     (airports_list[destination_id],final_airport_id, day, last_flight_price )]
            else:
                next_price = None
                next_road = None
        else:
            (next_price, next_road) = partial_dfs(get_flights_to_specific_area(destination_id, day, order_of_areas[day]),
                                                  destination_id, final_airport_id, day, price + flight_price,
                                                  road + [(airports_list[current_airport_id], airports_list[destination_id],
                                                     day - 1, flight_price)], order_of_areas)


        if (next_price is not None) and (next_price < cheapest_price):
            cheapest_road = next_road
            cheapest_price = next_price
    if len(cheapest_road) == 0 and cheapest_price == math.inf:
        return None, None
    return cheapest_price, cheapest_road

def dfs(flights_to_try, current_airport_code, day, price, road, order_of_areas):
    if len(flights_to_try) == 0:
        return None, None
    day +=1
    cheapest_road = []
    cheapest_price = math.inf
    for flight in flights_to_try:
        destination_id = flight[0]
        flight_price = flight[1]
        if airport_area[destination_id] == start_area_id and (len(road) + 2 == len(order_of_areas)):
            return price + flight_price, road + [(current_airport_code,airports_list[destination_id],day-1,flight_price)]
        (next_price, next_road) = dfs(get_flights_to_specific_area(destination_id, day, order_of_areas[day]),
                                      airports_list[destination_id], day, price + flight_price,
                                      road + [(current_airport_code,airports_list[destination_id],day-1,flight_price)],
                                      order_of_areas)

        if (next_price is not None) and (next_price < cheapest_price):
            cheapest_road = next_road
            cheapest_price = next_price
    if len(cheapest_road) == 0 and cheapest_price == math.inf:
        return None, None
    return cheapest_price, cheapest_road


def init_state_heuristic(current_airport_id, day, order_of_areas, road):
    if(len(road) == number_of_areas):
        return 0, road, order_of_areas

    possible_areas_to_flight = set(range(number_of_areas)) - set(order_of_areas)

    if len(possible_areas_to_flight) == 0:
        possible_areas_to_flight = [start_area_id]

    available_flights = []
    for area_id in possible_areas_to_flight:
        available_flights += get_flights_to_specific_area(current_airport_id, day, area_id)

    if len(available_flights) == 0:
        return None, None, None

    total_price = 0
    next_price = None

    available_flights.sort(key=lambda tup: tup[1])
    for flight in available_flights:
        flight_price = flight[1]
        next_price, next_road, next_order_of_areas = \
            init_state_heuristic(flight[0], day + 1, order_of_areas + [airport_area[flight[0]]],
                                 road + [(airports_list[current_airport_id], airports_list[flight[0]], day, flight_price)])
        if next_price is not None:
            order_of_areas = next_order_of_areas
            road = next_road
            total_price += next_price + flight_price
            break

    if(next_price is None):
        return None, None, None
    else:
        return total_price, road, order_of_areas

def generate_adjacent_neighbor(order_of_areas):
    #Adjacent interchanges
    n = len(order_of_areas) - 3
    i = random.randint(1, n)
    new_order_of_areas = order_of_areas[:]
    temp = new_order_of_areas[i]
    new_order_of_areas[i] = new_order_of_areas[i + 1]
    new_order_of_areas[i + 1] = temp
    return new_order_of_areas, i

def generate_interexchange_neighbor(order_of_areas, road):
    #interexchange
    n = len(order_of_areas) - 2
    i = random.randint(1, n)
    j = random.randint(1, n)
    while(j == i):
        j = random.randint(1, n)
    new_order_of_areas = order_of_areas[:]
    temp = new_order_of_areas[i]
    new_order_of_areas[i] = new_order_of_areas[j]
    new_order_of_areas[j] = temp
    return new_order_of_areas, i, j

def generate_interexchange_max_neighbor(order_of_areas, road):
    #interexchange
    i = np.argmax(np.array(s[3] for s in road[:-1])) + 1
    n = len(order_of_areas) - 2
    j = random.randint(1, n)
    while(j == i):
        j = random.randint(1, n)
    new_order_of_areas = order_of_areas[:]
    temp = new_order_of_areas[i]
    new_order_of_areas[i] = new_order_of_areas[j]
    new_order_of_areas[j] = temp
    return new_order_of_areas, i, j

def best_areas_order_search():
    #SIMULATED ANNEALING
    (price, road) = sa(0.90,5000)
    create_output(price, road)

def sa(cooling_factor, init_t):
    price, road, order_of_areas = init_state_heuristic(airports_dict[start_airport_code], 1, [start_area_id], [])
    t = init_t
    no_change = 0
    cheapest_price = price
    cheapest_road = road
    while time.time() - start_time < time_limit:

        if no_change >= 1000:
            t /= cooling_factor
        #new_order_of_areas, change = generate_adjacent_neighbor(order_of_areas)
        #(new_price, new_road) = adjacent_neighbor_eval(new_order_of_areas, change, road, price)
        new_order_of_areas, change_i, change_j = generate_interexchange_neighbor(order_of_areas, road)
        (new_price, new_road) = interexhange_neighbor_eval(new_order_of_areas, change_i, change_j, road, price)

        if new_price is None:
           continue

        if new_price < cheapest_price:
            cheapest_price = new_price
            cheapest_road = new_road
            price = new_price
            order_of_areas = new_order_of_areas
            road = new_road
            no_change = 0
            print(cheapest_price, " NEW BEST!!!")
        elif new_price <= price:
            price = new_price
            order_of_areas = new_order_of_areas
            road = new_road
            no_change = 0
            print(price, " improved")
        elif random.random() < math.exp((price - new_price)/t):
            price = new_price
            order_of_areas = new_order_of_areas
            road = new_road
            no_change = 0
            print(price, "worse aceepted")
        else:
            no_change += 1

        if no_change < 100:
            t *= cooling_factor

    return cheapest_price, cheapest_road

def create_output(price, road):
    print(price)
    for connection in road:
        print(connection[0], " ", connection[1], " ", connection[2], " ", connection[3])

def main():
    global start_time
    random.seed(5)
    start_time = time.time()
    read_data()
    best_areas_order_search()
    #print( time.time() - start_time)

if __name__ == '__main__':
    main()