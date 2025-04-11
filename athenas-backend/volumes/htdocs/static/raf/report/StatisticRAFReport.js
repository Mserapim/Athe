
Ext._define('raf.report.StatisticRAFReport', {
    extend: 'raf.report.BaseWindow',

    report: '/to/mpe/raf/raf_estatistico',

    _reportName: 'Estatístico - RAF',

    _filename: 'raf-estatistico',

    getValues: function() {
        var values = this.getFormPanel().getForm().getValues();
        var regex = /^(1[0-2]|0[1-9])\/(\d{4})$/;
        values.validate = true;
        if (values.grouped_by == 3) {
            values.validate = false;
            values.message = 'Opção em desenvolvimento ["Agrupar por: <b>MUNICÍPIO</b>"].';
        }
        values.areas = '';
        if (values.ckd_quest == 'on' ) { values.areas = values.areas + 'Q'; }
        if (values.ckd_item == 'on' ) {values.areas = values.areas + 'I'; }
        if (values.ckd_subitem == 'on' ) { values.areas = values.areas + 'S'; }
        if (values.ckd_municipios == 'on' ) { values.areas = values.areas + 'C'; }
        if (values.ckd_promotorias == 'on' ) {values.areas = values.areas + 'P'; }
        if (values.ckd_membros == 'on' ) { values.areas = values.areas + 'M'; }
        if (values.areas == '') {
            values.validate = false;
            values.message = 'Selecione pelo menos umas das opções em <b>Configurações > Áreas</b>.';
        }
        if (regex.test(values.initial_raf)) {
            values.initial_year = values.initial_raf.split("/")[1];
            values.initial_month = values.initial_raf.split("/")[0];
            if (regex.test(values.final_raf)) {
              values.final_year = values.final_raf.split("/")[1];
              values.final_month = values.final_raf.split("/")[0];
            } else {
              values.validate = false;
              values.message = 'RAF FINAL incorreto.<br/>Formato correto: <b>mm/aaaa</b>.';
            }
        } else {
          values.validate = false;
          values.message = 'RAF INICIAL incorreto.<br/>Formato correto: <b>mm/aaaa</b>.';
        }
        values.employee = this.getEmployeeField().getValues();
        values.location = this.getLocationField().getValues();
        values.county = this.getCountyField().getValues();
        values.classes = this.getClassField().getValues();
        values.matters = this.getMatterField().getValues();
        values.movements = this.getMovementField().getValues();
        if (values.employee == "" ) { values.employee = 0; }
        if (values.location == "" ) { values.location = 0; }
        if (values.county == "" ) { values.county = 0; }
        if (values.classes == "" ) { values.classes = 0; }
        if (values.matters == "" ) { values.matters = 0; }
        if (values.movements == "" ) { values.movements = 0; }
        return values;
    },

    generate: function(preventClose) {
        var values = this.getValues();
        if (values.validate) {
            engine.mq.Report.request({
                report: this.report,
                params: Ext.apply(
                    values,
                    {
                        outfile: this.filename(),
                        report_name: this.reportName()
                    }
                ),
                el: this.getEl(),
                waitMessage: 'Gerando relatório...',
            });
            if(!preventClose) this.close();
        } else {
            Ext.Msg.show({
              title: 'Status de Entrega do RAF',
              msg: values.message,
              icon: Ext.Msg.ERROR,
              buttons: Ext.Msg.OK
            });
        }
    },

    getEmployeeField: function(cfg) {
        if(!this._employeeField)
            this._employeeField = Ext._create('core.fields.MultiSelectField', {
                title: 'Membro',
                hideLabel: true,
                name: 'employee',
                hiddenName: 'employee',
                displayField: 'unicode',
                allowBlank: true,
                rest: 'raf.EmployeeRestful',
                preFilter: [
                    {property: 'tipo', value: 'M', stage: 100},
                ],
                gridConfig: {
                    columnAction: false,
                    hideColumns: ['departure_unicode', 'effective_unicode', 'commission_unicode', 'elective_unicode', 'ativo'],
                    hideItemsToolbar: ['add', 'edit', 'remove', 'download', 'filter'],
                },
                width: 415,
                height: 200,
                border: false
            });

        return this._employeeField;
    },

    getLocationField: function(cfg) {
        if(!this._locationField)
            this._locationField = Ext._create('core.fields.MultiSelectField', {
                title: 'Lotação',
                hideLabel: true,
                name: 'location',
                hiddenName: 'location',
                displayField: 'nome',
                allowBlank: true,
                rest: 'judicial.county.ExecutionOrganRestful',
                gridConfig: {
                    columnAction: false,
                    hideItemsToolbar: ['add', 'edit', 'remove', 'download', 'filter'],
                },
                width: 415,
                height: 200,
                border: false
            });

        return this._locationField;
    },

    getCountyField: function(cfg) {
        if(!this._countyField)
            this._countyField = Ext._create('core.fields.MultiSelectField', {
                title: 'Município',
                hideLabel: true,
                name: 'county',
                hiddenName: 'county',
                displayField: 'nome',
                allowBlank: true,
                rest: 'rh.localidade.Restful',
                preFilter: [
                    {property: 'estado__sigla', value: 'TO', stage: 100},
                ],
                gridConfig: {
                    columnAction: false,
                    hideItemsToolbar: ['add', 'edit', 'remove', 'download', 'filter'],
                },
                width: 415,
                height: 200,
                border: false
            });

        return this._countyField;
    },

    getClassField: function(cfg) {
        if(!this._classField)
            this._classField = Ext._create('core.fields.MultiSelectField', {
                title: 'Classes',
                hideLabel: true,
                name: 'classes',
                hiddenName: 'classes',
                gridField: 'title',
                findield: 'path_cache',
                allowBlank: true,
                rest: 'judicial.taxonomy.LegalClassRestful',
                gridConfig: {
                    columnAction: false,
                    hideItemsToolbar: ['add', 'edit', 'remove', 'download', 'filter'],
                },
                width: 415,
                height: 200,
                border: false
            });

        return this._classField;
    },

    getMatterField: function(cfg) {
        if(!this._matterField)
            this._matterField = Ext._create('core.fields.MultiSelectField', {
                title: 'Assunto',
                hideLabel: true,
                name: 'matters',
                hiddenName: 'matters',
                gridField: 'title',
                findield: 'path_cache',
                allowBlank: true,
                rest: 'judicial.taxonomy.LegalMatterRestful',
                gridConfig: {
                    columnAction: false,
                    hideItemsToolbar: ['add', 'edit', 'remove', 'download', 'filter'],
                },
                width: 415,
                height: 200,
                border: false
            });

        return this._matterField;
    },

    getMovementField: function(cfg) {
        if(!this._movementField)
            this._movementField = Ext._create('core.fields.MultiSelectField', {
                title: 'Movimento',
                hideLabel: true,
                name: 'movements',
                hiddenName: 'movementes',
                gridField: 'title',
                findield: 'path_cache',
                allowBlank: true,
                rest: 'judicial.taxonomy.LegalMovimentRestful',
                gridConfig: {
                    columnAction: false,
                    hideItemsToolbar: ['add', 'edit', 'remove', 'download', 'filter'],
                },
                width: 415,
                height: 200,
                border: false
            });

        return this._movementField;
    },

    getFormPanel: function() {
        if(!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                frame: true,
                border: false,
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
                                columnWidth: 0.21,
                                labelWidth: 60,
                                items: [
                                    {
                                        xtype:'fieldset',
                                        title: 'Período',
                                        collapsible: false,
                                        autoHeight:true,
                                        width: 260,
                                        items: [
                                            {
                                                xtype: 'textfield',
                                                fieldLabel: 'RAF Inicial',
                                                emptyText: 'mm/aaaa',
                                                regex: /^(1[0-2]|0[1-9])\/(\d{4})$/,
                                                regexText: 'Entrada inválida.<br/>Formato correto: <b>mm/aaaa</b>.',
                                                maxLength: 7,
                                                maxLengthText: 'Entrada inválida.<br/>Formato correto: <b>mm/aaaa</b>.',
                                                name: 'initial_raf',
                                            },
                                            {
                                                xtype: 'textfield',
                                                fieldLabel: 'RAF Final',
                                                emptyText: 'mm/aaaa',
                                                regex: /^(1[0-2]|0[1-9])\/(\d{4})$/,
                                                regexText: 'Entrada inválida.<br />Formato correto: <b>mm/aaaa</b>.',
                                                maxLength: 7,
                                                maxLengthText: 'Entrada inválida.<br />Formato correto: <b>mm/aaaa</b>.',
                                                name: 'final_raf',
                                            },
                                        ]
                                    },
                                ]
                            },
                            {
                                xtype:'panel',
                                autoHeight:true,
                                layout: 'form',
                                columnWidth: 0.79,
                                labelWidth: 70,
                                items: [
                                    {
                                        xtype:'fieldset',
                                        title: 'Configuração',
                                        collapsible: false,
                                        autoHeight:true,
                                        width: 1010,
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
                                                        columnWidth: 0.30,
                                                        labelWidth: 62,
                                                        items: [
                                                            {
                                                                fieldLabel: 'Disposição',
                                                                xtype: 'combo',
                                                                hiddenName: 'disposition',
                                                                width: 200,
                                                                triggerAction: 'all',
                                                                editable: false,
                                                                value: 1,
                                                                store: [
                                                                    [1, 'INDIVIDUAL'],
                                                                    [2, 'AGRUPADO']
                                                                ],
                                                            },
                                                        ]
                                                    },
                                                    {
                                                        xtype:'panel',
                                                        autoHeight:true,
                                                        layout: 'form',
                                                        columnWidth: 0.35,
                                                        labelWidth: 80,
                                                        items: [
                                                            {
                                                                fieldLabel: 'Organizar por',
                                                                xtype: 'combo',
                                                                hiddenName: 'grouped_by',
                                                                width: 200,
                                                                triggerAction: 'all',
                                                                editable: false,
                                                                value: 1,
                                                                store: [
                                                                    [1, 'ÓRGÃO DE EXECUÇÃO'],
                                                                    [2, 'MEMBRO'],
                                                                    [3, 'MUNICÍPIO'],
                                                                ],
                                                                listeners: {
                                                                    scope: this,
                                                                    select: function(index, scrollIntoView){
                                                                        if (index.value==1) {
                                                                            this.getFormPanel().getForm().findField('ckd_quest').enable();
                                                                            this.getFormPanel().getForm().findField('ckd_item').enable();
                                                                            this.getFormPanel().getForm().findField('ckd_subitem').enable();
                                                                            this.getFormPanel().getForm().findField('ckd_municipios').enable();
                                                                            this.getFormPanel().getForm().findField('ckd_promotorias').enable();
                                                                            this.getFormPanel().getForm().findField('ckd_membros').enable();
                                                                            this.getFormPanel().getForm().findField('ckd_x1').disable();
                                                                            this.getFormPanel().getForm().findField('ckd_x2').disable();
                                                                        }
                                                                        if (index.value==2) {
                                                                            this.getFormPanel().getForm().findField('ckd_quest').enable();
                                                                            this.getFormPanel().getForm().findField('ckd_item').enable();
                                                                            this.getFormPanel().getForm().findField('ckd_subitem').enable();
                                                                            this.getFormPanel().getForm().findField('ckd_municipios').enable();
                                                                            this.getFormPanel().getForm().findField('ckd_promotorias').enable();
                                                                            this.getFormPanel().getForm().findField('ckd_membros').enable();
                                                                            this.getFormPanel().getForm().findField('ckd_x1').disable();
                                                                            this.getFormPanel().getForm().findField('ckd_x2').disable();
                                                                        }
                                                                        if (index.value==3) {
                                                                            this.getFormPanel().getForm().findField('ckd_quest').disable();
                                                                            this.getFormPanel().getForm().findField('ckd_item').disable();
                                                                            this.getFormPanel().getForm().findField('ckd_subitem').disable();
                                                                            this.getFormPanel().getForm().findField('ckd_municipios').disable();
                                                                            this.getFormPanel().getForm().findField('ckd_promotorias').disable();
                                                                            this.getFormPanel().getForm().findField('ckd_membros').disable();
                                                                            this.getFormPanel().getForm().findField('ckd_x1').disable();
                                                                            this.getFormPanel().getForm().findField('ckd_x2').disable();
                                                                        }
                                                                    }
                                                                }
                                                            },
                                                        ]
                                                    },
                                                    {
                                                        xtype:'panel',
                                                        autoHeight:true,
                                                        layout: 'form',
                                                        columnWidth: 0.30,
                                                        labelWidth: 40,
                                                        items: [
                                                            {
                                                                fieldLabel: 'Layout',
                                                                xtype: 'combo',
                                                                hiddenName: 'layout',
                                                                width: 200,
                                                                triggerAction: 'all',
                                                                editable: false,
                                                                value: 1,
                                                                store: [
                                                                    [1, 'LISTAGEM/GRÁFICO'],
                                                                    [2, 'LISTAGEM'],
                                                                    [3, 'GRÁFICO'],
                                                                ],
                                                            },
                                                        ]
                                                    },
                                                    {
                                                        xtype:'panel',
                                                        autoHeight:true,
                                                        layout: 'form',
                                                        labelWidth: 1,
                                                        columnWidth: 0.5,
                                                        items: [

                                                        ]
                                                    },
                                                ]
                                            },
                                            {
                                                xtype:'fieldset',
                                                title: 'Áreas',
                                                collapsible: false,
                                                autoHeight:true,
                                                width: 985,
                                                items: [
                                                    {
                                                        xtype:'panel',
                                                        autoHeight:true,
                                                        layout: 'column',
                                                        labelWidth: 1,
                                                        items: [
                                                            {
                                                                xtype:'panel',
                                                                autoHeight:true,
                                                                layout: 'form',
                                                                columnWidth: 0.25,
                                                                items: [
                                                                    {
                                                                        xtype: 'checkbox',
                                                                        id: 'ckd_quest',
                                                                        name: 'ckd_quest',
                                                                        boxLabel: 'Questionários',
                                                                        checked: true,
                                                                    },
                                                                    {
                                                                        xtype: 'checkbox',
                                                                        id: 'ckd_item',
                                                                        name: 'ckd_item',
                                                                        boxLabel: 'Itens/Assuntos',
                                                                        checked: true,
                                                                    },
                                                                ]
                                                            },
                                                            {
                                                                xtype:'panel',
                                                                autoHeight:true,
                                                                layout: 'form',
                                                                columnWidth: 0.25,
                                                                items: [
                                                                    {
                                                                        xtype: 'checkbox',
                                                                        id: 'ckd_subitem',
                                                                        name: 'ckd_subitem',
                                                                        boxLabel: 'Subitens/Movimentos',
                                                                        checked: true,
                                                                    },
                                                                    {
                                                                        xtype: 'checkbox',
                                                                        id: 'ckd_municipios',
                                                                        name: 'ckd_municipios',
                                                                        boxLabel: 'Municípios',
                                                                        checked: true,
                                                                    },

                                                                ]
                                                            },
                                                            {
                                                                xtype:'panel',
                                                                autoHeight:true,
                                                                layout: 'form',
                                                                columnWidth: 0.25,
                                                                items: [
                                                                    {
                                                                        xtype: 'checkbox',
                                                                        id: 'ckd_membros',
                                                                        name: 'ckd_membros',
                                                                        boxLabel: 'Membros',
                                                                        checked: true,
                                                                    },
                                                                    {
                                                                        xtype: 'checkbox',
                                                                        id: 'ckd_promotorias',
                                                                        name: 'ckd_promotorias',
                                                                        boxLabel: 'Promotorias',
                                                                        checked: true,
                                                                    },
                                                                ]
                                                            },
                                                            {
                                                                xtype:'panel',
                                                                autoHeight:true,
                                                                layout: 'form',
                                                                columnWidth: 0.25,
                                                                items: [
                                                                    {
                                                                        xtype: 'checkbox',
                                                                        id: 'ckd_x1',
                                                                        name: 'ckd_x1',
                                                                        boxLabel: 'X1',
                                                                        checked: true,
                                                                        disabled: true,
                                                                    },
                                                                    {
                                                                        xtype: 'checkbox',
                                                                        id: 'ckd_x2',
                                                                        name: 'ckd_x2',
                                                                        boxLabel: 'X2',
                                                                        checked: true,
                                                                        disabled: true,
                                                                    },
                                                                ]
                                                            },
                                                        ]
                                                    },
                                                ]
                                            },
                                        ]
                                    },
                                ]
                            },
                        ]
                    },
                    {
                        xtype:'fieldset',
                        title: 'Opções de Filtro',
                        collapsible: false,
                        autoHeight:true,
                        labelWidth: 55,
                        width: 1285,
                        items: [
                            {
                                xtype:'panel',
                                autoHeight:true,
                                layout: 'column',
                                width: 1280,
                                items: [
                                    {
                                        xtype:'panel',
                                        autoHeight:true,
                                        layout: 'form',
                                        columnWidth: 0.33,
                                        labelWidth: 70,
                                        items: [
                                            this.getEmployeeField(),
                                        ]
                                    },
                                    {
                                        xtype:'panel',
                                        autoHeight:true,
                                        layout: 'form',
                                        columnWidth: 0.33,
                                        labelWidth: 70,
                                        items: [
                                            this.getLocationField(),
                                        ]
                                    },
                                    {
                                        xtype:'panel',
                                        autoHeight:true,
                                        layout: 'form',
                                        columnWidth: 0.33,
                                        labelWidth: 70,
                                        items: [
                                            this.getCountyField(),
                                        ]
                                    },
                                ]
                            },
                            {
                                xtype:'panel',
                                autoHeight:true,
                                layout: 'column',
                                width: 1280,
                                items: [
                                    {
                                        xtype:'panel',
                                        autoHeight:true,
                                        layout: 'form',
                                        columnWidth: 0.33,
                                        labelWidth: 70,
                                        items: [
                                            this.getClassField(),
                                        ]
                                    },
                                    {
                                        xtype:'panel',
                                        autoHeight:true,
                                        layout: 'form',
                                        columnWidth: 0.33,
                                        labelWidth: 70,
                                        items: [
                                            this.getMatterField(),
                                        ]
                                    },
                                    {
                                        xtype:'panel',
                                        autoHeight:true,
                                        layout: 'form',
                                        columnWidth: 0.33,
                                        labelWidth: 70,
                                        items: [
                                            this.getMovementField(),
                                        ]
                                    },
                                ]
                            },
                        ]
                    },
                ]
            });
        return this._formPanel;
    },

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});
        Ext.applyIf(
            cfg,
            {
                title: this.reportName(),
                width: 1315,
            }
        );
        Ext.apply(
            cfg,
            { }
        );
        raf.report.StatisticRAFReport.superclass.constructor.call(this, cfg);
    }
});
