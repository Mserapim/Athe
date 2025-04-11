/**
 *
 **/

Ext._define('common.internalSecurity.incidentReport.FilterLocationWindow', {
    extend: 'common.internalSecurity.incidentReport.FilterBaseWindow',

    width: 650,

    properties: [
        {stage: 1000, property: 'places__place__localidade'}
    ],

    getFormPanel: function(cfg) {
        if(!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                border: false,
                frame: true,
                labelWidth: 120,
                items: [
                    {
                        name: 'places__place__localidade',
                        fieldLabel: 'Localidade',
                        xtype: 'rest-autocompletefield',
                        rest: 'rh.localidade.Restful'
                    }
                ]
            });

        return this._formPanel;
    },

    constructor: function(cfg) {
        cfg = (cfg || {});

        Ext.applyIf(
            cfg,
            {
                title: 'Filtrar por Localidade'
            }
        );

        common.internalSecurity.incidentReport.FilterLocationWindow.superclass.constructor.call(this, cfg);
        this.readFilters();
    }
});
