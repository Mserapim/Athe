Ext._define('judicial.diligences.FilterCountyWindow', {
    extend: 'judicial.diligences.FilterBaseWindow',

    width: 650,

    properties: [
        {stage: 1002, property: 'county'}
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
                        name: 'county',
                        rest: 'judicial.county.Restful',
                        fieldLabel: "Comarca",
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
                title: 'Filtrar por Comarca'
            }
        );

        judicial.diligences.FilterCountyWindow.superclass.constructor.call(this, cfg);
        this.readFilters();
    }
});
