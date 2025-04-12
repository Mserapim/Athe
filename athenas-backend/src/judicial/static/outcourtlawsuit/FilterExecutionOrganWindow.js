/**
 *
 **/

Ext._define('judicial.outcourtlawsuit.FilterExecutionOrganWindow', {
    extend: 'judicial.outcourtlawsuit.FilterBaseWindow',

    width: 650,

    properties: [
        {stage: 1000, property: 'location'}
    ],

    getFormPanel: function(cfg) {
        if(!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                border: false,
                frame: true,
                labelWidth: 120,
                items: [
                    {
                        name: 'location',
                        fieldLabel: 'Orgão de Execução',
                        xtype: 'rest-autocompletefield',
                        rest: 'rh.workplace.Restful'
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
                title: 'Filtrar por Orgão de Execução'
            }
        );

        judicial.outcourtlawsuit.FilterExecutionOrganWindow.superclass.constructor.call(this, cfg);
        this.readFilters();
    }
});
