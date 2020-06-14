map = L.map('map').setView([22.157385036461264,-100.97436087045361], 13);

L.tileLayer('https://api.tiles.mapbox.com/v4/{id}/{z}/{x}/{y}.png?access_token={accessToken}', {
    attribution: 'Map data &copy; <a href="https://www.openstreetmap.org/">OpenStreetMap</a> contributors, <a href="https://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>, Imagery © <a href="https://www.mapbox.com/">Mapbox</a>',
    id: 'mapbox.streets',
    accessToken: 'pk.eyJ1IjoiZGV2Y3JhY2siLCJhIjoiY2ppbHpqaTM3MDNlZTNsbzlxMWZicmFsdyJ9.FnWLqL--4780qlIO3dzQ0w'
}).addTo(map);

geodata = [];

drawnItems = L.geoJSON().addTo(map);
obj_data = "";

options = {
    position: 'topleft',
	draw: {
		polygon: {
			allowIntersection: true,
			showArea: true,
		},
		circle: false,
		marker: false,
        polyline: false,
	},
	edit: {
		featureGroup: drawnItems,
		remove: true,
        edit: true
	}
};

drawControl = new L.Control.Draw(options);

map.addControl(drawControl);

map.on(L.Draw.Event.CREATED, function (event) {
    layer = event.layer;

    drawnItems.addLayer(layer);
});


$('#btn_save_geojson').click(function() {

	obj = JSON.stringify(drawnItems.toGeoJSON());

	console.log(obj);
	$.ajax({
		 data: obj,
		url: '/save_coordinates',
		type: 'post',
		dataType: 'json',
		contentType: 'application/json',
		success: function(response) {
			alert("Coordenadas guardadas..");
		},
		error: function(error) {
			alert("Error al guardar coordenadas..");
		}

	});
});


function click_list(num) {
	console.log(num);

    obj = obj_data[num];
	map.panTo(new L.LatLng(parseFloat(obj['lat']), parseFloat(obj['lon'])));

	geojson = obj['geojson'];
	//drawnItems.clearLayers();

	drawnItems.addData(geojson);

	map.fitBounds(drawnItems.getBounds());

}

//busca si existe un geojson

function busca_elemento() {
	$("#FList").empty();
	$("#FList").append("<p>Buscando elementos....</p>");
	$.get("/geo_search", {data: document.getElementById("entrada").value}, function(respuesta){
		$("#FList").empty();
		if(respuesta['status'] === 1) {
			text = respuesta['datos'].replace(/&#34;/g, '\"');
			obj_data = new String(text);
			obj_data = JSON.parse(text);

			for(i = 0; i < obj_data.length; i++) {
                out = "<a class=\"list-group-item list-group-item-action\" onclick=\"click_list(" + i + ")\" data-toggle=\"list\" href=\"#\" role=\"tab\">" + obj_data[i]['display_name'] + "</a><br>";
                $("#FList").append(out);
            }
		}else if(respuesta['status'] === -1){
			$("#FList").append("<p>No se encontraron datos..</p>");
		}
	});
}


$.ajax({
    url: "/get_geodata",
    type: 'GET',
    success: function(res) {
        if (res)
        {
            drawnItems.addData(res);

            map.fitBounds(drawnItems.getBounds());
        }
    }
});
