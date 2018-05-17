// Towing Management Application

// Company ID
companyid = "";

// Google Map
let map;

// Markers for map
let truckMarkers = [];
let incidentMarkers = [];

// Info window
let info = new google.maps.InfoWindow();

// Tracking device coordinates
var coords;
var timeout;

// Execute when the DOM is fully loaded
$(document).ready(function() {
    // enable submit button when input string length is 9 
    $('#companyidcheck').on('change textInput input', function () {
	companyid = this.value;

	var btn = $("#checkCompanyButton");

	if (companyid.length==9){
	    btn.prop('disabled', false);

	} else {
	    btn.prop('disabled', true);
	}
    });

    // enable submit button when all input fields are filled
    $('#company_info_form input').keyup(function() {
	var empty = $("#company_info_form").find("input").filter(function() {
	    return this.value === "";
	});
	if(empty.length) {
	   $(':input[type="submit"]').prop('disabled', true);
	} else {
	   $(':input[type="submit"]').prop('disabled', false);
	}
    });
    $('#operator_info_form input').keyup(function() {
	var empty = $("#operator_info_form").find("input").filter(function() {
	    return this.value === "";
	});
	if(empty.length) {
	   $(':input[type="submit"]').prop('disabled', true);
	} else {
	   $(':input[type="submit"]').prop('disabled', false);
	}
    });
    $('#request_ownership_form input').keyup(function() {
	var empty = $("#request_ownership_form").find("input").filter(function() {
	    return this.value === "";
	});
	if(empty.length) {
	   $(':input[type="submit"]').prop('disabled', true);
	} else {
	   $(':input[type="submit"]').prop('disabled', false);
	}
    });

    // onload requestownership.html - get companyid parameter
    if ( window.location.pathname == "/requestOwnership" ) {
	$("#companyid").val( getUrlParameter('companyid') );
    }

    if ( window.location.pathname == "/login" ) {
	$('#usertype>option:eq(1)').prop('selected', true);
    }

    // bind close message on clicking x
    $('.messageBox .x').click(function() {
	$(this).parent().fadeOut(function() {
	    $(this).remove();
	});
    });

    configureTypeahead();

    // initialize map only on map page
    if ( window.location.pathname == "/map" ) {
	initMap();
	$('#addIncident').on('click', function () {
	    addIncidentMarker(coords);
	});
    }
});

function initMap()
{
    // Styles for map
    // https://developers.google.com/maps/documentation/javascript/styling
    let styles = [
	// Hide Google's labels
	{
	    featureType: "all",
	    elementType: "labels",
	    stylers: [
	    {visibility: "off"}
	    ]
	},

	// Hide roads
	{
	    featureType: "road",
	    elementType: "geometry",
	    stylers: [
	    {visibility: "off"}
	    ]
	}
    ];

    // map options 
    let options = {
	center: {lat: 43.7037, lng: -79.3646}, // Toronto, Canada
        disableDefaultUI: true,
        mapTypeId: google.maps.MapTypeId.ROADMAP,
        maxZoom: 16,
        panControl: true,
        zoom: 14,
        zoomControl: false
    };

    // Get DOM node in which map will be instantiated
    let canvas = $("#map").get(0);

    // Instantiate map
    map = new google.maps.Map(canvas, options);

    // Configure UI once Google Map is idle (i.e., loaded)
    google.maps.event.addListenerOnce(map, "idle", configure);
}

function configure() {
    // Try HTML5 geolocation.
    if (navigator.geolocation) {

	let options = {
	    enableHighAccuracy: true,
	    maximumAge: 0
	};

	// watch current coordinates
	navigator.geolocation.watchPosition(function(position) {
	    coords = {
		lat: position.coords.latitude,
		lng: position.coords.longitude
	    };
	    // send coordinates to server 
	    $.ajax({
		type: 'GET',
		url: '/updateCoordinates',
		data: { 
		    lat: coords.lat,
		    lng: coords.lng
		},
		// return list of active trucks
		success: function(activetrucks) {
		    console.log("DEBUG: updateCoordinates (callback:success)");
		    console.log("Updated coordinates: ");
		    console.log(coords);

		    console.log("Active trucks: ");
		    console.log(activetrucks);

		    // Center map to current location
		    removeTruckMarkers();

		    drawTruckMarkers(activetrucks);
		    map.setCenter(coords);
		},
		error: function() {
		    console.log("DEBUG: updateCoordinates (callback:error)");
		}
	    });

	}, function() {
	    handleLocationError(true, info, map.getCenter());
	    console.log("DEBUG: watchPosition (callback:error)");
	}, options);

	/* Update UI after map has been dragged
	// google.maps.event.addListener(map, "dragend", function() {
	// If info window isn't open
	// http://stackoverflow.com/a/12410385
	if (!info.getMap || !info.getMap())
	{
	update()
	}

	}); */

    } else {
	// Browser doesn't support Geolocation
	handleLocationError(false, info, map.getCenter());
    }
}

let activetrucks = [];

function drawTruckMarkers() {

    // iterate through array of objects returned by updateCoords
    activetrucks.forEach((element, index, array) => {
	console.log("TRUCK #" + element.operatorid);
	console.log("Lat: " + element.lat);
	console.log("Lng: " + element.lng);
	console.log("Index: " + index);
	console.log("Array: " + array);

	coords = { 
	    element.lat,
	    element.lng
	};

	var image = "/static/truck-35x35.png";
	truckMarker = new google.maps.Marker({
	    position: coords,
	    map: map,
	    animation: google.maps.Animation.DROP,
	    icon: image,
	    title: 'todo: <operatorinfo>',
	    id: operatorid
	});

	truckMarkers.push(truckMarker);

	truckMarker.addListener('click', function() {
	    info.open(map, truckMarker);
	    console.log("Truck #" + truckMarker.id + "clicked");
	});

	info.setPosition(coords);
	info.setContent('It\'s me! Mario');
    });
}


function handleLocationError(browserHasGeolocation, info, coords) {
    info.setPosition(coords);
    info.setContent(browserHasGeolocation ?
	    'Error: The Geolocation service failed.' :
	    'Error: Your browser doesn\'t support geolocation.');
    info.open(map);
}

function addIncidentMarker(coords) {
    
    $.ajax({
	type: 'GET',
	url: '/createIncidentReport',
	data: { 
	    lat: coords.lat,
	    lng: coords.lng
	},
	success: function(incidentid) {
	    console.log("DEBUG: createIncidentReport (callback:success)");
	    console.log("Incident ID: " + incidentid);
	    console.log("Latitude: " + coords.lat);
	    console.log("Longitude: " + coords.lng);

	    var image = '/static/incident-32x32.png';
	    var incidentMarker = new google.maps.Marker({
		position: coords,
		map: map,
		animation: google.maps.Animation.DROP,
		icon: image,
		draggable: true,
	    });

	    incidentMarkers.push(incidentMarker);

	    incidentMarker.addListener('click', function() {
		info.open(map, incidentMarker);
	    });

	    google.maps.event.addListener(incidentMarker, 'dragend', function(evt){

		newLat = evt.latLng.lat();
		newLng = evt.latLng.lng();
		console.log('\n');
		console.log('Updated marker position');
		console.log('Latitude: ' + newLat);
		console.log('Longitude: ' + newLng);

		$.ajax({
		    type: 'GET',
		    url: '/updateIncidentReport',
		    data: { 
			incidentid: incidentid,
			lat: newLat,
			lng: newLng
		    },
		    success: function() {
			console.log("DEBUG: updateIncidentReport (callback:success)");
		    },
		    error: function() {
			console.log("DEBUG: updateIncidentReport (callback:error)");
		    }
		});
	    });

	    info.setPosition(coords);
	    info.setContent('<a href="/incidentReportForm">Start Report</a>');
	},
	error: function() {
	    console.log("DEBUG: createIncidentReport (callback:error)");
	}
    }); 
}

// Remove truck markers from map
function removeTruckMarkers()
{
    for (var i = 0; i < truckMarkers.length; i++) {
        truckMarkers[i].setMap(null);
    }
}

// Remove incident markers from map
function removeIncidentMarkers()
{
    for (var i = 0; i < incidentMarkers.length; i++) {
        incidentMarkers[i].setMap(null);
    }
}

// Search database for typeahead's suggestions
function search(query, syncResults, asyncResults)
{
    // Get places matching query (asynchronously)
    let parameters = {
        q: query
    };
    $.getJSON("/search", parameters, function(data, textStatus, jqXHR) {

        // Call typeahead's callback with search results (i.e., places)
        asyncResults(data);
    });
}

// Show info window at marker with content
function showInfo(marker, content)
{
    // Start div
    let div = "<div id='info'>";
    if (typeof(content) == "undefined")
    {
        // http://www.ajaxload.info/
        div += "<img alt='loading' src='/static/ajax-loader.gif'/>";
    }
    else
    {
        div += content;
    }

    // End div
    div += "</div>";

    // Set info window's content
    info.setContent(div);

    // Open info window (if not already open)
    info.open(map, marker);
}

/*
 * remove operator from company
 */
function removeOperator(rb)
{
    var row = $(rb).closest("tr");
    let operatorid = row.children().first().text();
    if (confirm("Are you sure?")) {
	$.ajax({
	    type: 'GET',
	    url: '/removeOperator',
	    data: { 
		operatorid: operatorid
	    },
	    success: function(returnVal) {
		row.remove();
	    },
	    error: function(request,error) {
		console.log('Callback error.');
	    }
	});
    } 
} 

/*
 * remove truck from company
 */
function removeTruck(rb)
{
    var row = $(rb).closest("tr");
    let truckid = row.children().first().text();
    if (confirm("Are you sure?")) {
	$.ajax({
	    type: 'GET',
	    url: '/removeTruck',
	    data: { 
		truckid: truckid
	    },
	    success: function(returnVal) {
		row.remove();
	    },
	    error: function(request,error) {
		console.log('Callback error.');
	    }
	});
    } 
} 

/*
 * remove pound from company
 */
function removePound(rb)
{
    var row = $(rb).closest("tr");
    let poundid = row.children().first().text();
    if (confirm("Are you sure?")) {
	$.ajax({
	    type: 'GET',
	    url: '/removePound',
	    data: { 
		poundid: poundid
	    },
	    success: function(returnVal) {
		row.remove();
	    },
	    error: function(request,error) {
		console.log('Callback error.');
	    }
	});
    } 
} 

/*
 *  check if company exists on submit 
 */
$(function() {
    $('#company_name_form').submit(function() {
        $.ajax({
            type: 'POST',
            url: '/getCompanyName',
            data: { 
		companyid: companyid
	    },
	    success: function(returnVal) {
		cb_func(returnVal);
	    },
	    error: function(request,error) {
		console.log('Callback error.');
	    }
        });
        return false;
    }); 
})

function cb_func(data) {
    $("#company_name_form").fadeOut(100, function() {
	if(data == "") {
	    // new company - show registration form
	    $("#company_info_form #companyid").val(companyid);
	    $("#company_info_form #companyidtitle").text("Reg. #: " + companyid);
	    $("#company_info_form").fadeIn(200);
	} else {
	    // existing company - redirect to request ownership page (pass companyid parameter)
	    window.location.href = "/requestOwnership?companyid=" + companyid;
	}
    });
}

var timeout; 

function configureTypeahead() {
    // Configure typeahead
    $("#q").typeahead({
        highlight: false,
        minLength: 1
    },
    {
        display: function(suggestion) { return null; },
        limit: 5,
        source: function(value, syncResult, asyncResult) {


            if (timeout) {
                clearTimeout(timeout);
            }

            timeout = setTimeout(function() {
                searchCompany(value, syncResult, asyncResult);
            }, 50);

        },
        templates: {
            suggestion: function(data) {
                return "<div class='typeahead-row'>" +
			    "<div class='company-name'>" + data[1] + "</div>" + 
			    "<div class='company-id'>(" + data[0] + ")</div>" + 
			"</div>"
	    }
        }
    });

    // Re-center map after place is selected from drop-down
    $("#q").on("typeahead:selected", function(eventObject, suggestion) {
	// hide company search form 
	$("#company_name_form").fadeOut(200, function() {
	    $("#companyNameTitle").text(suggestion[1]);
	// show operator info form
	    $("#operator_info_form").fadeIn(200, function() {
		$("#companyid").val(suggestion[0]);
	    });
	});
    });

    // Hide info window when text box has focus
    $("#q").focus(function(eventData) {
	// do something
    });

    // Give focus to text box
    $("#q").focus();

}

// Search database for typeahead's suggestions
function searchCompany(query, syncResults, asyncResults)
{
    // Get places matching query (asynchronously)
    let parameters = {
        q: query
    };
    $.getJSON("/searchCompany", parameters, function(data) {

        // Call typeahead's callback with search results (i.e., places)
        asyncResults(data);
    });
}


info = new google.maps.InfoWindow;

function handleLocationError(browserHasGeolocation, info, coords) {
    info.setPosition(coords);
    info.setContent(browserHasGeolocation ?
	    'Error: The Geolocation service failed.' :
	    'Error: Your browser doesn\'t support geolocation.');
    info.open(map);
}

index = 1;
function goToNextTab() {
    index++;
    $(".goPrev").show();
    if (index == 3) {
	$(".goNext").hide();
	$(".submit").show();
    }
    var nextTab = $('.nav-tabs > .active').next('li');
    if (nextTab.hasClass("disabled")) {
	nextTab.removeClass("disabled");
    }
    $('.nav-tabs > li').removeClass("active");
    nextTab.addClass("active");
    nextTab.find('a').attr("data-toggle","tab").trigger('click');
    
    $('html, body').animate({
        scrollTop: 0
    }, 100);
    
    if( nextTab.find('a').attr("href") == "#submit" ) {
        $(".go").fadeOut();
        $(window).unbind('beforeunload');
    }
}

function goToPrevTab() {
    index--;
    $(".goNext").show();
    $(".submit").hide();
    if (index == 1) {
	$(".goPrev").hide();
    }
    var prevTab = $('.nav-tabs > .active').prev('li');
    if (prevTab.hasClass("disabled")) {
	prevTab.removeClass("disabled");
    }
    $('.nav-tabs > li').removeClass("active");
    prevTab.addClass("active");
    prevTab.find('a').attr("data-toggle","tab").trigger('click');
    
    $('html, body').animate({
        scrollTop: 0
    }, 100);
}
