Ext._define('judicial.diligences.FilterOfficcerDiligenceWindow', {
    extend: 'judicial.diligences.FilterBaseWindow',

    width: 650,

    properties: [
        { stage: 1003, property: 'responsible_delivering'}
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
                        name: 'responsible_delivering',
                        rest: 'judicial.diligences.officer.DiligenceRestful',
                        fieldLabel: "Oficial de Diligência",
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
                title: 'Filtrar por Oficial de Diligência'
            }
        );

        judicial.diligences.FilterOfficcerDiligenceWindow.superclass.constructor.call(this, cfg);
        this.readFilters();
    }
});
