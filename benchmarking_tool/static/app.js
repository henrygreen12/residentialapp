function initialize() {
    var longitude = $('#map').data()['longitude'];
    var latitude = $('#map').data()['latitude'];

    var place = {lat: latitude, lng: longitude};

    var map = new google.maps.Map(document.getElementById('map'), {
        center: place,
        zoom: 18,
         mapTypeId: 'satellite',
         disableDefaultUI: true

    });

    var panorama = new google.maps.StreetViewPanorama(
        document.getElementById('pano'), {
            position: place,
            pov: {
            heading: 34,
            pitch: 10
        }
     });
    map.setStreetView(panorama);

}

$(document).ready(function () {
    initialize();
    });
