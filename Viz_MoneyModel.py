from mesa.visualization.modules import CanvasGrid
from mesa.visualization.modules import ChartModule
from mesa.visualization.ModularVisualization import ModularServer

from MoneyModel import EnergyModel
from MoneyModel import EnergyUsageType


def agent_portrayal1(agent):


    portrayal = {"Shape": "circle",
                 "Filled": "true"}


    if(agent.type == EnergyUsageType.CONSUMER):
      portrayal["Color"] = "blue"
      portrayal["r"] = agent.savings/1000
      portrayal["Layer"] = 0

    elif(agent.type == EnergyUsageType.KEROSENE):
      portrayal["Color"] = "grey"
      portrayal["r"] = agent.savings/1000
      portrayal["Layer"] = 0

    elif(agent.type == EnergyUsageType.PRODUCER):
      portrayal["Color"] = "red"
      portrayal["r"] = agent.savings/1000
      portrayal["Layer"] = 0
      portrayal["text"] = agent.level_solar
      portrayal["text_color"] = "#000"

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

server = ModularServer(EnergyModel, [grid1, grid2], "Money Model",
 { "width":10,
   "height":10,
   "consumption_of_energy_mean": 3,
   "consumption_of_energy_std":0,
   "daily_production_of_energy_mean": 15,
   "daily_production_of_energy_std": 0,
   "daily_outcome_mean": 2,
   "daily_outcome_std":0,
   "daily_income_mean":15,
   "daily_income_std":0,
   "price_of_alternative_fuels":7,
   "price_of_solar_panel":150,
   "price_of_electricity_from_producer": 1,
   "probability_of_converting_into_producer":0.1,
   "probability_of_neighbour_converting_into_producer":0.001
})
server.port = 8888
server.launch()
