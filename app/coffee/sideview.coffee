
class LinePlotter
    constructor: (@selector) ->
        @img = $(@selector)
        @svg = d3.select(@selector).append("svg")

        @svg.append("defs").append("clipPath")
            .attr("id", "clip")
            .append("rect")

        @projection = d3.geo.mercator()
        @padding =
            top: 0
            left: 60
            bottom: 30
            right: 10

        @padding2 =
            top: 250
            left: @padding.left
            bottom: @padding.bottom
            right: @padding.right

        @focus = @svg.append("g")
            .attr("id", "focus")
            .attr("transform", "translate(" + @padding.left + "," + @padding.top + ")")

        @focus.append("g")
            .attr("class", "y axis")

        @focus.append("g")
            .attr("class", "x axis")

        @focus.append("text")
            .attr("class", "axis")
            .attr("x", -@padding.left)
            .attr("y", (@padding2.top - @padding.bottom)/2)
            .attr("text-anchor", "right")
            .text("NAP")

        @waterFocus = @focus.append("g")
            .attr("class", "water")

        @focus.append("g")
            .attr("class", "land")
            .append("path")
            .attr("id", "focus-land-path")
            .attr("clip-path", "url(#clip)")

        @context = @svg.append("g")
            .attr("id", "context")
            .attr("transform", "translate(" + @padding2.left + ", " +@padding2.top + ")")

        @context.append("g")
            .attr("class", "x axis")

        @waterContext = @context.append("g")
            .attr("class", "water")

        @context.append("g")
            .attr("class", "land")
            .append("path")
            .attr("id", "context-land-path")
            .attr("clip-path", "url(#clip)")
        @context.append("g")
            .attr("id", "locations")

        @mouseoverlay = @svg.append("rect")
        .attr("id", "mouseoverlay")

        @data = undefined
        @metadata = undefined
        @year = 0

        @setSizes()
        d3.select(window).on("resize", @setSizes.bind(this));

    setSizes: () ->
        @width = @img.width()
        @height = @img.height()
        @svg.attr("width", @width)
        @svg.attr("height", @height)

        @heightFocusBox = @padding2.top - @padding.bottom
        @heightContextBox = @height - @padding2.top - @padding2.bottom
        @widthFocusBox = @width - @padding.left - @padding.right
        @widthContextBox = @width - @padding2.left - @padding2.right

        @svg.select('#clip rect')
            .attr("width", @widthFocusBox)
            .attr("height", @heightFocusBox);

        @mouseoverlay
            .attr("transform", "translate(" + @padding.left + "," + @padding.top + ")")
            .attr("width", @widthFocusBox)
            .attr("height", @heightFocusBox)

        @focus.select('.axis.x')
            .attr("transform", "translate(0 ," + (@heightFocusBox) + ")")

        @context.select('.axis.x')
            .attr("transform", "translate(0 ," + (@heightContextBox) + ")")


        if @data? && @metadata?
            @draw()

    adjustScales: (maxX, maxY, minX, minY) ->
        @xScaleFocus = d3.scale.linear()
            .domain([minX, maxX])
            .range([0, @widthFocusBox])

        @xScaleContext = d3.scale.linear()
            .domain([minX, maxX])
            .range([0, @widthContextBox])

        @yScaleFocus = d3.scale.linear()
            .domain([minY, maxY])
            .range([@heightFocusBox, 0])

        @yScaleContext = d3.scale.linear()
            .domain([minY, maxY])
            .range([@heightContextBox, 0])

        @brush = d3.svg.brush()
        @brush.x(@xScaleContext)
            .on("brush", @brushed)

        @context.select('.brush.x').remove()
        @context.append("g")
            .attr("class", "x brush")
            .call(@brush)
            .selectAll("rect")
            .attr("y", -6)
            .attr("height", @height - @padding2.top - @padding2.bottom + 7);


    brushed: () =>
        if (@brush.empty())
            @xScaleFocus.domain(@xScaleContext.domain())
        else
            @xScaleFocus.domain(@brush.extent())
        @focus.select(".land path").attr("d", @areaFocus);
        @xAxisSVG.call(@xAxisFocus);

    convertToDegrees: (d) ->
        @projection.invert([d, @data.data[0].lat])

    plot: (@data, @metadata) ->
        @draw()

    draw: () ->
        data = @data.data

        xMin = @projection(@metadata.geometry.coordinates[0])[0]
        xMax = d3.max(data, (d) => 
            @projection([d.long, d.lat])[0]
        )

        yMax = d3.max(data, (d) => d.height)
        yMin = -13
        @adjustScales(xMax, yMax, xMin, yMin)

        cityX = (@projection(@metadata.properties.location)[0])

        @areaFocus = d3.svg.area()
            .x( (d) => @xScaleFocus(@projection([d.long, d.lat])[0]))
            .y0(@heightFocusBox)
            .y1( (d) => @yScaleFocus(d.height))

        areaContext = d3.svg.area()
            .x( (d) => @xScaleContext(@projection([d.long, d.lat])[0]))
            .y0(@heightContextBox)
            .y1( (d) => @yScaleContext(d.height))

        yAxis = d3.svg.axis().scale(@yScaleFocus)
            .orient("left").ticks(5)

        @xAxisFocus = d3.svg.axis().scale(@xScaleFocus)
            .orient("bottom")
            .tickFormat((d) => (d3.round(@convertToDegrees(d)[0], 2) + "°"))
            .ticks(5)

        xAxisContext = d3.svg.axis().scale(@xScaleContext)
            .orient("bottom").ticks(1).tickValues([xMin, cityX, xMax])
            .tickFormat((d) => (d3.round(@convertToDegrees(d)[0], 2) + "°"))

        @focus.select(".axis.y")
            .call(yAxis)


        @xAxisSVG = @focus.select(".axis.x")
            .call(@xAxisFocus)

        @context.select('.axis.x')
            .call(xAxisContext)

        @plotSealevel(xMin, xMax)

        d3.select('#focus-land-path')
            .datum(data)
            .attr("d", @areaFocus)

        d3.select('#context-land-path')
            .datum(data)
            .attr("d", areaContext)

        @context.select("#locations").remove()
        @context.append("g")
            .attr('id', 'locations')
            .attr("transform", "translate(" + @xScaleFocus(cityX) + ", " + (@heightContextBox + @padding2.bottom)  + ")")
            .append('text')
            .attr("text-anchor", "middle")
            .text(@metadata.properties.name)


    plotSealevel: (@xMinSeaLevel, @xMaxSeaLevel) ->
        @drawSeaLevel()

    drawSeaLevel: () ->
        baseSeaLevel = 0

        data = [
            {x: @xMinSeaLevel, y: baseSeaLevel},
            {x: @xMaxSeaLevel, y: baseSeaLevel}
        ]

        @waterFocus.selectAll("path").remove()
        @waterContext.selectAll("path").remove()

        areaNowFocus = d3.svg.area()
            .x((d) => @xScaleFocus(d.x))
            .y0(@heightFocusBox)
            .y1((d) => @yScaleFocus(d.y))

        areaNowContext = d3.svg.area()
            .x((d) => @xScaleContext(d.x))
            .y0(@heightContextBox)
            .y1((d) => @yScaleContext(d.y))

        @waterFocus.append("path")
            .datum(data)
            .attr("class", "waterarea")
            .attr("d", areaNowFocus)
            .attr("clip-path", "url(#clip)")

        @waterContext.append("path")
            .datum(data)
            .attr("class", "waterarea")
            .attr("d", areaNowContext)
            .attr("clip-path", "url(#clip)")


range = (start, stop, elements, baseL, projL) ->
    a = [{x: start, base: baseL, proj: projL}]
    b = start
    step = (stop - start) / elements
    while(b<stop)
        b+=step
        a.push({x: b, base: baseL, proj: projL})
    a
