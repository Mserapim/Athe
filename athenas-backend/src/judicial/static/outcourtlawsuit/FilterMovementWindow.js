Ext._define('judicial.outcourtlawsuit.FilterMovementWindow', {
    extend: 'judicial.outcourtlawsuit.FilterBaseWindow',

    width: 650,

    properties: [
        {stage: 1004, property: 'last_part_lawsuit__type_part'}
    ],

    getGlossary: function(cfg) {
        if(!this._glossary)
            this._glossary = Ext._create('core.fields.AutocompleteField',{
                xtype: "rest-autocompletefield",
                fieldLabel: "Movimento",
                valueField: 'model_name',
                displayField: 'title',
                allowBlank: false,
                rest: "judicial.params.GlosaryFilterRestful",
                name: "last_part_lawsuit__type_part",
            });
        return this._glossary;
    },

    getFormPanel: function(cfg) {
        if(!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                border: false,
                frame: true,
                labelWidth: 140,
                items: [
                    this.getGlossary()
                ]
            });

        return this._formPanel;
    },

    constructor: function(cfg) {
        cfg = (cfg || {});

        Ext.applyIf(
            cfg,
            {
                title: 'Filtrar por último movimento'
            }
        );

        judicial.outcourtlawsuit.FilterLawsuitTypeWindow.superclass.constructor.call(this, cfg);
        this.readFilters();
    }
});
