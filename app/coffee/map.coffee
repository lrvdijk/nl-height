class SealevelMap
    constructor: (element) ->

        @map = L.map(element)
        L.tileLayer('//{s}.tile.openstreetmap.org/{z}/{x}/{y}.png'
            attribution: '&copy; <a href="http://osm.org/copyright">OpenStreetMap</a> contributors'
        ).addTo(@map)

        L.tileLayer.wms('//geodata.nationaalgeoregister.nl/ahn2/wms',
            layers: 'ahn2_5m'
            format: 'image/png'
            transparent: true
            opacity: 0.5
            attribution: 'AHN2: CC-BY Kadaster'
        ).addTo(@map)

        # Center on Amersfoort
        @map.setView([52.1561110, 5.3878270], 7)
        @cut_layer = undefined

    addLocation: (loc, on_click_handler) ->
        marker = L.marker(loc.coordinates,
            zIndexOffset: 500
        ).addTo(@map);

        load_btn = $(document.createElement('button'))
        load_btn.addClass('btn btn-xs btn-success')
        load_btn.append(document.createTextNode('Load location'))
        load_btn.data(
            name: loc.name
            slug: loc.slug
            coordinates: loc.coordinates
        )

        $(load_btn).on('click', on_click_handler)

        p = $(document.createElement('p'))
        p.append($(document.createTextNode(loc.name + " - ")))
        p.append(load_btn)

        marker.bindPopup(p.get(0))

        return

    setCutLayer: (geoJson) ->
        if @cut_layer?
            @map.removeLayer(@cut_layer)

        @cut_layer = L.geoJson(geoJson)
        @cut_layer.addTo(@map)

