Ext._define('judicial.diligences.FilterOriginWindow', {
    extend: 'judicial.diligences.FilterBaseWindow',

    width: 650,

    properties: [
        { stage: 1004, property: 'part__lawsuit__location'}
    ],

    getFormPanel: function(cfg) {
        if(!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                border: false,
                frame: true,
                labelWidth: 120,
                items: [
                    {
                        xtype: 'rest-autocompletefield',
                        rest: "rh.workplace.Restful",
                        name: "part__lawsuit__location",
                        fieldLabel: "Origem",
                        gridConfig: {
                            columnAction: false,
                            hideItemsToolbar: ['add', 'edit', 'remove', 'download', 'filter'],
                        }
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
                title: 'Filtrar por Origem'
            }
        );

        judicial.diligences.FilterOriginWindow.superclass.constructor.call(this, cfg);
        this.readFilters();
    }
});
