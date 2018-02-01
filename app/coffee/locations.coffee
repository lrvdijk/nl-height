class Location
    constructor: (@name, @slug, @coordinates) ->

    @loadLocations: (handler) =>
        locations = []
        $.ajax('/data/locations.json').done (data, status, xhr) ->
            for slug, loc of data
                obj = new Location(
                    loc.properties.name,
                    loc.properties.slug,
                    # Reverse lat and long for leaflet
                    [
                        loc.properties.location[1],
                        loc.properties.location[0]
                    ]
                )

                handler(obj);
