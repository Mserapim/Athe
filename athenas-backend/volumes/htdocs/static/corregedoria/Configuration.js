Ext._define('corregedoria.Configuration', {
    extend: 'toolkit.widget.TabPanel',


    getFromTypeMemberGrid: function() {
        var self = this;

        if(!this._fromTypeMember) {
            this._fromTypeMember = Ext._create('standard.ChoiceGrid', {
                title: 'Disponível',
                border: true,
                flex: 1,
                doubleClickHandler: function() { self.addAutoCreateForTypeMember(); },
                gridAutoLoad: false,
                columnAction: false,
                hideColumns: [ 'app_label', 'name', 'value', 'cvalue', 'order_weight', 'active', 'description', ],
            });

            for(var x = 0; x < 4; x++)
                this._fromTypeMember.getToolbar().remove(0);

            this._fromTypeMember.addFilterProperty('app_label', 'rh', 100, false);
            this._fromTypeMember.addFilterProperty('name', 'CLASSIF_EMPLOYEE_BY_POSSESSION', 101, false);
            this._fromTypeMember.setFilterProperty('cvalue__in', core.nullValue(this._valuesMember.autoCreateForTypeMember, []), -1000);
        }

        return this._fromTypeMember;
    },

    getToTypeMemberGrid: function() {
        var self = this;

        if(!this._toTypeMember) {
            this._toTypeMember = Ext._create('standard.ChoiceGrid', {
                title: 'Selecionado',
                border: true,
                flex: 1,
                doubleClickHandler: function() { self.removeAutoCreateForTypeMember(); },
                gridAutoLoad: false,
                columnAction: false,
                hideColumns: [ 'app_label', 'name', 'value', 'cvalue', 'order_weight', 'active', 'description', ],
            });

            for(var x = 0; x < 4; x++)
                this._toTypeMember.getToolbar().remove(0);

            this._toTypeMember.setFilterProperty('cvalue__in', core.nullValue(this._valuesMember.autoCreateForTypeMember, []), 1000);
        }

        return this._toTypeMember;
    },

    getTypeMemberField: function() {
        if(!this._typeMemberField)
            this._typeMemberField = Ext._create('Ext.form.FieldSet', {
                title: 'Tipo',
                collapsible: false,
                collapsed: false,
                layout: {
                    type: 'hbox',
                    align: 'stretchmax',
                    padding: '0 0 6 0'
                },
                items: [
                    this.getFromTypeMemberGrid(),
                    {
                        width: 35,
                        height: 200,
                        xtype: 'container',
                        frame: true,
                        layout: {
                            type: 'vbox',
                            align: 'stretchmax',
                            padding: '6'
                        },
                        items: [
                            {
                                xtype: 'container',
                                flex: 1
                            },
                            {
                                xtype: 'container',
                                defaults: {
                                    xtype: 'button',
                                    width: 24,
                                    height: 24,
                                    style: {
                                        marginBottom: '5px'
                                    }
                                },
                                items: [
                                    {
                                        iconCls: 'icon-core icon-core-add-all',
                                        scope: this,
                                        handler: function() {this.addAllAutoCreateForTypeMember(); }
                                    },
                                    {
                                        iconCls: 'icon-core icon-core-add-selected',
                                        scope: this,
                                        handler: function() {this.addAutoCreateForTypeMember(); }
                                    },
                                    {
                                        iconCls: 'icon-core icon-core-remove-selected',
                                        scope: this,
                                        handler: function() {this.removeAutoCreateForTypeMember(); }
                                    },
                                    {
                                        iconCls: 'icon-core icon-core-remove-all',
                                        scope: this,
                                        handler: function() {this.removeAllAutoCreateForTypeMember(); }
                                    }
                                ]
                            },
                            {
                                xtype: 'container',
                                flex: 1
                            }
                        ]
                    },
                    this.getToTypeMemberGrid()
                ]
            });

        return this._typeMemberField;
    },

    removeAllAutoCreateForTypeMember: function() {
        var selected = [];

        this.getToTypeMemberGrid().getStore().each(
            function(data) {
                selected.push(data.get('cvalue'));
            }
        );

        this.removeAutoCreateForTypeMember(selected);
    },

    removeAutoCreateForTypeMember: function(selected) {
        selected = core.nullValue(
            selected,
            this.getToTypeMemberGrid().getSelectionModel().getSelections().map(
                function(data) {
                    return data.get('cvalue');
                }
            )
        );

        if(selected.length > 0) {
            var value = this.autoCreateForTypeMember();
            selected.map(function(pk) { value.remove(pk); });
            this.autoCreateForTypeMember(value);
        }
        else
            Ext.Msg.show({
                'title': 'Removendo',
                'icon': Ext.Msg.ERROR,
                'buttons': Ext.Msg.OK,
                'msg': 'Primeiro selecione os itens a serem removidos.'
            });
    },

    addAllAutoCreateForTypeMember: function() {
        var selected = [];

        this.getFromTypeMemberGrid().getStore().each(
            function(data) {
                selected.push(data.get('cvalue'));
            }
        );

        this.addAutoCreateForTypeMember(selected);
    },

    addAutoCreateForTypeMember: function(selected) {
        selected = core.nullValue(
            selected,
            this.getFromTypeMemberGrid().getSelectionModel().getSelections().map(
                function(data) {
                    return data.get('cvalue');
                }
            )
        );

        if(selected.length > 0) {
            selected = selected.concat(this.autoCreateForTypeMember());
            this.autoCreateForTypeMember(selected);
        }
        else
            Ext.Msg.show({
                'title': 'Adicionando',
                'icon': Ext.Msg.ERROR,
                'buttons': Ext.Msg.OK,
                'msg': 'Primeiro selecione os itens a serem adiconados.'
            });
    },

    autoCreateForTypeMember: function(value, persist) {
        persist = core.nullValue(persist, true);

        if(value !== undefined) {
            this.getToTypeMemberGrid().setFilterProperty('cvalue__in', value, 1000);
            this.getFromTypeMemberGrid().setFilterProperty('cvalue__in', value, -1000);

            this._autoCreateForTypeMember = value;

            if(persist) {
                Ext.Ajax.request({
                    url: core.callAction('CORREGEDORIAConfiguration', 'write'),
                    params: {
                        property: 'autoCreateForTypeMember',
                        value: Ext.encode(this._autoCreateForTypeMember)
                    }
                });
            }
        }

        return this._autoCreateForTypeMember;
    },

    getFromTypeEmployeeGrid: function() {
        var self = this;

        if(!this._fromTypeEmployee) {
            this._fromTypeEmployee = Ext._create('standard.ChoiceGrid', {
                title: 'Disponível',
                border: true,
                flex: 1,
                doubleClickHandler: function() { self.addAutoCreateForTypeEmployee(); },
                gridAutoLoad: false,
                columnAction: false,
                hideColumns: [ 'app_label', 'name', 'value', 'cvalue', 'order_weight', 'active', 'description', ],
            });

            for(var x = 0; x < 4; x++)
                this._fromTypeEmployee.getToolbar().remove(0);

            this._fromTypeEmployee.addFilterProperty('app_label', 'rh', 100, false);
            this._fromTypeEmployee.addFilterProperty('name', 'CLASSIF_EMPLOYEE_BY_POSSESSION', 101, false);
            this._fromTypeEmployee.setFilterProperty('cvalue__in', core.nullValue(this._valuesEmployee.autoCreateForTypeEmployee, []), -1000);
        }

        return this._fromTypeEmployee;
    },

    getToTypeEmployeeGrid: function() {
        var self = this;

        if(!this._toTypeEmployee) {
            this._toTypeEmployee = Ext._create('standard.ChoiceGrid', {
                title: 'Selecionado',
                border: true,
                flex: 1,
                doubleClickHandler: function() { self.removeAutoCreateForTypeEmployee(); },
                gridAutoLoad: false,
                columnAction: false,
                hideColumns: [ 'app_label', 'name', 'value', 'cvalue', 'order_weight', 'active', 'description', ],
            });

            for(var x = 0; x < 4; x++)
                this._toTypeEmployee.getToolbar().remove(0);

            this._toTypeEmployee.setFilterProperty('cvalue__in', core.nullValue(this._valuesEmployee.autoCreateForTypeEmployee, []), 1000);
        }

        return this._toTypeEmployee;
    },

    getTypeEmployeeField: function() {
        if(!this._typeEmployeeField)
            this._typeEmployeeField = Ext._create('Ext.form.FieldSet', {
                title: 'Tipo',
                collapsible: false,
                collapsed: false,
                layout: {
                    type: 'hbox',
                    align: 'stretchmax',
                    padding: '0 0 6 0'
                },
                items: [
                    this.getFromTypeEmployeeGrid(),
                    {
                        width: 35,
                        height: 200,
                        xtype: 'container',
                        frame: true,
                        layout: {
                            type: 'vbox',
                            align: 'stretchmax',
                            padding: '6'
                        },
                        items: [
                            {
                                xtype: 'container',
                                flex: 1
                            },
                            {
                                xtype: 'container',
                                defaults: {
                                    xtype: 'button',
                                    width: 24,
                                    height: 24,
                                    style: {
                                        marginBottom: '5px'
                                    }
                                },
                                items: [
                                    {
                                        iconCls: 'icon-core icon-core-add-all',
                                        scope: this,
                                        handler: function() {this.addAllAutoCreateForTypeEmployee(); }
                                    },
                                    {
                                        iconCls: 'icon-core icon-core-add-selected',
                                        scope: this,
                                        handler: function() {this.addAutoCreateForTypeEmployee(); }
                                    },
                                    {
                                        iconCls: 'icon-core icon-core-remove-selected',
                                        scope: this,
                                        handler: function() {this.removeAutoCreateForTypeEmployee(); }
                                    },
                                    {
                                        iconCls: 'icon-core icon-core-remove-all',
                                        scope: this,
                                        handler: function() {this.removeAllAutoCreateForTypeEmployee(); }
                                    }
                                ]
                            },
                            {
                                xtype: 'container',
                                flex: 1
                            }
                        ]
                    },
                    this.getToTypeEmployeeGrid()
                ]
            });

        return this._typeEmployeeField;
    },

    removeAllAutoCreateForTypeEmployee: function() {
        var selected = [];

        this.getToTypeEmployeeGrid().getStore().each(
            function(data) {
                selected.push(data.get('cvalue'));
            }
        );

        this.removeAutoCreateForTypeEmployee(selected);
    },

    removeAutoCreateForTypeEmployee: function(selected) {
        selected = core.nullValue(
            selected,
            this.getToTypeEmployeeGrid().getSelectionModel().getSelections().map(
                function(data) {
                    return data.get('cvalue');
                }
            )
        );

        if(selected.length > 0) {
            var value = this.autoCreateForTypeEmployee();
            selected.map(function(pk) { value.remove(pk); });
            this.autoCreateForTypeEmployee(value);
        }
        else
            Ext.Msg.show({
                'title': 'Removendo',
                'icon': Ext.Msg.ERROR,
                'buttons': Ext.Msg.OK,
                'msg': 'Primeiro selecione os itens a serem removidos.'
            });
    },

    addAllAutoCreateForTypeEmployee: function() {
        var selected = [];

        this.getFromTypeEmployeeGrid().getStore().each(
            function(data) {
                selected.push(data.get('cvalue'));
            }
        );

        this.addAutoCreateForTypeEmployee(selected);
    },

    addAutoCreateForTypeEmployee: function(selected) {
        selected = core.nullValue(
            selected,
            this.getFromTypeEmployeeGrid().getSelectionModel().getSelections().map(
                function(data) {
                    return data.get('cvalue');
                }
            )
        );

        if(selected.length > 0) {
            selected = selected.concat(this.autoCreateForTypeEmployee());
            this.autoCreateForTypeEmployee(selected);
        }
        else
            Ext.Msg.show({
                'title': 'Adicionando',
                'icon': Ext.Msg.ERROR,
                'buttons': Ext.Msg.OK,
                'msg': 'Primeiro selecione os itens a serem adiconados.'
            });
    },

    autoCreateForTypeEmployee: function(value, persist) {
        persist = core.nullValue(persist, true);

        if(value !== undefined) {
            this.getToTypeEmployeeGrid().setFilterProperty('cvalue__in', value, 1000);
            this.getFromTypeEmployeeGrid().setFilterProperty('cvalue__in', value, -1000);

            this._autoCreateForTypeEmployee = value;

            if(persist) {
                Ext.Ajax.request({
                    url: core.callAction('CORREGEDORIAConfiguration', 'write'),
                    params: {
                        property: 'autoCreateForTypeEmployee',
                        value: Ext.encode(this._autoCreateForTypeEmployee)
                    }
                });
            }
        }

        return this._autoCreateForTypeEmployee;
    },

    dataReload: function() {
        if (!this._values) {
            this._config = core.nullValue(this.config, {});
            this._values = {};
            Ext.Ajax.request({
                url: core.callAction('CORREGEDORIAConfiguration', 'read'),
                scope: this,
                success: function(xhr) {
                    var rst = Ext.decode(xhr.responseText);

                    if(rst.success) {
                        this.autoCreateForTypeMember(
                            rst.config.autoCreateForTypeMember != undefined ? Ext.decode(rst.config.autoCreateForTypeMember) : rst.config.autoCreateForTypeMember,
                            false
                        );
                        this.autoCreateForTypeEmployee(
                            rst.config.autoCreateForTypeEmployee != undefined ? Ext.decode(rst.config.autoCreateForTypeEmployee) : rst.config.autoCreateForTypeEmployee,
                            false
                        );
                        this.getFormPanel().getForm().setValues(rst.config);
                    }
                }
            });
        }
        return this._values;
    },

    saveConfiguration: function() {
        var values =

        Ext.Ajax.request({
            url: core.callAction('CORREGEDORIAConfiguration', 'save'),
            scope: this,
            params: this.getFormPanel().getForm().getValues(),
            success: function(xhr) {
                var rst = Ext.decode(xhr.responseText);
                var message, tipo;

                if(rst.success) {
                    message = 'Configurações persistidas com sucesso';
                    tipo = Ext.Msg.INFO;
                }
                else {
                    tipo = Ext.Msg.ERROR;
                    message = rst.message;
                }

                Ext.Msg.show({
                    title: 'Gravando configurações',
                    icon: tipo,
                    buttons: Ext.Msg.OK,
                    msg: message
                });
            }
        });
    },

    getScoreTableGrid: function() {
        if(!this._scoreTableGrid) {
            this._scoreTableGrid = Ext._create('corregedoria.scoretable.Grid', {
                region: 'center',
                layout: 'form',
                border: true,
                height: 450,
                gridAutoLoad: true,
                columnAction: false,
                hideItemsToolbar:['download', ],
                doubleClickHandler: function() { },
            });
        }
        return this._scoreTableGrid;
    },

    getLinkInspectionRAFGrid: function() {
        if(!this._linkInspectionRAFGrid) {
            this._linkInspectionRAFGrid = Ext._create('corregedoria.linkinspectionraf.Grid', {
                region: 'center',
                layout: 'form',
                border: true,
                height: 610,
                width: 1110,
                gridAutoLoad: true,
                columnAction: false,
                hideItemsToolbar:['edit', 'download',],
                sm: new Ext.grid.RowSelectionModel({singleSelect:true}),
            });
        }
        return this._linkInspectionRAFGrid;
    },

    getProductuvityGrid: function() {
        if(!this._productivityGrid) {
            this._productivityGrid = Ext._create('corregedoria.productivity.Grid', {
                region: 'center',
                layout: 'form',
                border: true,
                height: 300,
                gridAutoLoad: true,
                columnAction: false,
                hideItemsToolbar:['edit', 'download',],
                doubleClickHandler: function() { },
            });
        }
        return this._productivityGrid;
    },

    getInspectorGeneralField: function() {
        if(!this._inspectorGeneralField) {
            this._inspectorGeneralField = Ext._create('core.fields.AutocompleteField', {
                xtype: "rest-autocompletefield",
                fieldLabel: 'Corregedor-geral',
                allowBlank: true,
                rest: "rh.employee.Restful",
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

    getFormPanel: function(val) {
        if(!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                border: false,
                autoScroll: true,
                region: 'center',
                layout: 'form',
                padding: '10',
                items: [
                    {
                        xtype: 'fieldset',
                        title: '',
                        layout: 'form',
                        collapsible: false,
                        collapsed: false,
                        labelWidth: 100,
                        items: [
                            this.getInspectorGeneralField(),
                        ]
                    },
                    {
                        xtype: 'fieldset',
                        title: 'Gestor de Inspeção',
                        collapsible: true,
                        collapsed: true,
                        layout: {
                            type: 'hbox',
                            align: 'center',
                        },
                        items: [
                            {
                                xtype: 'fieldset',
                                title: '',
                                layout: 'form',
                                collapsible: false,
                                collapsed: false,
                                items: [
                                    {
                                        xtype: 'fieldset',
                                        title: 'Regularidade dos serviços',
                                        layout: 'form',
                                        collapsible: false,
                                        collapsed: false,
                                        labelWidth: 300,
                                        items: [
                                            {
                                                xtype: 'choicefield',
                                                fieldLabel: 'Registro de Atendimento ao Público',
                                                hiddenName: 'var_registerpublicattendance',
                                                width: 365,
                                                choiceId: 'corregedoria.INSPECTION_TABLE',
                                            },
                                            {
                                                xtype: 'choicefield',
                                                fieldLabel: 'Registro de Processos Judiciais Recebidos',
                                                hiddenName: 'var_courtlawsuitreceived',
                                                width: 365,
                                                choiceId: 'corregedoria.INSPECTION_TABLE',
                                            },
                                            {
                                                xtype: 'choicefield',
                                                fieldLabel: 'Registro de Processos Judiciais Devolvidos',
                                                hiddenName: 'var_courtlawsuitreturned',
                                                width: 365,
                                                choiceId: 'corregedoria.INSPECTION_TABLE',
                                            },
                                            {
                                                xtype: 'choicefield',
                                                fieldLabel: 'Registro de Processos Judiciais Eleitorais Recebidos',
                                                hiddenName: 'var_courtlawsuitelectoralreceived',
                                                width: 365,
                                                choiceId: 'corregedoria.INSPECTION_TABLE',
                                            },
                                            {
                                                xtype: 'choicefield',
                                                fieldLabel: 'Registro de Processos Judiciais Eleitorais Devolvidos',
                                                hiddenName: 'var_courtlawsuitelectoralreturned',
                                                width: 365,
                                                choiceId: 'corregedoria.INSPECTION_TABLE',
                                            },
                                            {
                                                xtype: 'choicefield',
                                                fieldLabel: 'Número de Ações Civis Públicas e Medidas ajuizadas',
                                                hiddenName: 'var_number_of_public_civil_actions',
                                                width: 365,
                                                choiceId: 'corregedoria.INSPECTION_TABLE',
                                            },
                                            {
                                                xtype: 'choicefield',
                                                fieldLabel: 'Número de ACPs de Improbidade Administrativa',
                                                hiddenName: 'var_number_of_acp_admin_dishonesty',
                                                width: 365,
                                                choiceId: 'corregedoria.INSPECTION_TABLE',
                                            },
                                            {
                                                xtype: 'choicefield',
                                                fieldLabel: 'Número de Recomendações expedidas',
                                                hiddenName: 'var_number_of_recommendations_issued',
                                                width: 365,
                                                choiceId: 'corregedoria.INSPECTION_TABLE',
                                            },
                                            {
                                                xtype: 'choicefield',
                                                fieldLabel: 'Número de Termos de Ajustamento de Conduta',
                                                hiddenName: 'var_number_of_conduct_adjustment_terms',
                                                width: 365,
                                                choiceId: 'corregedoria.INSPECTION_TABLE',
                                            },
                                            {
                                                xtype: 'choicefield',
                                                fieldLabel: 'Número de Audiências Públicas',
                                                hiddenName: 'var_number_of_public_audiences',
                                                width: 365,
                                                choiceId: 'corregedoria.INSPECTION_TABLE',
                                            },
                                            {
                                                xtype: 'choicefield',
                                                fieldLabel: 'Número de Procedimentos Extrajudiciais Instaurados',
                                                hiddenName: 'var_number_of_procedures_instituted',
                                                width: 365,
                                                choiceId: 'corregedoria.INSPECTION_TABLE',
                                            },
                                            {
                                                xtype: 'choicefield',
                                                fieldLabel: 'Número de Procedimentos Extrajudiciais Arquivados',
                                                hiddenName: 'var_number_of_procedures_archived',
                                                width: 365,
                                                choiceId: 'corregedoria.INSPECTION_TABLE',
                                            },
                                        ]
                                    },
                                    {
                                        xtype: 'fieldset',
                                        title: 'Tabelas de Pontuação',
                                        layout: 'form',
                                        collapsible: false,
                                        collapsed: false,
                                        width: 700,
                                        items: [
                                            {
                                                xtype: 'fieldset',
                                                title: 'Atendimento ao Público',
                                                layout: 'form',
                                                collapsible: false,
                                                collapsed: false,
                                                labelWidth: 120,
                                                width: 675,
                                                items: [
                                                    {
                                                        xtype: 'choicefield',
                                                        fieldLabel: 'Tabela de Pontuação',
                                                        hiddenName: 'var_public_attendance',
                                                        width: 525,
                                                        choiceId: 'corregedoria.SCORE_TABLE',
                                                    },
                                                ]
                                            },
                                            {
                                                xtype: 'fieldset',
                                                title: 'Presteza',
                                                layout: 'form',
                                                collapsible: false,
                                                collapsed: false,
                                                width: 675,
                                                labelWidth: 290,
                                                items: [
                                                    {
                                                        xtype: 'choicefield',
                                                        fieldLabel: 'Tabela de Pontuação para Feitos Judiciais',
                                                        hiddenName: 'var_promptness_courtlawsuit',
                                                        width: 350,
                                                        choiceId: 'corregedoria.SCORE_TABLE',
                                                    },
                                                    {
                                                        xtype: 'choicefield',
                                                        fieldLabel: 'Tabela de Pontuação para Feitos Extraudiciais',
                                                        hiddenName: 'var_promptness_outcourtlawsuit',
                                                        width: 350,
                                                        choiceId: 'corregedoria.SCORE_TABLE',
                                                    },
                                                    {
                                                        xtype: 'choicefield',
                                                        fieldLabel: 'Tabela de Pontuação para Atendimento Tempestivo',
                                                        hiddenName: 'var_promptness_uppermanagement',
                                                        width: 350,
                                                        choiceId: 'corregedoria.SCORE_TABLE',
                                                    },
                                                ]
                                            },
                                        ]
                                    },
                                ]
                            },
                            {
                                xtype: 'fieldset',
                                title: 'Vinculação - Relatórios de Atividades Funcionais - RAF',
                                margins: '0 0 0 5',
                                collapsible: false,
                                collapsed: false,
                                width: 1135,
                                items: [
                                    this.getLinkInspectionRAFGrid(),
                                ]
                            },
                        ]
                    },
                    {
                        xtype: 'fieldset',
                        title: 'SRDIR',
                        layout: 'form',
                        collapsible: true,
                        collapsed: true,
                        items:[
                            {
                                xtype: 'fieldset',
                                title: 'Agendamento Padrão',
                                // layout: 'form',
                                collapsible: false,
                                collapsed: false,
                                layout: {
                                    type: 'hbox',
                                    align: 'center',
                                },
                                items: [
                                    {
                                        xtype: 'fieldset',
                                        title: 'Residência',
                                        layout: 'form',
                                        collapsible: false,
                                        collapsed: false,
                                        labelWidth: 75,
                                        margins: '0 0 0 5',
                                        items: [
                                            {
                                                xtype: "textfield",
                                                fieldLabel: "Abertura",
                                                name: "var_open_date_address",
                                            },
                                            {
                                                xtype: "textfield",
                                                fieldLabel: "Fechamento",
                                                name: "var_close_date_address",
                                            },
                                        ]
                                    },
                                    {
                                        xtype: 'fieldset',
                                        title: 'Docência - 1º Semestre',
                                        layout: 'form',
                                        collapsible: false,
                                        collapsed: false,
                                        labelWidth: 75,
                                        margins: '0 0 0 5',
                                        items: [
                                            {
                                                xtype: "textfield",
                                                fieldLabel: "Abertura",
                                                name: "var_open_date_teaching_1st_semestry",
                                            },
                                            {
                                                xtype: "textfield",
                                                fieldLabel: "Fechamento",
                                                name: "var_close_date_teaching_1st_semestry",
                                            },
                                        ]
                                    },
                                    {
                                        xtype: 'fieldset',
                                        title: 'Docência - 2º Semestre',
                                        layout: 'form',
                                        collapsible: false,
                                        collapsed: false,
                                        labelWidth: 75,
                                        margins: '0 0 0 5',
                                        items: [
                                            {
                                                xtype: "textfield",
                                                fieldLabel: "Abertura",
                                                name: "var_open_date_teaching_2nd_semestry",
                                            },
                                            {
                                                xtype: "textfield",
                                                fieldLabel: "Fechamento",
                                                name: "var_close_date_teaching_2nd_semestry",
                                            },
                                        ]
                                    },
                                    {
                                        xtype: 'fieldset',
                                        title: 'Bens e Direitos',
                                        layout: 'form',
                                        collapsible: false,
                                        collapsed: false,
                                        labelWidth: 75,
                                        margins: '0 0 0 5',
                                        items: [
                                            {
                                                xtype: "textfield",
                                                fieldLabel: "Abertura",
                                                name: "var_open_date_property",
                                            },
                                            {
                                                xtype: "textfield",
                                                fieldLabel: "Fechamento",
                                                name: "var_close_date_property",
                                            },
                                        ]
                                    },
                                    {
                                        xtype: 'fieldset',
                                        title: 'Débitos',
                                        layout: 'form',
                                        collapsible: false,
                                        collapsed: false,
                                        labelWidth: 75,
                                        margins: '0 0 0 5',
                                        items: [
                                            {
                                                xtype: "textfield",
                                                fieldLabel: "Abertura",
                                                name: "var_open_date_debits",
                                            },
                                            {
                                                xtype: "textfield",
                                                fieldLabel: "Fechamento",
                                                name: "var_close_date_debits",
                                            },
                                        ]
                                    },
                                    {
                                        xtype: 'fieldset',
                                        title: 'Saúde',
                                        layout: 'form',
                                        collapsible: false,
                                        collapsed: false,
                                        labelWidth: 75,
                                        margins: '0 0 0 5',
                                        items: [
                                            {
                                                xtype: "textfield",
                                                fieldLabel: "Abertura",
                                                name: "var_open_date_health",
                                            },
                                            {
                                                xtype: "textfield",
                                                fieldLabel: "Fechamento",
                                                name: "var_close_date_health",
                                            },
                                        ]
                                    },
                                ]
                            },
                            {
                                xtype: 'fieldset',
                                title: 'Grupos de Acesso',
                                // layout: 'form',
                                collapsible: false,
                                collapsed: false,
                                layout: {
                                    type: 'hbox',
                                    align: 'center',
                                },
                                items: [
                                    {
                                        xtype: 'fieldset',
                                        title: 'Membros',
                                        layout: 'form',
                                        collapsible: false,
                                        collapsed: false,
                                        margins: '0 0 0 5',
                                        width: 920,
                                        labelWidth: 35,
                                        items: [
                                            {
                                                xtype: 'fieldset',
                                                title: 'Critérios',
                                                layout: 'form',
                                                collapsible: false,
                                                collapsed: false,
                                                margins: '0 0 0 5',
                                                labelWidth: 120,
                                                items: [
                                                    {
                                                        xtype: 'choicefield',
                                                        fieldLabel: 'Residência',
                                                        hiddenName: 'var_member_address',
                                                        width: 70,
                                                        choiceId: 'rh.SIM_NAO',
                                                    },
                                                    {
                                                        xtype: 'choicefield',
                                                        fieldLabel: 'Docência',
                                                        hiddenName: 'var_member_teaching',
                                                        width: 70,
                                                        choiceId: 'rh.SIM_NAO',
                                                    },
                                                    {
                                                        xtype: 'choicefield',
                                                        fieldLabel: 'Bens e Direitos',
                                                        hiddenName: 'var_member_property',
                                                        width: 70,
                                                        choiceId: 'rh.SIM_NAO',
                                                    },
                                                    {
                                                        xtype: 'choicefield',
                                                        fieldLabel: 'Ônus e Dívidas Reais',
                                                        hiddenName: 'var_member_debits',
                                                        width: 70,
                                                        choiceId: 'rh.SIM_NAO',
                                                    },
                                                    {
                                                        xtype: 'choicefield',
                                                        fieldLabel: 'Declaração IRPF',
                                                        hiddenName: 'var_member_irpf',
                                                        width: 70,
                                                        choiceId: 'rh.SIM_NAO',
                                                    },
                                                    {
                                                        xtype: 'choicefield',
                                                        fieldLabel: 'Saúde',
                                                        hiddenName: 'var_member_health',
                                                        width: 70,
                                                        choiceId: 'rh.SIM_NAO',
                                                    },
                                                ],
                                            },
                                            this.getTypeMemberField(),
                                        ]
                                    },
                                    {
                                        xtype: 'fieldset',
                                        title: 'Servidores',
                                        layout: 'form',
                                        collapsible: false,
                                        collapsed: false,
                                        margins: '0 0 0 5',
                                        width: 920,
                                        labelWidth: 150,
                                        items: [
                                            {
                                                xtype: 'fieldset',
                                                title: 'Critérios',
                                                layout: 'form',
                                                collapsible: false,
                                                collapsed: false,
                                                margins: '0 0 0 5',
                                                labelWidth: 120,
                                                items: [
                                                    {
                                                        xtype: 'choicefield',
                                                        fieldLabel: 'Residência',
                                                        hiddenName: 'var_employee_address',
                                                        width: 70,
                                                        choiceId: 'rh.SIM_NAO',
                                                    },
                                                    {
                                                        xtype: 'choicefield',
                                                        fieldLabel: 'Docência',
                                                        hiddenName: 'var_employee_teaching',
                                                        width: 70,
                                                        choiceId: 'rh.SIM_NAO',
                                                    },
                                                    {
                                                        xtype: 'choicefield',
                                                        fieldLabel: 'Bens e Direitos',
                                                        hiddenName: 'var_employee_property',
                                                        width: 70,
                                                        choiceId: 'rh.SIM_NAO',
                                                    },
                                                    {
                                                        xtype: 'choicefield',
                                                        fieldLabel: 'Ônus e Dívidas Reais',
                                                        hiddenName: 'var_employee_debits',
                                                        width: 70,
                                                        choiceId: 'rh.SIM_NAO',
                                                    },
                                                    {
                                                        xtype: 'choicefield',
                                                        fieldLabel: 'Declaração IRPF',
                                                        hiddenName: 'var_employee_irpf',
                                                        width: 70,
                                                        choiceId: 'rh.SIM_NAO',
                                                    },
                                                    {
                                                        xtype: 'choicefield',
                                                        fieldLabel: 'Saúde',
                                                        hiddenName: 'var_employee_health',
                                                        width: 70,
                                                        choiceId: 'rh.SIM_NAO',
                                                    },
                                                ],
                                            },
                                            this.getTypeEmployeeField(),
                                        ]
                                    },
                                ]
                            },
                        ]
                    },
                    {
                        xtype: 'fieldset',
                        title: 'Prontuário Eletrônico',
                        layout: 'form',
                        collapsible: true,
                        collapsed: true,
                        margins: '0 0 0 5',
                        items: [
                            {
                                xtype: 'fieldset',
                                title: 'Cumulação de Atividades, Cargos e Funções',
                                layout: 'form',
                                collapsible: false,
                                collapsed: false,
                                labelWidth: 120,
                                items: [
                                    {
                                        xtype: 'choicefield',
                                        fieldLabel: 'Tabela de Pontuação',
                                        hiddenName: 'var_functionalperformance_cumulation',
                                        width: 770,
                                        choiceId: 'corregedoria.SCORE_TABLE',
                                    },
                                ]
                            },
                            {
                                xtype: 'fieldset',
                                title: 'Participação em Cursos',
                                layout: 'form',
                                collapsible: false,
                                collapsed: false,
                                labelWidth: 220,
                                items: [
                                    {
                                        xtype: 'choicefield',
                                        fieldLabel: 'Tabela de Pontuacao - Doutorado',
                                        hiddenName: 'var_coursesparticipation_doctorate',
                                        width: 670,
                                        choiceId: 'corregedoria.SCORE_TABLE',
                                    },
                                    {
                                        xtype: 'choicefield',
                                        fieldLabel: 'Tabela de Pontuacao - Mestrado',
                                        hiddenName: 'var_coursesparticipation_masters',
                                        width: 670,
                                        choiceId: 'corregedoria.SCORE_TABLE',
                                    },
                                    {
                                        xtype: 'choicefield',
                                        fieldLabel: 'Tabela de Pontuacao - Especialização',
                                        hiddenName: 'var_coursesparticipation_specialization',
                                        width: 670,
                                        choiceId: 'corregedoria.SCORE_TABLE',
                                    },
                                    {
                                        xtype: 'choicefield',
                                        fieldLabel: 'Tabela de Pontuacao - Aperfeiçoameto',
                                        hiddenName: 'var_coursesparticipation_improvement',
                                        width: 670,
                                        choiceId: 'corregedoria.SCORE_TABLE',
                                    },
                                ]
                            },
                            {
                                xtype: 'fieldset',
                                title: 'Atuação em Comarca de Particular Dificuldade',
                                layout: 'form',
                                collapsible: false,
                                collapsed: false,
                                labelWidth: 120,
                                items: [
                                    {
                                        xtype: 'choicefield',
                                        fieldLabel: 'Tabela de Pontuação',
                                        hiddenName: 'var_performance_particular_difficulty',
                                        width: 770,
                                        choiceId: 'corregedoria.SCORE_TABLE',
                                    },
                                ]
                            },
                        ]
                    },
                    {
                        xtype: 'fieldset',
                        title: 'Produtividade',
                        layout: 'form',
                        collapsible: true,
                        collapsed: true,
                        items: [
                            this.getProductuvityGrid(),
                        ]
                    },
                    {
                        xtype: 'fieldset',
                        title: 'Tabelas de Pontuação',
                        layout: 'form',
                        collapsible: true,
                        collapsed: true,
                        items: [
                            this.getScoreTableGrid(),
                        ]
                    },
                    {
                        xtype: 'fieldset',
                        title: 'Parâmetros do Sistema',
                        layout: 'form',
                        collapsible: true,
                        collapsed: true,
                        items: [
                            {
                                xtype: 'fieldset',
                                title: 'Permissão e Menu dos Avaliadores da Saúde',
                                layout: 'form',
                                collapsible: false,
                                collapsed: false,
                                labelWidth: 300,
                                items: [
                                    this.getEvaluatorHealthAreaGroupPermission(),
                                    this.getEvaluatorHealthAreaGroupMenu()
                                ]
                            }
                        ]
                    },
                ],
                buttons: [
                    {
                        text: 'Salvar',
                        scope: this,
                        handler: this.saveConfiguration
                    },
                    {
                        text: 'Restaurar',
                        scope: this,
                        handler: this.dataReload
                    }
                ]
            });

        return this._formPanel;
    },

    getEvaluatorHealthAreaGroupPermission: function() {
        if(!this._evaluatorhealthAreaGroupPermission) {
            this._evaluatorhealthAreaGroupPermission = Ext._create('core.fields.AutocompleteField', {
                xtype: "rest-autocompletefield",
                fieldLabel: 'Permissão',
                allowBlank: true,
                rest: "auth.GroupRestful",
                name: "evaluator_health_group_permission",
                width: 400,
                disabled: false,
                preFilter: [
                    {property: 'permissions__codename__icontains', value: 'healthassessment', stage: 100},
                ],
                gridConfig: {
                    columnAction: false,
                    hideItemsToolbar: ['add', 'edit', 'remove', 'download', 'filter'],
                }
            });
        }
        return this._evaluatorhealthAreaGroupPermission;
    },

    getEvaluatorHealthAreaGroupMenu: function() {
        if(!this._evaluatorhealthAreaGroupMenu) {
            this._evaluatorhealthAreaGroupMenu = Ext._create('core.fields.AutocompleteField', {
                xtype: "rest-autocompletefield",
                fieldLabel: 'Menu',
                allowBlank: true,
                rest: "engine.ControllerPermissionRestful",
                name: "evaluator_health_group_menu",
                width: 400,
                disabled: false,
                preFilter: [
                    {property: 'controllers__module', value: 'corregedoria.cirdir', stage: 100},
                ],
                gridConfig: {
                    columnAction: false,
                    hideItemsToolbar: ['add', 'edit', 'remove', 'download', 'filter'],
                }
            });
        }
        return this._evaluatorhealthAreaGroupMenu;
    },

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});

        this._valuesMember = {};
        this._valuesEmployee = {};

        Ext.applyIf(
            cfg,
            {
                title: 'Configurações',
            }
        );

        Ext.apply(
            cfg,
            {
                layout: 'border',
                items: [this.getFormPanel()],
            }
        );

        corregedoria.Configuration.superclass.constructor.call(this, cfg);
        this.dataReload();
    }
});
