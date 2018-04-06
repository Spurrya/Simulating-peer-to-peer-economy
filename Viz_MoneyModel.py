from mesa.visualization.modules import CanvasGrid
from mesa.visualization.modules import ChartModule
from mesa.visualization.ModularVisualization import ModularServer

from MoneyModel import EnergyModel
from MoneyModel import EnergyUsageType

DEBUG = 0

def agent_portrayal1(agent):


    portrayal = {"Shape": "circle",
                 "Filled": "true"}


    if(agent.type == EnergyUsageType.CONSUMER):
      portrayal["Color"] = "blue"
      portrayal["r"] = agent.savings/1000
      portrayal["Layer"] = 0
      # portrayal["text"] = str(agent.savings)
      # portrayal["text_color"] = "#000"

    elif(agent.type == EnergyUsageType.KEROSENE):
      portrayal["Color"] = "grey"
      portrayal["r"] = agent.savings/1000
      portrayal["Layer"] = 0
      # portrayal["text"] = str(agent.savings)
      # portrayal["text_color"] = "#000"

    elif(agent.type == EnergyUsageType.PRODUCER):
      portrayal["Color"] = "red"
      portrayal["r"] = agent.savings/1000
      portrayal["Layer"] = 0
      portrayal["text"] =  str(agent.level_solar)
      portrayal["text_color"] = "#000"


    if(agent.savings == 0):
      portrayal['r'] = 0
    elif(agent.savings > 2000 ):
      portrayal['r'] = 0.9
    elif(agent.savings > 1500):
      portrayal['r'] = 0.8
    elif(agent.savings>1000):
      portrayal['r'] = 0.6
    elif(agent.savings > 500):
      portrayal['r'] = 0.5
    elif(agent.savings > 100):
      portrayal['r'] = 0.2
    elif(agent.savings > 10):
      portrayal['r'] = 0.1

    return portrayal

def agent_portrayal2(agent):
  portrayal = {}


  if(agent.today_energy_needs == 0):
    portrayal["Shape"] = "circle"
    portrayal["Filled"] = "true"
    portrayal["Color"] = "green"
    portrayal["r"] = 1
    portrayal["Layer"] = 0

      

    return portrayal

grid1 = CanvasGrid(agent_portrayal1, 10, 10, 500, 500)
grid2 = CanvasGrid(agent_portrayal2, 10, 10, 500, 500)
chart = ChartModule([
    {"Label": "Number of people satisfied with energy needs", "Color": "Black"}],
    data_collector_name='datacollector'
)


parameters =  { "width":10,
   "height":10,
   "consumption_of_energy_mean": 3,
   "consumption_of_energy_std":0.1,
   "daily_production_of_energy_mean": 6,
   "daily_production_of_energy_std": 1,
   "daily_outcome_mean": 2,
   "daily_outcome_std":0.1,
   "daily_income_mean":10,
   "daily_income_std":0.5,
   "price_of_alternative_fuels":7.5,
   "price_of_solar_panel":150,
   "price_of_electricity_from_producer": 0.5,
   "probability_of_converting_into_producer":0.25,
   "probability_of_neighbour_converting_into_producer":0.05
}


parameters["probability_of_converting_into_producer"] = parameters["probability_of_converting_into_producer"] * parameters["price_of_electricity_from_producer"]
parameters["probability_of_neighbour_converting_into_producer"] = parameters["probability_of_neighbour_converting_into_producer"] * parameters["price_of_electricity_from_producer"] 


server = ModularServer(EnergyModel, [grid1, grid2], "Money Model", parameters)
server.port = 5000

server.launch()

