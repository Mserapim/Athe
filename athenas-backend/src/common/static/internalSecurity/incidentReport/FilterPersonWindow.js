/**
 *
 **/

Ext._define('common.internalSecurity.incidentReport.FilterPersonWindow', {
    extend: 'common.internalSecurity.incidentReport.FilterBaseWindow',

    width: 650,

    properties: [
        {stage: 1000, property: 'reported_by'}
    ],

    getFormPanel: function(cfg) {
        if(!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                border: false,
                frame: true,
                labelWidth: 120,
                items: [
                    {
                        name: 'reported_by',
                        fieldLabel: 'Usuário',
                        xtype: 'rest-autocompletefield',
                        rest: 'auth.UserRestful'
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
                title: 'Filtrar por Usuário'
            }
        );

        common.internalSecurity.incidentReport.FilterPersonWindow.superclass.constructor.call(this, cfg);
        this.readFilters();
    }
});
