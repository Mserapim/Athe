Ext._define('judicial.noticeconfiguration.FilterDepartamentWindow', {
    extend: 'judicial.noticeconfiguration.FilterBaseWindow',

    width: 650,

    properties: [
        {stage: 1002, property: 'departament'}
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
                        name: 'departament',
                        rest: 'rh.workplace.Restful',
                        fieldLabel: "Departamento",
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
                title: 'Filtrar por departamento'
            }
        );

        judicial.noticeconfiguration.FilterDepartamentWindow.superclass.constructor.call(this, cfg);
        this.readFilters();
    }
});
