Ext._define('corregedoria.inspection.inspection.filling.administrativeorganization.proceduresinprogress.Window', {
    extend: 'core.RestfulWindow',

    rest: 'corregedoria.inspection.inspection.filling.administrativeorganization.proceduresinprogress.Restful',

    width: 600,

    getTaxonomyClassField: function(cfg) {
        if(!this._taxnomyClassField) {
            this._taxnomyClassField = Ext._create('core.fields.AutocompleteField', {
                xtype: "rest-autocompletefield",
                fieldLabel: "Tipo",
                allowBlank: true,
                rest: "judicial.taxonomy.LegalClassRestful",
                name: "taxonomy_class",
                disabled: false,
                gridConfig: {
                    columnAction: false,
                    hideItemsToolbar:['add', 'edit', 'remove', '-', 'download'],
                    // params: {inspection: cfg.values.inspection_id},
                }
            });
        }
        return this._taxnomyClassField;
    },

    getTaxonomyMatterField: function(cfg) {
        if(!this._taxnomyMatterField) {
            this._taxnomyMatterField = Ext._create('core.fields.AutocompleteField', {
                xtype: "rest-autocompletefield",
                fieldLabel: "Assunto",
                allowBlank: true,
                rest: "judicial.taxonomy.LegalMatterRestful",
                name: "taxonomy_matter",
                disabled: false,
                gridConfig: {
                    columnAction: false,
                    hideItemsToolbar:['add', 'edit', 'remove', '-', 'download'],
                    // params: {inspection: cfg.values.inspection_id},
                }
            });
        }
        return this._taxnomyMatterField;
    },

    getFormPanel: function(cfg) {
        if(!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                border: false,
                frame: true,
                items: [
                    {
                        xtype:'panel',
                        autoHeight:true,
                        layout: 'column',
                        items: [
                            {
                                xtype:'panel',
                                autoHeight:true,
                                labelWidth: 70,
                                columnWidth: 0.40,
                                layout: 'form',
                                items: [
                                    {
                                        xtype:'panel',
                                        autoHeight:true,
                                        layout: 'form',
                                        labelWidth: 50,
                                        items: [
                                            {
                                                xtype: 'textfield',
                                                fieldLabel: 'Número',
                                                name: 'number',
                                                hideLabel: false,
                                                width: 150,
                                            },
                                        ]
                                    },
                                ]
                            },
                            {
                                xtype:'panel',
                                autoHeight:true,
                                labelWidth: 70,
                                columnWidth: 0.60,
                                layout: 'form',
                                items: [
                                    {
                                        xtype:'panel',
                                        autoHeight:true,
                                        labelWidth: 115,
                                        layout: 'form',
                                        items: [
                                            {
                                                xtype: 'datefield',
                                                fieldLabel: 'Data de Instauração',
                                                width: 150,
                                                name: 'instauration_date',
                                            },
                                        ]
                                    },
                                ]
                            },
                        ]
                    },
                    {
                        xtype:'panel',
                        autoHeight:true,
                        labelWidth: 30,
                        layout: 'form',
                        items: [
                            this.getTaxonomyClassField(cfg),
                        ]
                    },
                    {
                        xtype:'panel',
                        autoHeight:true,
                        labelWidth: 50,
                        layout: 'form',
                        items: [
                            this.getTaxonomyMatterField(cfg),
                            {
                                xtype: 'textarea',
                                fieldLabel: '',
                                name: 'matter',
                                hideLabel: false,
                                allowBlank: true,
                                width: 517,
                                height: 35,
                            },
                        ]
                    },
                    {
                        xtype:'panel',
                        autoHeight:true,
                        labelWidth: 77,
                        layout: 'form',
                        items: [
                            {
                                xtype: 'textarea',
                                fieldLabel: 'Observações',
                                name: 'observation',
                                hideLabel: false,
                                allowBlank: true,
                                width: 490,
                                height: 50,
                            },
                        ]
                    },
                ]
            });

        return this._formPanel;
    },
});
