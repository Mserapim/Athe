Ext._define('raf.taxonomyclassification.Window', {
    extend: 'core.RestfulWindow',

    rest: 'raf.taxonomyclassification.Restful',

    getClassificationField: function(cfg) {
        if(!this._classificationField) {
            this._classificationField = Ext._create('core.fields.AutocompleteField', {
                xtype: "rest-autocompletefield",
                fieldLabel: "Classificação",
                allowBlank: false,
                rest: "judicial.taxonomy.LegalClassificationRestful",
                name: cfg.params.excludeTaxonomy == true ? "exclude_classification" : "classification",
                disabled: false,
                gridConfig: {
                    columnAction: false,
                    allowUpdate: false,
                    allowRemove: false,
                    listeners: {
                        scope: this,
                        render: function(grid){
                            tbar = grid.getToolbar();
                            tbar.remove(tbar.getComponent(0));//Novo
                            tbar.remove(tbar.getComponent(0));//Editar
                            tbar.remove(tbar.getComponent(0));//Remover
                        },
                    }
                },
                preFilter: [
                    {
                        property: 'taxonomy_type',
                        value: cfg.params.taxonomy_type === undefined ? 0 : cfg.params.taxonomy_type,
                        stage: 100
                    }
                ]
            });
        }

        return this._classificationField;
    },

    getFormPanel: function(cfg) {
        if(!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                border: false,
                frame: true,
                items: [
                    {
                        xtype: 'hidden',
                        name: 'item',
                    },

                    {
                        xtype: 'hidden',
                        name: 'subitem',
                    },

                    this.getClassificationField(cfg)
                ]
            });

        return this._formPanel;
    },

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});

        Ext.applyIf(cfg, {
            width: 500,
        });

        raf.taxonomyclassification.Window.superclass.constructor.call(this, cfg);

    }
});
