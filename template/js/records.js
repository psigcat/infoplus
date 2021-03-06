'use strict';

/* jshint globalstrict: true */

var layerId = null,
    featureId = null,
    json = null;

var margin = {top: 10, right: 5, bottom: 0, left: 0},
    width = 960 - margin.left - margin.right,
    barHeight = 20,
    barWidth = width * .8;

var i = 0,
    duration = 400,
    root;

var tree = d3.layout.tree()
    .nodeSize([0, 20]);

var diagonal = d3.svg.diagonal()
    .projection(function(d) { return [d.y, d.x]; });

var svg = d3.select("body").append("svg")
    .attr("width", width + margin.left + margin.right)
    .append("g")
    .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

function showRecords(layerIdFromPython, jsonFromPython) {
    layerId = layerIdFromPython;
    json = jsonFromPython;
    if (json.length == 0) {
        return;
    }
    
    // add some coord parameters to json necessary to tree visualization
    json.x0 = 0;
    json.y0 = 0;
    
    // show the tree
    update(root = json);
};

function update(source) {

    // Compute the flattened node list. TODO use d3.layout.hierarchy.
    var nodes = tree.nodes(root);
    var height = Math.max(500, nodes.length * barHeight + margin.top + margin.bottom);

    d3.select("svg").transition()
        .duration(duration)
        .attr("height", height);

    d3.select(self.frameElement).transition()
        .duration(duration)
        .style("height", height + "px");

    // Compute the "layout".
    nodes.forEach(function(n, i) {
        n.x = i * barHeight;
    });

    // Update the nodes…
    var gNode = svg.selectAll("g.node")
        .data(nodes, function(d) { return d.id || (d.id = ++i); });

    var nodeGroup = gNode.enter().append("g")
        .attr("class", "node")
        .attr("transform", function(d) { return "translate(" + source.y0 + "," + source.x0 + ")"; })
        .style("opacity", 1e-6);

    // Enter any new nodes at the parent's previous position.
    nodeGroup.append("svg:rect")
        .attr("y", -barHeight / 2)
        .attr("height", barHeight)
        .attr("width", barWidth)
        .style("fill", color)
        .on("click", manageExpansion);
  
    // show node name and value if it exists
    nodeGroup.append(nodeGenerator);
      
    // Transition nodes to their new position.
    nodeGroup.transition()
        .duration(duration)
        .attr("transform", function(d) { return "translate(" + d.y + "," + d.x + ")"; })
        .style("opacity", 1);

    gNode.transition()
        .duration(duration)
        .attr("transform", function(d) { return "translate(" + d.y + "," + d.x + ")"; })
        .style("opacity", 1)
        .select("rect")
        .style("fill", color);

    // Transition exiting nodes to the parent's new position.
    gNode.exit().transition()
        .duration(duration)
        .attr("transform", function(d) { return "translate(" + source.y + "," + source.x + ")"; })
        .style("opacity", 1e-6)
        .remove();

    // Update the links…
    var link = svg.selectAll("path.link")
      .data(tree.links(nodes), function(d) { return d.target.id; });

    // Enter any new links at the parent's previous position.
    link.enter().insert("path", "g")
        .attr("class", "link")
        .attr("d", function(d) {
            var o = {x: source.x0, y: source.y0};
            return diagonal({source: o, target: o});
        })
        .transition()
        .duration(duration)
        .attr("d", diagonal);

    // Transition links to their new position.
    link.transition()
        .duration(duration)
        .attr("d", diagonal);

    // Transition exiting nodes to the parent's new position.
    link.exit().transition()
        .duration(duration)
        .attr("d", function(d) {
            var o = {x: source.x, y: source.y};
            return diagonal({source: o, target: o});
        })
      . remove();

    // Stash the old positions for transition.
    nodes.forEach(function(d) {
        d.x0 = d.x;
        d.y0 = d.y;
    });
};

// add a id hiperlink node or a fieldName leaf node
function nodeGenerator(d) {
    
    var element = d3.select(this);
    var currentNodeType =  kindOfNode(d);
    
    // if root node
    if (currentNodeType == 'rootnode') {
        var t = element.append('text')
            .attr('class', currentNodeType)
            .attr("dy", 3.5)
            .attr("dx", 5.5)
            .text(d.name);
        return t.node();
    }
    
    // if record id node
    if (currentNodeType == 'recordid') {
        var t = element.append('text')
            .text(d.name) 
            .attr('class', currentNodeType)
            .attr("dy", 3.5)
            .attr("dx", 5.5)
            .on('click', selectRecord)
            .on('mouseover', hilightRecord);
        return t.node();
    }
    
    // if record leaf node
    if (currentNodeType == 'leafnode') {
        var g = element.append('g');
        g.append('text')
            .classed('fieldname', true)
            .text(function() {return d.name;})
            .attr("dy", 3.5)
            .attr("dx", 5.5);
        
        // check what to add depending if it's pdf or link
        var isUrl = IsURL( d.value );
        var isDocument = isDOC( d.value );
        
        if (!isUrl && !isDocument) {
            g.append('text')
                .classed('fieldvalue ', true)
                .text(d.value)
                .attr("dy", 3.5)
                .attr("dx", 120.5);
        }
        if (isUrl) {
            g.append('a')
                //.attr('xlink:href', d.value)
                .classed('link', true)
                .classed('fieldvalue ', true)
                .append('text')
                    .text(d.value)
                    .on('click', notifyLinkClicked)
                    .attr("dy", 3.5)
                    .attr("dx", 120.5);
        }
        if (isDocument) {
            g.append('a')
                //.attr('xlink:href', d.value)
                .classed('doc', true)
                .classed('fieldvalue ', true)
                .append('text')
                    .text(d.value)
                    .on('click', notifyDocClicked)
                    .attr("dy", 3.5)
                    .attr("dx", 120.5);
        }
        return g.node();
    }
}

// notify that a link has been clicked
function notifyLinkClicked(d) {
    // knowing data organization, browsing data, I can recover record Id
    var featureId = d.parent.parent.children[0].name;
    var link = d.value;
    recordsDisplayWidgetBridge.notifyLinkClicked(layerId, featureId, link);
}

// notify that a pdf document has been clicked
function notifyDocClicked(d) {
    // knowing data organization, browsing data, I can recover record Id
    var featureId = d.parent.parent.children[0].name;
    var pdfDocument = d.value;
    recordsDisplayWidgetBridge.notifyDocClicked(layerId, featureId, pdfDocument);
}

// select current clicked record deselecting the others
function selectRecord(d) {
    // deselect all
    d3.selectAll('.recordid')
        .classed('selected', false);
    
    // select current
    d3.select(this)
        .classed('selected', true);
        
    // set current featureId selection
    featureId = d3.select(this).text();
    recordsDisplayWidgetBridge.setSelctedRecord(layerId, featureId);
}

// hilight the record when the mouse is over the featureId
function hilightRecord(d) {
    // set current featureId selection
    featureId = d3.select(this).text();
    recordsDisplayWidgetBridge.setHilightRecord(layerId, featureId);
}

// return the updated class of the current node
function kindOfClass(d) {
    // get current class
    var currentClass = d3.select(this).attr('class');
    var newClass = kindOfNode(d);
    if (currentClass) {
        newClass = currentClass + ' ' + newClass;
    }
    
    return newClass;
}

function kindOfNode(d) {
    if (!d.parent) {
        return 'rootnode';
    }
    if (d.depth && d.depth == 1) {
        return 'recordid';
    }
    if (!d.children) {
        return 'leafnode';
    }
    return '';
}

// Toggle children on click.
function manageExpansion(d) {
    if (d.children) {
        d._children = d.children;
        d.children = null;
    } else {
        d.children = d._children;
        d._children = null;
    }
    update(d);
}

function color(d) {
    return d._children ? "#3182bd" : d.children ? "#c6dbef" : "#fd8d3c";
}

// recognise if string is a pdf filename
function isDOC(text) {
    // you can create a smarted regexp... leaved simple to allow simple modification
    var strRegex = "^.*\.(pdf|PDF|jpg|JPG|png|PNG)$";
    var re=new RegExp(strRegex);
    return re.test(text);
}

// fuction to recognise if string is am URL
function IsURL(url) {
    // because the regext recognize float as url due to '.' => check if it is a float before
    if (url === +url) {
        return false;
    }
     
    // get from http://stackoverflow.com/questions/3809401/what-is-a-good-regular-expression-to-match-a-url
    var urlRegex = '^(?!mailto:)(?:(?:http|https|ftp)://)(?:\\S+(?::\\S*)?@)?(?:(?:(?:[1-9]\\d?|1\\d\\d|2[01]\\d|22[0-3])(?:\\.(?:1?\\d{1,2}|2[0-4]\\d|25[0-5])){2}(?:\\.(?:[0-9]\\d?|1\\d\\d|2[0-4]\\d|25[0-4]))|(?:(?:[a-z\\u00a1-\\uffff0-9]+-?)*[a-z\\u00a1-\\uffff0-9]+)(?:\\.(?:[a-z\\u00a1-\\uffff0-9]+-?)*[a-z\\u00a1-\\uffff0-9]+)*(?:\\.(?:[a-z\\u00a1-\\uffff]{2,})))|localhost)(?::\\d{2,5})?(?:(/|\\?|#)[^\\s]*)?$';
    var re = new RegExp(urlRegex, 'i');
    return url.length < 2083 && re.test(url);
 }