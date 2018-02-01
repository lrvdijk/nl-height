class Visualisation

    constructor: (@line_plot_elem_id, @map_elem_id, @title_id) ->
        @line_plotter = new LinePlotter("#" + @line_plot_elem_id)
        @sealevel_map = new SealevelMap(@map_elem_id)

        # Connect to mouse events of the line plot, to show corresponding
        # location on the map
        @mouse_icon = L.divIcon(
            iconSize: [5, 5],
            className: 'mouse-loc-icon'
        )

        @mouse_marker = L.marker([0, 0],
            icon: @mouse_icon
            clickable: false
            zIndex: 1000
        ).addTo(@sealevel_map.map)

        @latitude = 0

        @line_plotter.mouseoverlay
            .on("mousemove", () =>
                mouse_pos = d3.mouse(d3.event.target)

                x = @line_plotter.xScaleFocus.invert(mouse_pos[0])
                degrees = @line_plotter.convertToDegrees(x)
                @mouse_marker.setLatLng([@latitude, degrees[0]])
                @mouse_marker.update()
        )

    loadMarkers: () ->
        Location.loadLocations((loc) =>
            @sealevel_map.addLocation(loc, (e, src, test) =>
                @loadLocation($(e.target).data('slug'))
            )
        )

    loadLocation: (slug) ->
        $.when(
            $.ajax url: "/data/" + slug + "/dataset.json"
            $.ajax url: "/data/" + slug + "/metadata.json"
        ).then (data, metadata) =>
            @line_plotter.plot(data[0], metadata[0])
            @sealevel_map.setCutLayer(metadata[0])
            @latitude = metadata[0].geometry.coordinates[0][1]

            $('#' + @title_id).text(
                "Elevation profile through " + metadata[0].properties.name
            )


$(document).ready ->
    vis = new Visualisation('chart', 'map', 'title');
    vis.loadMarkers()
    vis.loadLocation('amsterdam')

pairgen = (begin, end, baseL, projL) ->
    a = [{x: begin, base: baseL, proj: projL}]
    a.push({x: end, base: baseL, proj: projL})
    a
