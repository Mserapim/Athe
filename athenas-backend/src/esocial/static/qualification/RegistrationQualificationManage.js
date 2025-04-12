/**
 *
 **/
Ext._define('esocial.qualification.RegistrationQualificationManage', {
    extend: 'toolkit.widget.TabPanel',

    getQualificationGrid: function() {
        if(!this._grid) {
            this._grid = Ext._create('esocial.qualification.RegistrationQualificationGrid', {
                region: 'center',
                gridAutoLoad: true
            });
        }

        return this._grid;
    },

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});

        Ext.applyIf(
            cfg,
            {
                title: 'ESocial - Qualificação'
            }
        );

        Ext.apply(
            cfg,
            {
                layout: 'border',
                items: [
                    this.getQualificationGrid(),
                ]
            }
        );

        esocial.qualification.RegistrationQualificationManage.superclass.constructor.call(this, cfg);
    }
});
