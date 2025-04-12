Ext._define('corregedoria.inspection.analyze_recommendation.Window', {
  extend: 'core.RestfulWindow',

  rest: 'corregedoria.inspection.analyze_recommendation.Restful',
  width: 810,

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

    getInspectorProsecutorField: function() {
        if(!this._inspectorProsecutorField) {
            this._inspectorProsecutorField = Ext._create('core.fields.AutocompleteField', {
                xtype: "rest-autocompletefield",
                fieldLabel: 'Promotor-Corregedor',
                allowBlank: true,
                rest: "raf.EmployeeRestful",
                name: "inspector_prosecutor",
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
        return this._inspectorProsecutorField;
    },

    getEmployee: function(execution_organ){
        var rest = this.factoryRestful();
        var mask = new Ext.LoadMask(this.getEl(), {msg: 'Carregando informações do Órgão de Execução selecionado...'});
        mask.show();
        rest.get_employee(
            {
                execution_organ: this.getFormPanel().getForm().findField('execution_organ').getValue(),
            },
            {
                scope: this,
                fn: function(rst) {
                    if(rst.success) {
                        this.getFormPanel().getForm().findField('employee').setValue(rst.employee);
                        this.getFormPanel().getForm().findField('responsible').setValue(rst.employee);
                    }
                    else
                        Ext.Msg.show({
                            title: 'Gestor de Inspeções/Correições',
                            msg: rst.message,
                            icon: Ext.Msg.ERROR,
                            buttons: Ext.Msg.OK
                        });
                }
            },
            {
                scope: this,
                fn: function(message) {
                    Ext.Msg.show({
                        title: 'Gestor de Inspeções/Correições',
                        msg: message,
                        icon: Ext.Msg.ERROR,
                        buttons: Ext.Msg.OK
                    });
                }
            },
            {
                scope: this,
                fn: function() {
                    mask.hide();
                }
            }
        );
    },

    getHolderEmployee: function(execution_organ){
        var rest = this.factoryRestful();
        var mask = new Ext.LoadMask(this.getEl(), {msg: 'Carregando informações do Órgão de Execução selecionado...'});
        mask.show();
        rest.get_holder_employee(
            {
                execution_organ: this.getFormPanel().getForm().findField('execution_organ').getValue(),
            },
            {
                scope: this,
                fn: function(rst) {
                    if(rst.success) {
                        this.getFormPanel().getForm().findField('holder_employee').setValue(rst.holder_employee);
                    }
                    else
                        Ext.Msg.show({
                            title: 'Gestor de Inspeções/Correições',
                            msg: rst.message,
                            icon: Ext.Msg.ERROR,
                            buttons: Ext.Msg.OK
                        });
                }
            },
            {
                scope: this,
                fn: function(message) {
                    Ext.Msg.show({
                        title: 'Gestor de Inspeções/Correições',
                        msg: message,
                        icon: Ext.Msg.ERROR,
                        buttons: Ext.Msg.OK
                    });
                }
            },
            {
                scope: this,
                fn: function() {
                    mask.hide();
                }
            }
        );
    },

    getAreaOfAction: function(execution_organ){
        var rest = this.factoryRestful();
        var mask = new Ext.LoadMask(this.getEl(), {msg: 'Carregando informações do Órgão de Execução selecionado...'});
        mask.show();
        rest.get_area_of_action(
            {
                execution_organ: this.getFormPanel().getForm().findField('execution_organ').getValue(),
            },
            {
                scope: this,
                fn: function(rst) {
                    if(rst.success) {
                        this.getFormPanel().getForm().findField('area_of_action').setValue(rst.area_of_action);
                    }
                    else
                        Ext.Msg.show({
                            title: 'Gestor de Inspeções/Correições',
                            msg: rst.message,
                            icon: Ext.Msg.ERROR,
                            buttons: Ext.Msg.OK
                        });
                }
            },
            {
                scope: this,
                fn: function(message) {
                    Ext.Msg.show({
                        title: 'Gestor de Inspeções/Correições',
                        msg: message,
                        icon: Ext.Msg.ERROR,
                        buttons: Ext.Msg.OK
                    });
                }
            },
            {
                scope: this,
                fn: function() {
                    mask.hide();
                }
            }
        );
    },

    getAssignment: function(execution_organ){
        var rest = this.factoryRestful();
        var mask = new Ext.LoadMask(this.getEl(), {msg: 'Carregando informações do Órgão de Execução selecionado...'});
        mask.show();
        rest.get_assignment(
            {
                execution_organ: this.getFormPanel().getForm().findField('execution_organ').getValue(),
            },
            {
                scope: this,
                fn: function(rst) {
                    if(rst.success) {
                        this.getFormPanel().getForm().findField('assignment').setValue(rst.assignment);
                    }
                    else
                        Ext.Msg.show({
                            title: 'Gestor de Inspeções/Correições',
                            msg: rst.message,
                            icon: Ext.Msg.ERROR,
                            buttons: Ext.Msg.OK
                        });
                }
            },
            {
                scope: this,
                fn: function(message) {
                    Ext.Msg.show({
                        title: 'Gestor de Inspeções/Correições',
                        msg: message,
                        icon: Ext.Msg.ERROR,
                        buttons: Ext.Msg.OK
                    });
                }
            },
            {
                scope: this,
                fn: function() {
                    mask.hide();
                }
            }
        );
    },

    onChangeExecutionOrgan: function(value) {
        var employee = this.getEmployee(value);
        var holder_employee = this.getHolderEmployee(value);
        this.getAreaOfAction(value);
        this.getAssignment(value);
    },

    getExecutionOrganField: function() {
        if(!this._locationField) {
            this._locationField = Ext._create('core.fields.AutocompleteField', {
                xtype: "rest-autocompletefield",
                fieldLabel: "Órgão de Execução",
                allowBlank: true,
                rest: "judicial.county.ExecutionOrganRestful",
                id: "execution_organ",
                name: "execution_organ",
                disabled: false,
                gridConfig: {
                    columnAction: false,
                    hideColumns: ['habilita_protocolo', 'ativo', 'sigla', 'general_distribution', 'replacements', 'owner_unicode', 'employee_exercise_unicode'],
                    hideItemsToolbar: ['add', 'edit', 'remove', 'download'],
                },
            });
        }
        this._locationField.getComboField().addListener('change', function(combo, record, index) { this.onChangeExecutionOrgan(record.id); }, this);
        return this._locationField;
    },

    getResponsibleField: function() {
        if(!this._responsibleField) {
            this._responsibleField = Ext._create('core.fields.AutocompleteField', {
                xtype: "rest-autocompletefield",
                fieldLabel: "Responsável",
                allowBlank: true,
                rest: "raf.EmployeeRestful",
                name: "responsible",
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
        return this._responsibleField;
    },

    getEmployeeField: function() {
        if(!this._employeeField) {
            this._employeeField = Ext._create('core.fields.AutocompleteField', {
                xtype: "rest-autocompletefield",
                fieldLabel: "Inspecionado",
                allowBlank: true,
                rest: "raf.EmployeeRestful",
                name: "employee",
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
        return this._employeeField;
    },

    getHolderEmployeeField: function() {
        if(!this._holderEmployeeField) {
            this._holderEmployeeField = Ext._create('core.fields.AutocompleteField', {
                xtype: "rest-autocompletefield",
                fieldLabel: "Titular",
                allowBlank: true,
                rest: "raf.EmployeeRestful",
                name: "holder_employee",
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
        return this._holderEmployeeField;
    },

    getTitular_employeeSelection: function() {
        if(!this._titular_employeeSelection) {
            this._titular_employeeSelection = Ext._create('Ext.form.RadioGroup', {
                xtype: 'radiogroup',
                fieldLabel: 'Titular na Procuradoria/Promotoria',
                hideLabel: false,
                columns: 2,
                vertical: true,
                items: [
                    {boxLabel: 'SIM', name: 'titular_employee', inputValue: 'Yes',},
                    {boxLabel: 'NÃO', name: 'titular_employee', inputValue: 'No',},
                ]
            });
        }
        return this._titular_employeeSelection;
    },

    getDaily_attendanceSelection: function() {
        if(!this._daily_attendanceSelection) {
            this._daily_attendanceSelection = Ext._create('Ext.form.RadioGroup', {
                xtype: 'radiogroup',
                fieldLabel: 'Atendimento ao público diário',
                hideLabel: false,
                columns: 2,
                vertical: true,
                items: [
                    {boxLabel: 'SIM', name: 'daily_attendance', inputValue: 'Yes',},
                    {boxLabel: 'NÃO', name: 'daily_attendance', inputValue: 'No',},
                ]
            });
        }
        return this._daily_attendanceSelection;
    },

    getFormPanel: function() {
      if(!this._formPanel) {
        this._formPanel = Ext._create('Ext.form.FormPanel', {
            border: false,
            frame: true,
            items: [
                {
                    xtype:'fieldset',
                    title: '1. Dados da Inspeção',
                    collapsible: false,
                    autoHeight:true,
                    width: 783,
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
                            labelWidth: 130,
                            layout: 'form',
                            items: [
                                this.getInspectorGeneralField(),
                                this.getInspectorProsecutorField(),
                            ],
                        },
                    ]
                },
                {
                    xtype:'fieldset',
                    title: '2. Dados Funcionais',
                    labelWidth: 115,
                    collapsible: false,
                    autoHeight:true,
                    width: 783,
                    items: [
                        this.getExecutionOrganField(),
                        this.getResponsibleField(),
                        this.getEmployeeField(),
                        this.getHolderEmployeeField(),
                        {
                            xtype: 'textfield',
                            fieldLabel: 'Área de Atuação',
                            id: 'area_of_action',
                            name: 'area_of_action',
                            hideLabel: false,
                            width: 635,
                        },
                        {
                            xtype: 'textarea',
                            fieldLabel: 'Atribuição',
                            name: 'assignment',
                            hideLabel: false,
                            width: 635,
                            height: 50,
                        },
                    ]
                },
                {
                    xtype:'fieldset',
                    title: '3. Designação Eleitoral',
                    labelWidth: 115,
                    collapsible: false,
                    autoHeight:true,
                    width: 783,
                    items: [
                        {
                            xtype:'panel',
                            autoHeight:true,
                            layout: 'form',
                            labelWidth: 53,
                            items: [
                                {
                                    fieldLabel: 'Se aplica',
                                    xtype: 'combo',
                                    id: 'electoral_applicable',
                                    hiddenName: 'electoral_applicable',
                                    width: 100,
                                    editable: false,
                                    triggerAction: 'all',
                                    store: [
                                        [1, ''],
                                        [2, 'SIM'],
                                        [3, 'NÃO'],
                                    ],
                                    listeners: {
                                        scope: this,
                                        select: function(index){
                                            if (index.value!=2) {
                                                this.getFormPanel().getForm().findField('electoral_electoralzone').disable();
                                                this.getFormPanel().getForm().findField('electoral_designation').disable();
                                                this.getFormPanel().getForm().findField('electoral_initialbiennium').disable();
                                                this.getFormPanel().getForm().findField('electoral_finalbiennium').disable();
                                            } else {
                                                this.getFormPanel().getForm().findField('electoral_electoralzone').enable();
                                                this.getFormPanel().getForm().findField('electoral_designation').enable();
                                                this.getFormPanel().getForm().findField('electoral_initialbiennium').enable();
                                                this.getFormPanel().getForm().findField('electoral_finalbiennium').enable();
                                            }
                                        },
                                        render: function(){
                                            if (Ext.getCmp('electoral_applicable').value!=2) {
                                                this.getFormPanel().getForm().findField('electoral_electoralzone').disable();
                                                this.getFormPanel().getForm().findField('electoral_designation').disable();
                                                this.getFormPanel().getForm().findField('electoral_initialbiennium').disable();
                                                this.getFormPanel().getForm().findField('electoral_finalbiennium').disable();
                                            } else {
                                                this.getFormPanel().getForm().findField('electoral_electoralzone').enable();
                                                this.getFormPanel().getForm().findField('electoral_designation').enable();
                                                this.getFormPanel().getForm().findField('electoral_initialbiennium').enable();
                                                this.getFormPanel().getForm().findField('electoral_finalbiennium').enable();
                                            }
                                        },
                                    },
                                },
                            ]
                        },
                        {
                            xtype:'panel',
                            autoHeight:true,
                            layout: 'column',
                            items: [
                                {
                                    xtype:'panel',
                                    autoHeight:true,
                                    layout: 'form',
                                    labelWidth: 80,
                                    columnWidth: 0.20,
                                    items: [
                                        {
                                            xtype: "textfield",
                                            fieldLabel: "Zona Eleitoral",
                                            id: "electoral_electoralzone",
                                            name: "electoral_electoralzone",
                                            width: 55,
                                            disabled: true,
                                        },
                                    ]
                                },
                                {
                                    xtype:'panel',
                                    autoHeight:true,
                                    layout: 'form',
                                    labelWidth: 105,
                                    columnWidth: 0.38,
                                    items: [
                                        {
                                            xtype: "textfield",
                                            fieldLabel: "Ato de Designação",
                                            id: "electoral_designation",
                                            name: "electoral_designation",
                                            width: 165,
                                            disabled: true,
                                        },
                                    ]
                                },
                                {
                                    xtype:'panel',
                                    autoHeight:true,
                                    layout: 'form',
                                    labelWidth: 87,
                                    columnWidth: 0.20,
                                    items: [
                                        {
                                            xtype: "textfield",
                                            fieldLabel: "Início do Biênio",
                                            id: "electoral_initialbiennium",
                                            name: "electoral_initialbiennium",
                                            width: 45,
                                            disabled: true,
                                        },
                                    ]
                                },
                                {
                                    xtype:'panel',
                                    autoHeight:true,
                                    layout: 'form',
                                    labelWidth: 103,
                                    columnWidth: 0.22,
                                    items: [
                                        {
                                            xtype: "textfield",
                                            fieldLabel: "Término do Biênio",
                                            id: "electoral_finalbiennium",
                                            name: "electoral_finalbiennium",
                                            width: 45,
                                            disabled: true,
                                        },
                                    ]
                                },
                            ]
                        },
                    ]
                },
                {
                    xtype:'fieldset',
                    title: '4. Informações do Membro',
                    hideLabel: true,
                    labelWidth: 1,
                    collapsible: false,
                    autoHeight:true,
                    width: 783,
                    items: [
                        // {
                        //     xtype: 'checkbox',
                        //     name: 'residence',
                        //     boxLabel: 'Mantém residência efetiva na comarca de lotação, inclusive nos finais de semana',
                        // },
                        // {
                        //     xtype: 'checkbox',
                        //     name: 'accumulates',
                        //     boxLabel: 'Acumula ou acumulou outra Procuradoria/Promotoria',
                        // },
                        // {
                        //     xtype: 'checkbox',
                        //     name: 'replacements',
                        //     boxLabel: 'Substituiu outra Procuradoria/Promotoria',
                        // },
                        {
                            xtype: 'checkbox',
                            name: 'attendance',
                            boxLabel: 'Atende aos expedientes internos e externos',
                        },
                        // {
                        //     xtype: 'checkbox',
                        //     name: 'teaching',
                        //     boxLabel: 'Exerce atividade docente',
                        // },
                    ]
                },
                {
                    xtype:'fieldset',
                    title: '5. Dados da Procuradoria/Promotoria',
                    labelWidth: 115,
                    collapsible: false,
                    autoHeight:true,
                    width: 783,
                    items: [
                        {
                            xtype:'panel',
                            autoHeight:true,
                            layout: 'column',
                            defaults: {
                                labelAlign: 'left',
                                style: 'margin-right: 15px;',
                            },
                            items: [
                                {
                                    xtype:'panel',
                                    autoHeight:true,
                                    width: 350,
                                    layout: 'form',
                                    labelWidth: 50,
                                    columnWidth: 0.4,
                                    items: [
                                        {
                                            xtype:'panel',
                                            autoHeight:true,
                                            layout: 'form',
                                            labelWidth: 140,
                                            items: [
                                                {
                                                    xtype: 'datefield',
                                                    fieldLabel: 'Data da última inspeção',
                                                    name: 'last_inspection_date',
                                                },
                                            ]
                                        },
                                        {
                                            xtype:'panel',
                                            autoHeight:true,
                                            layout: 'form',
                                            hideLabel: true,
                                            labelWidth: 1,
                                            items: [
                                                // {
                                                //     xtype: 'checkbox',
                                                //     name: 'titular_employee',
                                                //     boxLabel: 'Titular na Procuradoria/Promotoria',
                                                // },
                                                {
                                                    xtype: 'checkbox',
                                                    name: 'daily_attendance',
                                                    boxLabel: 'Atendimento ao público diário',
                                                    listeners: {
                                                        scope: this,
                                                        check: function(checkbox, checked){
                                                            if (checked) {
                                                                this.getFormPanel().getForm().findField('input_days_of_attendance_per_week').disable();
                                                            } else {
                                                                this.getFormPanel().getForm().findField('input_days_of_attendance_per_week').enable();
                                                            }
                                                        }
                                                    }
                                                },
                                                {
                                                    xtype:'panel',
                                                    autoHeight:true,
                                                    layout: 'form',
                                                    labelWidth: 180,
                                                    style: {paddingLeft: '25px'},
                                                    items: [
                                                        {
                                                            id: 'input_days_of_attendance_per_week',
                                                            fieldLabel: 'Quantidade de dias por semana',
                                                            xtype: 'combo',
                                                            hiddenName: 'days_of_attendance_per_week',
                                                            width: 75,
                                                            editable: false,
                                                            triggerAction: 'all',
                                                            store: [
                                                                [1, '1'],
                                                                [2, '2'],
                                                                [3, '3'],
                                                                [4, '4'],
                                                            ],
                                                        }
                                                    ]
                                                },
                                            ]
                                        },
                                    ]
                                },
                                {
                                    xtype:'panel',
                                    autoHeight:true,
                                    width: 350,
                                    layout: 'form',
                                    hideLabel: true,
                                    labelWidth: 1,
                                    columnWidth: 0.6,
                                    items: [
                                        {
                                            xtype:'fieldset',
                                            title: 'Horário de atendimento ao público',
                                            hideLabel: true,
                                            collapsible: false,
                                            autoHeight:true,
                                            width: 440,
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
                                                            labelWidth: 80,
                                                            columnWidth: 0.55,
                                                            items: [
                                                                {
                                                                    xtype: "textfield",
                                                                    fieldLabel: "Manhã - Início",
                                                                    id: "attendance_schedule1_inital",
                                                                    name: "attendance_schedule1_inital",
                                                                    width: 120,
                                                                    emptyText: 'HH:MM',
                                                                    regex: /^([0-1][0-9]|2[0-3]):([0-5][0-9])$/,
                                                                    regexText: 'Entrada inválida.<br/>Formato correto: <b>HH:MM</b>.',
                                                                    maxLength: 5,
                                                                    maxLengthText: 'Entrada inválida.<br/>Formato correto: <b>HH:MM</b>.',
                                                                    listeners: {
                                                                        scope: this,
                                                                        blur: function(){
                                                                            if (Ext.getCmp('attendance_schedule1_inital').getValue().length == 2) {
                                                                                Ext.getCmp('attendance_schedule1_inital').setValue(Ext.getCmp('attendance_schedule1_inital').getValue()+':00');
                                                                            }
                                                                        },
                                                                    },
                                                                },
                                                            ]
                                                        },
                                                        {
                                                            xtype:'panel',
                                                            autoHeight:true,
                                                            layout: 'form',
                                                            labelWidth: 50,
                                                            columnWidth: 0.45,
                                                            items: [
                                                                {
                                                                    xtype: "textfield",
                                                                    fieldLabel: "Término",
                                                                    id: "attendance_schedule1_final",
                                                                    name: "attendance_schedule1_final",
                                                                    width: 120,
                                                                    emptyText: 'HH:MM',
                                                                    regex: /^([0-1][0-9]|2[0-3]):([0-5][0-9])$/,
                                                                    regexText: 'Entrada inválida.<br/>Formato correto: <b>HH:MM</b>.',
                                                                    maxLength: 5,
                                                                    maxLengthText: 'Entrada inválida.<br/>Formato correto: <b>HH:MM</b>.',
                                                                    listeners: {
                                                                        scope: this,
                                                                        blur: function(){
                                                                            if (Ext.getCmp('attendance_schedule1_final').getValue().length == 2) {
                                                                                Ext.getCmp('attendance_schedule1_final').setValue(Ext.getCmp('attendance_schedule1_final').getValue()+':00');
                                                                            }
                                                                        },
                                                                    },
                                                                },
                                                            ]
                                                        },
                                                    ]
                                                },
                                                {
                                                    xtype:'panel',
                                                    autoHeight:true,
                                                    layout: 'column',
                                                    items: [
                                                        {
                                                            xtype:'panel',
                                                            autoHeight:true,
                                                            layout: 'form',
                                                            labelWidth: 80,
                                                            columnWidth: 0.55,
                                                            items: [
                                                                {
                                                                    xtype: "textfield",
                                                                    fieldLabel: "Tarde - Início",
                                                                    id: "attendance_schedule2_inital",
                                                                    name: "attendance_schedule2_inital",
                                                                    width: 120,
                                                                    emptyText: 'HH:MM',
                                                                    regex: /^([0-1][0-9]|2[0-3]):([0-5][0-9])$/,
                                                                    regexText: 'Entrada inválida.<br/>Formato correto: <b>HH:MM</b>.',
                                                                    maxLength: 5,
                                                                    maxLengthText: 'Entrada inválida.<br/>Formato correto: <b>HH:MM</b>.',
                                                                    listeners: {
                                                                        scope: this,
                                                                        blur: function(){
                                                                            if (Ext.getCmp('attendance_schedule2_inital').getValue().length == 2) {
                                                                                Ext.getCmp('attendance_schedule2_inital').setValue(Ext.getCmp('attendance_schedule2_inital').getValue()+':00');
                                                                            }
                                                                        },
                                                                    },
                                                                },
                                                            ]
                                                        },
                                                        {
                                                            xtype:'panel',
                                                            autoHeight:true,
                                                            layout: 'form',
                                                            labelWidth: 50,
                                                            columnWidth: 0.45,
                                                            items: [
                                                                {
                                                                    xtype: "textfield",
                                                                    fieldLabel: "Término",
                                                                    id: "attendance_schedule2_final",
                                                                    name: "attendance_schedule2_final",
                                                                    width: 120,
                                                                    emptyText: 'HH:MM',
                                                                    regex: /^([0-1][0-9]|2[0-3]):([0-5][0-9])$/,
                                                                    regexText: 'Entrada inválida.<br/>Formato correto: <b>HH:MM</b>.',
                                                                    maxLength: 5,
                                                                    maxLengthText: 'Entrada inválida.<br/>Formato correto: <b>HH:MM</b>.',
                                                                    listeners: {
                                                                        scope: this,
                                                                        blur: function(){
                                                                            if (Ext.getCmp('attendance_schedule2_final').getValue().length == 2) {
                                                                                Ext.getCmp('attendance_schedule2_final').setValue(Ext.getCmp('attendance_schedule2_final').getValue()+':00');
                                                                            }
                                                                        },
                                                                    },
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
});
