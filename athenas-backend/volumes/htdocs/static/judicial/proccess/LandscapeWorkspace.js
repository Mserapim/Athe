Ext._define('judicial.proccess.LandscapeWorkspace', {
    extend: 'judicial.proccess.BaseWorkspace',

    _partLawsuitOrientationConfig: function() {
        return {
            minWidth: 640,
            width: 640,
            split: true,
            region: 'west'
        }
    },

    constructor: function(cfg) {
        cfg = cfg || {};

        console.log('portrait');

        judicial.proccess.LandscapeWorkspace.superclass.constructor.call(this, cfg);
    }
});
