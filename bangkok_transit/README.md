## Bangkok Transit

Scrape data from [transitbangkok.com](http://www.transitbangkok.com/) and put it online. Adding some tiny snippet for querying commute instruction.

### Usage

```python
import transit
stations = transit.read_stations('data/stations.csv')
route_descriptions = transit.get_commute_instruction('บางรัก', 'สีลม', stations) # return route instruction
```

**Output**

```python
{'query_link': 'http://www.transitbangkok.com/showBestRoute.php?from=Bang+Rak+Market&to=Si+Lom&originSelected=false&destinationSelected=false&lang=en',
 'route_descrtions':
    [{'action': 'Walk by foot',
      'lines': [],
      'to': 'Sathorn/Saphan Taksin'},
     {'action': 'Public Transport',
      'lines': ['BTS - Silom Line', '76', '163', '164', '172', '177', '504', '544', '547'],
      'to': 'Sala Daeng'},
     {'action': 'Walk by foot',
      'lines': [],
      'to': 'Si Lom'}],
 'station_end':
    {'station_link': 'http://www.transitbangkok.com/stations/Bangkok%20Bus/Si%20Lom',
     'station_name': 'Si Lom',
     'station_thai_name': 'สีลม'},
  'station_start':
    {'station_link': 'http://www.transitbangkok.com/stations/Bangkok%20Bus/Bang%20Rak%20Market',
     'station_name': 'Bang Rak Market',
     'station_thai_name': 'ตลาดบางรัก'}
}
```

The output (if both stations start and end match with their database)
will be list of instructions to go to the destination.
