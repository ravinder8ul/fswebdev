// global variables
var map;
var infoWindow;
var bounds;

var clientID = '14NQZDJIRHVTAGHF3LI3YIWSP0AEH25U3C4VVE5HBNZ1JIQP';
var clientSecret = '32FLPEJM1NSGAGSPIR1XMI1GJDDIJB1B2WDPG1GPFD4B0NBV';

function initMap() {
  // Constructor creates a new map - only center and zoom are required
  map = new google.maps.Map(document.getElementById('map'), {
  	center: {lat: 40.748541, lng: -73.985758},
  	zoom: 7,
  	mapTypeControl: false
  });

	infoWindow = new google.maps.InfoWindow();
  bounds = new google.maps.LatLngBounds();

  ko.applyBindings(new ViewModel());

}

var ViewModel = function() {
	var self = this;

	this.searchLocation = ko.observable('');
	this.mapList = ko.observableArray([]);

  // add location markers for each location
  locations.forEach(function(location) {
      self.mapList.push( new LocationMarker(location) );
  });


  // locations viewed on map
  this.filteredLocations = ko.computed(function() {
      var searchFilter = self.searchLocation().toLowerCase();
      if (searchFilter) {
          return ko.utils.arrayFilter(self.mapList(), function(location) {
              var str = location.title.toLowerCase();
              var result = str.includes(searchFilter);
              location.visible(result);
							return result;
						});
      }
      self.mapList().forEach(function(location) {
          location.visible(true);
      });
      return self.mapList();
  }, self);

};

var LocationMarker = function(data) {
    var self = this;

    this.title = data.title;
    this.position = data.location;

    this.visible = ko.observable(true);

    // Style the markers a bit. This will be our listing marker icon.
    var defaultIcon = makeMarkerIcon('0091ff');
    // Create a "highlighted location" marker color for when the user
    // mouses over the marker.
    var highlightedIcon = makeMarkerIcon('FFFF24');

    // Create a marker per location, and put into markers array
    this.marker = new google.maps.Marker({
        position: this.position,
        title: this.title,
        animation: google.maps.Animation.DROP,
        icon: defaultIcon
    });    

    self.filterMarkers = ko.computed(function () {
        // set marker and extend bounds (showListings)
        if(self.visible() === true) {
            self.marker.setMap(map);
            bounds.extend(self.marker.position);
            map.fitBounds(bounds);
        } else {
            self.marker.setMap(null);
        }
    });
    
    // Create an onclick event to open the  infowindow at each marker.
    this.marker.addListener('click', function() {
        populateInfoWindow(this, infoWindow);
        toggleBounce(this);
        map.panTo(this.getPosition());
    });

    // Two event listeners - one for mouseover, one for mouseout,
    // to change the colors back and forth.
    this.marker.addListener('mouseover', function() {
        this.setIcon(highlightedIcon);
    });
    this.marker.addListener('mouseout', function() {
        this.setIcon(defaultIcon);
    });

    // show item info when selected from list
    this.show = function(location) {
        google.maps.event.trigger(self.marker, 'click');
    };

    // creates bounce effect when item selected
    this.bounce = function(place) {
			google.maps.event.trigger(self.marker, 'click');
		};

};


function toggleBounce(marker) {
  if (marker.getAnimation() !== null) {
    marker.setAnimation(null);
  } else {
    marker.setAnimation(google.maps.Animation.BOUNCE);
    setTimeout(function() {
        marker.setAnimation(null);
    }, 1400);
  }
}

// use as it is
function makeMarkerIcon(markerColor) {
    var markerImage = new google.maps.MarkerImage(
        'http://chart.googleapis.com/chart?chst=d_map_spin&chld=1.15|0|' + markerColor +
        '|40|_|%E2%80%A2',
        new google.maps.Size(21, 34),
        new google.maps.Point(0, 0),
        new google.maps.Point(10, 34),
        new google.maps.Size(21, 34));
    return markerImage;
}

function populateInfoWindow(marker, infowindow) {
  var street = '';
  var city = '';
  var phone = '';
  // get JSON request of foursquare data

  var reqURL = 'https://api.foursquare.com/v2/venues/search?ll=' + marker.position.lat() + ',' + marker.position.lng() + '&client_id=' + clientID + '&client_secret=' + clientSecret + '&v=20160118' + '&query=' + marker.title;

  $.getJSON(reqURL).done(function(data) {
   	var results = data.response.venues[0];
   	street = results.location.formattedAddress[0] ? results.location.formattedAddress[0]: 'N/A';
    city = results.location.formattedAddress[1] ? results.location.formattedAddress[1]: 'N/A';
    phone = results.contact.formattedPhone ? results.contact.formattedPhone : 'N/A';
   }).fail(function() {
        alert('Something went wrong with foursquare');
    });

  // Check to make sure the infowindow is not already opened on this marker.
  if (infowindow.marker != marker) {
      // Clear the infowindow content to give the streetview time to load.
      infowindow.setContent('');
      infowindow.marker = marker;

      // Make sure the marker property is cleared if the infowindow is closed.
      infowindow.addListener('closeclick', function() {
          infowindow.marker = null;
      });
      var streetViewService = new google.maps.StreetViewService();
      var radius = 50;

      var windowContent = '<h4>' + marker.title + '</h4>' + 
          '<p>' + street + "<br>" + city + '<br>' + phone + "</p>";

      // In case the status is OK, which means the pano was found, compute the
      // position of the streetview image, then calculate the heading, then get a
      // panorama from that and set the options
      var getStreetView = function (data, status) {
          if (status == google.maps.StreetViewStatus.OK) {
              var nearStreetViewLocation = data.location.latLng;
              var heading = google.maps.geometry.spherical.computeHeading(
                  nearStreetViewLocation, marker.position);
              infowindow.setContent(windowContent + '<div id="panorama"></div>');
              var panoramaOptions = {
                  position: nearStreetViewLocation,
                  pov: {
                      heading: heading,
                      pitch: 20
                  }
              };
              var panorama = new google.maps.StreetViewPanorama(
                  document.getElementById('panorama'), panoramaOptions);
          } else {
              infowindow.setContent(windowContent + '<div style="color: red">No Street View Found</div>');
          }
      };
      // Use streetview service to get the closest streetview image within
      // 50 meters of the markers position
      streetViewService.getPanoramaByLocation(marker.position, radius, getStreetView);
      // Open the infowindow on the correct marker.
      infowindow.open(map, marker);
  }
}

function errorHandler() {
  alert('Failed to retrieve Google Maps');
}
