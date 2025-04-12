/**
 *
 **/

Ext._define('judicial.outcourtlawsuit.FilterInterestedWindow', {
    extend: 'judicial.outcourtlawsuit.FilterBaseWindow',

    width: 650,

    properties: [
        {stage: 1002, property: 'has_interested__person'}
    ],

    getFormPanel: function(cfg) {
        if(!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                border: false,
                frame: true,
                labelWidth: 140,
                items: [
                    {
                        name: 'has_interested__person',
                        fieldLabel: 'Interessado',
                        xtype: 'rest-autocompletefield',
                        rest: 'rh.person.Restful'
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
                title: 'Filtrar por Interessado'
            }
        );

        judicial.outcourtlawsuit.FilterInterestedWindow.superclass.constructor.call(this, cfg);
        this.readFilters();
    }
});
