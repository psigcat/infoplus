'use strict';

/* jshint globalstrict: true */
/* global dc,d3,crossfilter,colorbrewer */

var recordsTable = dc.dataTable('.dc-data-table');
var layerId = null,
    json = null,
    currentCat = null;

function showRecords(layerId, jsonFromPython) {
    layerId = layerId;
    json = JSON.parse(jsonFromPython);
    
    console.log(layerId);
    console.log(json);
    
    if (json.length == 0) {
        return;
    }
    
    // check column of the JSON records
    var genericRecord = json[0];
    var columns = Object.keys(genericRecord);
    
    //### Create Crossfilter Dimensions and Groups

    //See the [crossfilter API](https://github.com/square/crossfilter/wiki/API-Reference) for reference.
    var ndx = crossfilter(json);
    var all = ndx.groupAll();

    // Dimension by full ids
    var catDimension = ndx.dimension(function (d) {
        return d.featureId;
    });
        
    //#### Data Table
    recordsTable /* dc.dataTable('.dc-data-table', 'chartGroup') */
        .dimension(catDimension)
            .group(function (d) {
                return 'Category Index';
            })
            // (_optional_) max number of records to be shown, `default = 25`
            .size(json.length)
        .columns(columns)
        // (_optional_) sort using the given field, `default = function(d){return d;}`
        .sortBy(function (d) {
            return d.featureId;
        })
        // (_optional_) sort order, `default = d3.ascending`
        .order(d3.ascending)
        // (_optional_) custom renderlet to post-process chart using [D3](http://d3js.org)
        .on('renderlet', function (table) {
            table.selectAll('.dc-table-group').classed('info', true);
        });

    //#### Rendering

    //simply call `.renderAll()` to render all charts on the page
    dc.renderAll();
    
    // #### add listener to manage zooming / centering
    d3.selectAll('.dc-table-row').on('click', function() {
       // get featureId value to find it in the layer features
       // beaware that it is text not converted as integer
       currentCat = d3.select(this).select('.dc-table-column._0').text();
       
       // do some selection/hilight of the current row
       // changing some param
       
       console.log(layerId, currentCat)
       
       recordsDisplayWidgetBridge.setSelctedRecord(layerId, currentCat)
    });
};
