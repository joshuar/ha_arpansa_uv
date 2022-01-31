"""ARPANSA  """
from cProfile import run
from bs4 import BeautifulSoup
import lxml
import aiohttp
import asyncio
from .const import ARPANSA_URL

class Arpansa:
    """Arpansa class fetches the latest measurements from the ARPANSA site"""
    def __init__(self):
        self.measurements = None 

    async def fetchLatestMeasurements(self,session):
        """Retrieve the latest data from the ARPANSA site."""
        async with session.get(ARPANSA_URL) as response:
            try:
                t = await response.text()
                self.measurements = BeautifulSoup(t,'lxml')
            except response.status != 200:
                self.measurements = None

    def getAllLocations(self):
        """Get the names of all locations."""
        rs = self.measurements.find_all("location")
        allLocations = []
        for l in rs:
            allLocations.append(l.get("id"))
        return tuple(allLocations)

    def getAllLatest(self):
        """Get the latest measurements for all locations."""
        rs = self.measurements.find_all("location")
        allLocations = []
        for l in rs:
            thisLocation = {}
            thisLocation["name"] = l.get("id")
            thisLocation["value"] = l.find("index").text
            allLocations.append(thisLocation)
        return tuple(allLocations)

    def getLatest(self,name):
        """Get the latest measurements for a specified location."""
        rs = self.measurements.find("location", {"id": name})
        return rs.find("index").text

async def main():
    """Example usage of the class"""
    async with aiohttp.ClientSession() as session:
        arpansa = Arpansa()
        await arpansa.fetchLatestMeasurements(session)
        for measurement in arpansa.getAllLatest():
            print(measurement)
        location = arpansa.getLatest("Brisbane")
        print(location)

if __name__ == "__main__":
    import time
    s = time.perf_counter()
    asyncio.run(main())
    elapsed = time.perf_counter() - s
    print(f"{__file__} executed in {elapsed:0.2f} seconds.")