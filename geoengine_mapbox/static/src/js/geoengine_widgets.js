/* global mapboxgl */
odoo.define('geoengine_mapbox.mapbox_geoengine_widgets', function (require) {
    "use strict";

    var geoengine_widgets = require('base_geoengine.geoengine_widgets');

    var FieldGeoEngineEditMap = geoengine_widgets.FieldGeoEngineEditMap.include({
        mapbox_client_id: false,

        /**
         * @override
         */
        start: function() {
          var def = this._super();
          this._rpc({
            model: 'ir.config_parameter',
            method: 'get_param',
            args: ['mapbox.client_id']
          }).then(function (access_token) {
            if (access_token) {
              this.mapbox_client_id = access_token;
            }
          }.bind(this));
          return def;
        },

        _renderMap: function () {
          if (!this.map) {
            if (!this.mapbox_client_id) {
              this._super();
              return;
            }
            var $el = this.$el[0];
            $($el).css({width: "100%", height: "100%"});

            if (this.map) {
              this.map.remove();
            }
            mapboxgl.accessToken = this.mapbox_client_id;
            var partner_longitude = this.record.data.partner_longitude;
            var partner_latitude = this.record.data.partner_latitude;

            this.map = new mapboxgl.Map({
              container: 'geo_point',
              style: 'mapbox://styles/mapbox/streets-v11',
              center: [partner_longitude, partner_latitude],
              zoom: 15
            });
            new mapboxgl.Marker()
            .setLngLat([partner_longitude, partner_latitude])
            .addTo(this.map);
            $(document).trigger('FieldGeoEngineEditMap:ready', [this.map]);
          }
        }
    });

    return FieldGeoEngineEditMap;

});
