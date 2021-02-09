odoo.define('geoengine_mapbox.mapbox_geoengine_widgets', function (require) {
    "use strict";

    var geoengine_widgets = require('base_geoengine.geoengine_widgets');

    var FieldGeoEngineEditMap = geoengine_widgets.FieldGeoEngineEditMap.include({ // eslint-disable-line max-len

        _renderMap: function () {
            var self = this;
            if (!this.map) {
                var $el = this.$el[0];
                $($el).css({
                    width: '100%',
                    height: '100%',
                });
                try {
                    console.log("Trying to load the map using MapBox API");
                    var partner_longitude = this.record.data.partner_longitude;
                    var partner_latitude = this.record.data.partner_latitude;
                    var coordinates = [partner_longitude, partner_latitude];
                    this._rpc({
                        model: 'res.partner',
                        method: 'get_mapbox_client_id',
                    }).then(function (result) {
                        if (!result) {
                            if (this.map) {
                                this.map.setTarget(null);
                                this.map = null;
                            }
                            var $el = this.$el[0];
                            $($el).css({width: '100%', height: '100%'});
                            this.map = new ol.Map({
                                layers: this.rasterLayers,
                                target: $el,
                                view: new ol.View({
                                    center: [0, 0],
                                    zoom: 5,
                                }),
                            });
                            this.map.addLayer(this.vectorLayer);

                            this.format = new ol.format.GeoJSON({
                                internalProjection: this.map.getView().getProjection(),
                                externalProjection: 'EPSG:' + this.srid,
                            });

                            $(document).trigger('FieldGeoEngineEditMap:ready', [this.map]);
                            this._setValue(this.value);

                        }
                        else {
                            if (this.map) {
                                this.map.remove();
                            }
                            mapboxgl.accessToken = result;
                            this.map = new mapboxgl.Map({
                                container: 'geo_point',
                                style: 'mapbox://styles/mapbox/streets-v11',
                                center: coordinates,
                                zoom: 15,
                            });
                            this.map.on('error', function() {
                                console.log("MapBox API failed, loading the map using OpenStreet API. Error: Wrong mapbox key entered");
                                self._rpc({
                                    model: 'res.partner',
                                    method: 'send_mapbox_fail_mail',
                                    args: [self.record.data.id, "Wrong mapbox key entered"],
                                }).then(function (result) {
                                    if (self.map) {
                                        self.map.remove();
                                    }
                                    var $el = self.$el[0];
                                    $($el).css({width: '100%', height: '100%'});
                                    self.map = new ol.Map({
                                        layers: self.rasterLayers,
                                        target: $el,
                                        view: new ol.View({
                                            center: [0, 0],
                                            zoom: 5,
                                        }),
                                    });
                                    self.map.addLayer(self.vectorLayer);
    
                                    self.format = new ol.format.GeoJSON({
                                        internalProjection: self.map.getView().getProjection(),
                                        externalProjection: 'EPSG:' + self.srid,
                                    });
    
                                    $(document).trigger('FieldGeoEngineEditMap:ready', [self.map]);
                                    self._setValue(self.value);
                                });
                            });
                            new mapboxgl.Marker()
                                .setLngLat(coordinates)
                                .addTo(this.map);
                            $(document).trigger('FieldGeoEngineEditMap:ready', [this.map]);
                        }
                    }.bind(this));
                } catch (error) {
                    console.log("MapBox API failed, loading the map using OpenStreet API. Error:", error);
                    this._rpc({
                        model: 'res.partner',
                        method: 'send_mapbox_fail_mail',
                        args: [error],
                    }).then(function (result) {

                        if (this.map) {
                            this.map.setTarget(null);
                            this.map = null;
                        }
                        var $el = this.$el[0];
                        $($el).css({width: '100%', height: '100%'});
                        this.map = new ol.Map({
                            layers: this.rasterLayers,
                            target: $el,
                            view: new ol.View({
                                center: [0, 0],
                                zoom: 5,
                            }),
                        });
                        this.map.addLayer(this.vectorLayer);

                        this.format = new ol.format.GeoJSON({
                            internalProjection: this.map.getView().getProjection(),
                            externalProjection: 'EPSG:' + this.srid,
                        });

                        $(document).trigger('FieldGeoEngineEditMap:ready', [this.map]);
                        this._setValue(this.value);
                    });
                }

            }
        },

        _renderOSMmap: function(){

        }

    });

    return FieldGeoEngineEditMap;

});
