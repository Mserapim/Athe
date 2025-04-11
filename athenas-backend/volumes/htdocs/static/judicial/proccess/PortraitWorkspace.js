Ext._define('judicial.proccess.PortraitWorkspace', {
    extend: 'judicial.proccess.BaseWorkspace',

    _partLawsuitOrientationConfig: function() {
        return {
            height: 350,
            minHeight: 350,
            region: 'south'
        }
    },

    constructor: function(cfg) {
        cfg = cfg || {};

        console.log('landscape');

        judicial.proccess.PortraitWorkspace.superclass.constructor.call(this, cfg);
    }
});
