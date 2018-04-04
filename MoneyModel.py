import random

from mesa import Agent, Model
from mesa.time import SimultaneousActivation
from mesa.space import MultiGrid
from mesa.datacollection import DataCollector
import random
import enum
import numpy as np


energy_produced_today = 0

def number_of_people_whose_energy_requirement_are_fulfilled(model):
    i = 0
    for agent in model.schedule.agents:
        if(agent.today_energy_needs == 0):
            i = i + 1
    return i


class EnergyModel(Model):
    """A model with some number of agents."""   

    def __init__(self,         
        width, 
        height, 
        consumption_of_energy_mean,
        consumption_of_energy_std,
        daily_production_of_energy_mean,
        daily_production_of_energy_std,
        daily_outcome_mean,
        daily_outcome_std, 
        daily_income_mean,
        daily_income_std, 
        price_of_alternative_fuels,
        price_of_solar_panel, 
        price_of_electricity_from_producer,
        probability_of_converting_into_producer,
        probability_of_neighbour_converting_into_producer
        ):

        self.num_agents = (width * height)
        self.running = True
        self.grid = MultiGrid(height, width, True)
        self.schedule = SimultaneousActivation(self)

        self.price_of_alternative_fuels = price_of_alternative_fuels
        self.price_of_solar_panel = price_of_solar_panel
        self.price_of_electricity_from_producer = price_of_electricity_from_producer
        self.probability_of_converting_into_producer = probability_of_converting_into_producer
        self.probability_of_neighbour_converting_into_producer = probability_of_neighbour_converting_into_producer
        self.daily_production_of_energy_mean = daily_production_of_energy_mean
        self.daily_production_of_energy_std = daily_production_of_energy_std

        self.datacollector = DataCollector(
            model_reporters={"Number of people who have access to energy needs": number_of_people_whose_energy_requirement_are_fulfilled},
            agent_reporters={"Wealth": lambda a: a.savings}
        )
        i = 0

        print("initing")
        for x in range(width):
            for y in range(height):

                consumption_of_energy = abs(int(np.random.normal(consumption_of_energy_mean, consumption_of_energy_std, 1)))
                daily_income = abs(int(np.random.normal(daily_income_mean, daily_income_std, 1)))
                daily_outcome = abs(int(np.random.normal(daily_outcome_mean, daily_outcome_std, 1)))
                savings = abs(int(np.random.normal(100, 80, 1)))

                a = EnergyAgent(x,y, savings, i, consumption_of_energy, daily_income, daily_outcome, self)
                self.schedule.add(a)
                self.grid.place_agent(a, (x, y))
                i = i +1

    def step(self):
        self.schedule.step()
        self.datacollector.collect(self)

    def run_model(self, n):
        for i in range(n):
            self.step()


class EnergyUsageType(enum.IntEnum):
    PRODUCER = 0
    CONSUMER = 1
    KEROSENE = 2

class EnergyAgent(Agent):
    def __init__(self, x,y, savings, unique_id,daily_energy_needs, daily_income, daily_outcome, model):
        self.x = x
        self.y = y
        self.unique_id = unique_id
        self.savings = savings
        self.type = EnergyUsageType.KEROSENE
        self.daily_energy_needs = daily_energy_needs
        self.daily_income = daily_income
        self.daily_outcome = daily_outcome
        self.level_solar = 0 # Kerosene users and consumers are level 0
        self.energy_owned = 0
        self.today_money = 0
        self.today_energy_needs = self.daily_energy_needs

        self.price_of_alternative_fuels = model.price_of_alternative_fuels
        self.price_of_solar_panel = model.price_of_solar_panel
        self.price_of_electricity_from_producer = model.price_of_electricity_from_producer
        self.probability_of_converting_into_producer = model.probability_of_converting_into_producer
        self.probability_of_convertion = 0
        self.probability_of_neighbour_converting_into_producer = model.probability_of_neighbour_converting_into_producer
        self.model = model

    def update_savings(self):
        self.savings = self.savings + self.today_money

    def convert_to_producer(self):
        if(self.savings > self.price_of_solar_panel and random.random()< self.probability_of_convertion):
            if(self.type != EnergyUsageType.PRODUCER ):
                self.level_solar = 1
                self.type = EnergyUsageType.PRODUCER
                self.savings = self.savings - self.price_of_solar_panel

                neighbours = self.model.grid.iter_neighbors([self.x,self.y],include_center=False, moore=True, radius=1)
                for neighbour in neighbours:
                    if(neighbour.type == EnergyUsageType.KEROSENE):
                        neighbour.type = EnergyUsageType.CONSUMER

            else:
                self.level_solar = self.level_solar + 1
                self.savings = self.savings - self.price_of_solar_panel


    def net_saving_for_today(self):
        self.today_money = self.daily_income - self.daily_outcome

        if(self.today_money < 0):
            self.today_money = 1


    def provide_income(self):
        #self.savings = self.daily_income + self.savings
        self.today_money = self.daily_income


    def produce_electricity(self, energy_produced_today):
        if(self.type == EnergyUsageType.PRODUCER):
            self.energy_owned = energy_produced_today * self.level_solar


    def buy_kerosene(self):
        while(self.today_energy_needs > 0 and self.today_money > self.price_of_alternative_fuels):
            self.energy_owned = self.energy_owned + 11
            self.today_money = self.today_money - self.price_of_alternative_fuels


    def trade_electricity(self):
        if(self.type == EnergyUsageType.PRODUCER):
            neighbours = self.model.grid.get_neighbors([self.x,self.y],include_center=False, moore=True, radius=3)

            while(self.energy_owned > self.today_energy_needs):
                i = 0
                j = 0
                for neighbour in neighbours:
                    j = j + 1
                    if(neighbour.today_energy_needs > 0 and neighbour.today_money > neighbour.price_of_electricity_from_producer):
                        self.energy_owned = self.energy_owned - 1;
                        neighbour.energy_owned = neighbour.energy_owned + 1;

                        self.today_money = neighbour.today_money - neighbour.price_of_electricity_from_producer
                        neighbour.today_money = neighbour.today_money - neighbour.price_of_electricity_from_producer

                        neighbour.today_energy_needs = neighbour.today_energy_needs - 1
                        neighbour.energy_owned = neighbour.energy_owned - 1
                    else:
                        i = i + 1
                if(i == j):
                    break;

            # print("===")
            # for n in neighbours:
            #     print("Today Money," + str(n.today_money))
            #     print("Today Needs," + str(n.today_energy_needs))
            #     print("Today Owned," + str(n.energy_owned))
    
    def consume_own_needs_producer(self):
        if(self.type == EnergyUsageType.PRODUCER):
            while(self.energy_owned > 0 and self.today_energy_needs > 0):
                self.energy_owned = self.energy_owned -1;
                self.today_energy_needs = self.today_energy_needs - 1;

    def update_prob_of_converting(self):
        neighbours = self.model.grid.iter_neighbors([self.x,self.y],include_center=True, moore=True, radius=1)
        i = 0
        for neighbour in neighbours:
            if(neighbour.today_energy_needs > 0):
                i = i+ 1

        if(i > 1):
            self.probability_of_convertion = self.probability_of_converting_into_producer
        else:
            self.probability_of_convertion = self.probability_of_neighbour_converting_into_producer

    def advance(self):
        self.today_energy_needs = self.daily_energy_needs
        self.energy_owned = 0 
        energy_produced_today = abs(int(np.random.normal(self.model.daily_production_of_energy_mean, self.model.daily_production_of_energy_std, 1)))

        self.provide_income()
        self.net_saving_for_today()
        self.produce_electricity(energy_produced_today)

        self.consume_own_needs_producer()

        self.trade_electricity()


        #Left over needs buy kerosene
        self.buy_kerosene()

        if(self.today_money < 0):
            self.today_money = 0

        if(self.today_energy_needs != 0):
            print("======")
            print("I am a ," + str(self.type))
            print("I am at," + str(self.x) + ","+str(self.y))
            print("I made today, $" + str(self.today_money))
            print("I own energy," + str(self.energy_owned))
            print("For today, I need, this much energy " + str(self.today_energy_needs))


        self.update_savings()
        self.convert_to_producer()
        self.update_prob_of_converting()




    # def move(self):
    #     possible_steps = self.model.grid.get_neighborhood(
    #         self.pos, moore=True, include_center=False
    #     )
    #     new_position = random.choice(possible_steps)
    #     self.model.grid.move_agent(self, new_position)

    # def give_money(self):
    #     cellmates = self.model.grid.get_cell_list_contents([self.pos])
    #     if len(cellmates) > 1:
    #         other = random.choice(cellmates)
    #         other.wealth += 1
    #         self.wealth -= 1

    # def step(self):
    #     self.move()
    #     if self.wealth > 0:
    #         self.give_money()
