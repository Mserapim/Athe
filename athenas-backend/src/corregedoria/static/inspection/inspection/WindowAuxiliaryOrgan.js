Ext._define('corregedoria.inspection.inspection.WindowAuxiliaryOrgan', {
    extend: 'core.RestfulWindow',

    rest: 'corregedoria.inspection.inspection.Restful',
    // width: 810,
    // title: this.title + ' - Órgão Auxiliar',

    getInspectorGeneralField: function() {
        if(!this._inspectorGeneralField) {
            this._inspectorGeneralField = Ext._create('core.fields.AutocompleteField', {
                xtype: "rest-autocompletefield",
                fieldLabel: 'Corregedor-Geral',
                allowBlank: true,
                rest: "raf.EmployeeRestful",
                name: "inspector_general",
                disabled: false,
                preFilter: [
                    {property: 'tipo', value: 'M', stage: 100},
                ],
                gridConfig: {
                    columnAction: false,
                    hideColumns: ['departure_unicode', 'effective_unicode', 'commission_unicode', 'elective_unicode', 'ativo'],
                    hideItemsToolbar: ['add', 'edit', 'remove', 'download', 'filter'],
                }
            });
        }
        return this._inspectorGeneralField;
    },

    // getInspectorProsecutorField: function() {
    //     if(!this._inspectorProsecutorField) {
    //         this._inspectorProsecutorField = Ext._create('core.fields.AutocompleteField', {
    //             xtype: "rest-autocompletefield",
    //             fieldLabel: 'Promotor-Corregedor',
    //             allowBlank: true,
    //             rest: "raf.EmployeeRestful",
    //             name: "inspector_prosecutor",
    //             disabled: false,
    //             preFilter: [
    //                 {property: 'tipo', value: 'M', stage: 100},
    //             ],
    //             gridConfig: {
    //                 columnAction: false,
    //                 hideColumns: ['departure_unicode', 'effective_unicode', 'commission_unicode', 'elective_unicode', 'ativo'],
    //                 hideItemsToolbar: ['add', 'edit', 'remove', 'download', 'filter'],
    //             }
    //         });
    //     }
    //     return this._inspectorProsecutorField;
    // },

    getInspectorProsecutorsField: function(cfg) {
      if(!this._inspectorProsecutorsField)
          this._inspectorProsecutorsField = Ext._create('core.fields.RelatedRestfulField', {
            title: 'Promotores-Corregedores',
            hideLabel: true,
            name: 'inspector_prosecutors',
            displayField: 'unicode',
            allowBlank: true,
            relatedname: 'inspector_prosecutors',
            rest: this.rest,
            sourceRest: 'raf.EmployeeRestful',
            oId: this.oId || cfg.oId,
            width: 763,
            height: 170,
            border: false,
            preFilter: [
                {property: 'tipo', value: 'M', stage: 100},
            ],
            gridConfig: {
                columnAction: false,
                hideColumns: ['departure_unicode', 'effective_unicode', 'commission_unicode', 'elective_unicode', 'ativo'],
                hideItemsToolbar: ['add', 'edit', 'remove', 'download', 'filter'],
            }
          });
      return this._inspectorProsecutorsField;
    },

    getExecutionOrganField: function() {
        if(!this._locationField) {
            this._locationField = Ext._create('core.fields.AutocompleteField', {
                xtype: "rest-autocompletefield",
                fieldLabel: "Órgão Inspecionado",
                allowBlank: true,
                rest: "rh.workplace.Restful",
                id: "execution_organ",
                name: "execution_organ",
                disabled: false,
                gridConfig: {
                    columnAction: false,
                    // hideColumns: ['habilita_protocolo', 'ativo', 'sigla', 'general_distribution', 'replacements', 'owner_unicode', 'employee_exercise_unicode'],
                    hideItemsToolbar: ['add', 'edit', 'remove', 'download'],
                },
            });
        }
        // this._locationField.getComboField().addListener('change', function(combo, record, index) { this.onChangeExecutionOrgan(record.id); }, this);
        return this._locationField;
    },

    getFormPanel: function(cfg) {
        if(!this._formPanel) {
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                border: false,
                frame: true,
                items: [
                    {
                        xtype:'fieldset',
                        title: '1. Dados da Inspeção',
                        collapsible: false,
                        width: 783,
                        height: 243,
                        items: [
                            {
                                xtype:'panel',
                                autoHeight:true,
                                layout: 'column',
                                items: [
                                    {
                                        xtype:'panel',
                                        autoHeight:true,
                                        layout: 'form',
                                        labelWidth: 30,
                                        columnWidth: 0.21,
                                        items: [
                                            {
                                                xtype: 'datefield',
                                                fieldLabel: 'Início',
                                                name: 'inspection_date_initial',
                                                allowBlank: false,
                                                blankText: 'Data da Inspeção precisa ser preenchida.',
                                            },
                                        ]

                                    },
                                    {
                                        xtype:'panel',
                                        autoHeight:true,
                                        layout: 'form',
                                        labelWidth: 30,
                                        columnWidth: 0.21,
                                        items: [
                                            {
                                                xtype: 'datefield',
                                                fieldLabel: 'Final',
                                                name: 'inspection_date_final',
                                                allowBlank: false,
                                                blankText: 'Data da Inspeção precisa ser preenchida.',
                                            },
                                        ]

                                    },
                                    {
                                        xtype:'panel',
                                        autoHeight:true,
                                        layout: 'form',
                                        labelWidth: 50,
                                        columnWidth: 0.22,
                                        items: [
                                            {
                                                xtype: "textfield",
                                                fieldLabel: "Edital nº",
                                                name: "notice",
                                                width: 90,
                                                allowBlank: false,
                                            },
                                        ]

                                    },
                                    {
                                        xtype:'panel',
                                        autoHeight:true,
                                        labelWidth: 115,
                                        layout: 'form',
                                        columnWidth: 0.36,
                                        items: [
                                            {
                                                xtype: "textfield",
                                                fieldLabel: "Publicação do Edital",
                                                name: "publication",
                                                width: 150,
                                                allowBlank: false,
                                            },
                                        ]

                                    },
                                ]
                            },
                            {
                                xtype:'panel',
                                autoHeight:true,
                                labelWidth: 100,
                                layout: 'form',
                                items: [
                                    this.getInspectorGeneralField(),
                                    this.getInspectorProsecutorsField(cfg),
                                ],
                            },
                        ]
                    },
                    {
                        xtype:'fieldset',
                        title: '2. Dados Gerais',
                        labelWidth: 115,
                        collapsible: false,
                        autoHeight:true,
                        width: 783,
                        items: [
                            this.getExecutionOrganField(),
                            // this.getResponsibleField(), // coordenador
                            {
                                xtype:'panel',
                                autoHeight:true,
                                labelWidth: 80,
                                layout: 'form',
                                items: [
                                    {
                                        xtype: 'textarea',
                                        fieldLabel: 'Observações',
                                        name: 'observation',
                                        hideLabel: false,
                                        width: 675,
                                        height: 40,
                                    },
                                ]
                            }
                        ]
                    },

                ]
            });
        }
        return this._formPanel;
    },

    observer: function(cfg) {
        if (this.oId) {
            this.getInspectorProsecutorsField(cfg).objectId(this.oId);
        }
    },

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});

        Ext.applyIf(cfg, {
            title: 'Novo - Órgão Auxiliar',
            width: 810,
            disableSaveAndNew: true,
            saveAndContinue: {
                scope: this,
                fn: function(instance) {
                    this.getFormPanel(cfg).getForm().setValues(instance);
                    this.oId = instance.pk;
                    this.action = 'update';
                    this.observer(cfg);
                }
            }
        });
        corregedoria.inspection.inspection.WindowAuxiliaryOrgan.superclass.constructor.call(this, cfg);
        this.observer(cfg);
    }
});
