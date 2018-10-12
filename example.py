import dataclient
m = dataclient.MDALClient("corbusier.cs.berkeley.edu:8088")

request = {
    "Composition": ["temp"],
    "Aggregation": {
        "meter": ["MEAN"],
        "temp": ["MEAN"],
    },
    "Variables": {
        "meter": {
            "Definition": """SELECT ?meter ?meter_uuid WHERE {
                ?meter rdf:type brick:Building_Electric_Meter .
                ?meter bf:uuid ?meter_uuid
            };""" ,
        },
        "temp": {
            "Definition": """SELECT ?t ?t_uuid FROM ciee WHERE {
                ?t rdf:type/rdfs:subClassOf* brick:Temperature_Sensor .
                ?t bf:uuid ?t_uuid
            };""" ,
        },
    },
    "Time": {
        "Start":  "2018-01-01T10:00:00-07:00",
        "End":  "2018-08-12T10:00:00-07:00",
        "Window": '5min',
        "Aligned": True,
    },
}

resp = m.query(request)
print(resp.df)