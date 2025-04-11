
Ext._define('corregedoria.inspection.inspection.filling.administrativeorganization.Launcher', {
    extend: 'Ext.Panel',

    getOperatingHoursForm: function(cfg) {
        if(!this._operatingHoursForm) {
            this._operatingHoursForm = Ext._create('Ext.form.FieldSet', {
                title: '3.1. Horário de Funcionamento',
                collapsible: true,
                collapsed: false,
                autoHeight:true,
                labelWidth: 1,
                items:[
                    {
                        xtype:'panel',
                        autoHeight:true,
                        layout: 'column',
                        items: [
                            {
                                xtype:'panel',
                                autoHeight:true,
                                layout: 'form',
                                labelWidth: 110,
                                columnWidth: 0.65,
                                items: [
                                    {
                                        xtype:'panel',
                                        autoHeight:true,
                                        layout: 'column',
                                        style: {
                                            marginLeft: '200px',
                                            // marginRight: '150px',
                                        },
                                        items: [
                                            {
                                                xtype:'panel',
                                                autoHeight:true,
                                                layout: 'form',
                                                labelWidth: 110,
                                                columnWidth: 0.55,
                                                items: [
                                                    {
                                                        xtype: "textfield",
                                                        fieldLabel: "Matutino - Início",
                                                        id: "operate_schedule1_initial",
                                                        name: "ao_operate_schedule1_initial",
                                                        width: 120,
                                                        emptyText: 'HH:MM',
                                                        regex: /^([0-1][0-9]|2[0-3]):([0-5][0-9])$/,
                                                        regexText: 'Entrada inválida.<br/>Formato correto: <b>HH:MM</b>.',
                                                        maxLength: 5,
                                                        maxLengthText: 'Entrada inválida.<br/>Formato correto: <b>HH:MM</b>.',
                                                        listeners: {
                                                            scope: this,
                                                            blur: function(){
                                                                if (Ext.getCmp('operate_schedule1_initial').getValue().length == 2) {
                                                                    Ext.getCmp('operate_schedule1_initial').setValue(Ext.getCmp('operate_schedule1_initial').getValue()+':00');
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
                                                        id: "operate_schedule1_final",
                                                        name: "ao_operate_schedule1_final",
                                                        width: 120,
                                                        emptyText: 'HH:MM',
                                                        regex: /^([0-1][0-9]|2[0-3]):([0-5][0-9])$/,
                                                        regexText: 'Entrada inválida.<br/>Formato correto: <b>HH:MM</b>.',
                                                        maxLength: 5,
                                                        maxLengthText: 'Entrada inválida.<br/>Formato correto: <b>HH:MM</b>.',
                                                        listeners: {
                                                            scope: this,
                                                            blur: function(){
                                                                if (Ext.getCmp('operate_schedule1_final').getValue().length == 2) {
                                                                    Ext.getCmp('operate_schedule1_final').setValue(Ext.getCmp('operate_schedule1_final').getValue()+':00');
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
                                        style: {
                                            marginLeft: '200px',
                                            // marginRight: '150px',
                                        },
                                        items: [
                                            {
                                                xtype:'panel',
                                                autoHeight:true,
                                                layout: 'form',
                                                labelWidth: 110,
                                                columnWidth: 0.55,
                                                items: [
                                                    {
                                                        xtype: "textfield",
                                                        fieldLabel: "Vespertino - Início",
                                                        id: "operate_schedule2_initial",
                                                        name: "ao_operate_schedule2_initial",
                                                        width: 120,
                                                        emptyText: 'HH:MM',
                                                        regex: /^([0-1][0-9]|2[0-3]):([0-5][0-9])$/,
                                                        regexText: 'Entrada inválida.<br/>Formato correto: <b>HH:MM</b>.',
                                                        maxLength: 5,
                                                        maxLengthText: 'Entrada inválida.<br/>Formato correto: <b>HH:MM</b>.',
                                                        listeners: {
                                                            scope: this,
                                                            blur: function(){
                                                                if (Ext.getCmp('operate_schedule2_initial').getValue().length == 2) {
                                                                    Ext.getCmp('operate_schedule2_initial').setValue(Ext.getCmp('operate_schedule2_initial').getValue()+':00');
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
                                                        id: "operate_schedule2_final",
                                                        name: "ao_operate_schedule2_final",
                                                        width: 120,
                                                        emptyText: 'HH:MM',
                                                        regex: /^([0-1][0-9]|2[0-3]):([0-5][0-9])$/,
                                                        regexText: 'Entrada inválida.<br/>Formato correto: <b>HH:MM</b>.',
                                                        maxLength: 5,
                                                        maxLengthText: 'Entrada inválida.<br/>Formato correto: <b>HH:MM</b>.',
                                                        listeners: {
                                                            scope: this,
                                                            blur: function(){
                                                                if (Ext.getCmp('operate_schedule2_final').getValue().length == 2) {
                                                                    Ext.getCmp('operate_schedule2_final').setValue(Ext.getCmp('operate_schedule2_final').getValue()+':00');
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
                            {
                                xtype:'panel',
                                autoHeight:true,
                                layout: 'form',
                                hideLabel: true,
                                labelWidth: 1,
                                columnWidth: 0.35,
                                items: [
                                    {
                                        xtype:'panel',
                                        autoHeight:true,
                                        labelWidth: 77,
                                        layout: 'form',
                                        items: [
                                            {
                                                xtype: 'textarea',
                                                fieldLabel: 'Observações',
                                                name: 'aooh_observation',
                                                hideLabel: false,
                                                allowBlank: true,
                                                width: 300,
                                                height: 50,
                                            },
                                        ]
                                    },
                                ]
                            },
                        ]
                    },
                ]
            });
        }
        return this._operatingHoursForm;
    },

    getPublicAttendanceForm: function(cfg) {
        if(!this._publicAttendanceForm) {
            this._publicAttendanceForm = Ext._create('Ext.form.FieldSet', {
                title: '3.2. Atendimento ao Público',
                collapsible: true,
                collapsed: false,
                autoHeight:true,
                labelWidth: 1,
                items:[
                    {
                        xtype:'panel',
                        autoHeight:true,
                        layout: 'column',
                        // defaults: {
                        //     labelAlign: 'left',
                        //     style: 'margin-right: 15px;',
                        // },
                        items: [
                            {
                                xtype:'panel',
                                autoHeight:true,
                                layout: 'form',
                                labelWidth: 50,
                                columnWidth: 0.30,
                                items: [
                                    {
                                        xtype:'panel',
                                        autoHeight:true,
                                        layout: 'form',
                                        hideLabel: true,
                                        labelWidth: 1,
                                        items: [
                                            {
                                                xtype: 'checkbox',
                                                name: 'daily_attendance',
                                                boxLabel: 'Atendimento ao público diário',
                                                listeners: {
                                                    scope: this,
                                                    check: function(checkbox, checked){
                                                        if (checked) {
                                                            Ext.getCmp('input_days_of_attendance_per_week').disable();
                                                        } else {
                                                            Ext.getCmp('input_days_of_attendance_per_week').enable();
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
                                                        width: 80,
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
                                layout: 'form',
                                hideLabel: true,
                                labelWidth: 1,
                                columnWidth: 0.35,
                                items: [
                                    // {
                                    //     xtype:'fieldset',
                                    //     title: 'Horário de atendimento ao público',
                                    //     hideLabel: true,
                                    //     collapsible: false,
                                    //     autoHeight:true,
                                    //     width: 440,
                                    //     items: [
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
                                                                id: "attendance_schedule1_initial",
                                                                name: "ao_attendance_schedule1_initial",
                                                                width: 100,
                                                                emptyText: 'HH:MM',
                                                                regex: /^([0-1][0-9]|2[0-3]):([0-5][0-9])$/,
                                                                regexText: 'Entrada inválida.<br/>Formato correto: <b>HH:MM</b>.',
                                                                maxLength: 5,
                                                                maxLengthText: 'Entrada inválida.<br/>Formato correto: <b>HH:MM</b>.',
                                                                listeners: {
                                                                    scope: this,
                                                                    blur: function(){
                                                                        if (Ext.getCmp('attendance_schedule1_initial').getValue().length == 2) {
                                                                            Ext.getCmp('attendance_schedule1_initial').setValue(Ext.getCmp('attendance_schedule1_initial').getValue()+':00');
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
                                                                name: "ao_attendance_schedule1_final",
                                                                width: 100,
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
                                                                id: "attendance_schedule2_initial",
                                                                name: "ao_attendance_schedule2_initial",
                                                                width: 100,
                                                                emptyText: 'HH:MM',
                                                                regex: /^([0-1][0-9]|2[0-3]):([0-5][0-9])$/,
                                                                regexText: 'Entrada inválida.<br/>Formato correto: <b>HH:MM</b>.',
                                                                maxLength: 5,
                                                                maxLengthText: 'Entrada inválida.<br/>Formato correto: <b>HH:MM</b>.',
                                                                listeners: {
                                                                    scope: this,
                                                                    blur: function(){
                                                                        if (Ext.getCmp('attendance_schedule2_initial').getValue().length == 2) {
                                                                            Ext.getCmp('attendance_schedule2_initial').setValue(Ext.getCmp('attendance_schedule2_initial').getValue()+':00');
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
                                                                name: "ao_attendance_schedule2_final",
                                                                width: 100,
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
                                    //     ]
                                    // },
                                ]
                            },
                            {
                                xtype:'panel',
                                autoHeight:true,
                                layout: 'form',
                                hideLabel: true,
                                labelWidth: 1,
                                columnWidth: 0.35,
                                items: [
                                    {
                                        xtype:'panel',
                                        autoHeight:true,
                                        labelWidth: 77,
                                        layout: 'form',
                                        items: [
                                            {
                                                xtype: 'textarea',
                                                fieldLabel: 'Observações',
                                                name: 'aoah_observation',
                                                hideLabel: false,
                                                allowBlank: true,
                                                width: 300,
                                                height: 50,
                                            },
                                        ]
                                    },
                                ]
                            },
                        ]
                    }
                ]
            });
        }
        return this._publicAttendanceForm;
    },

    getExistingRegistersGrid: function(cfg) {
        if(!this._existingRegistersGrid) {
            this._existingRegistersGrid = Ext._create('corregedoria.inspection.inspection.filling.administrativeorganization.existingregisters.Grid', {
                 region: 'center',
                 layout: 'form',
                 border: true,
                 height: 200,
                 fieldLabel: 'Livros/Sistemas',
                 gridAutoLoad: true,
                 columnAction: false,
                 hideItemsToolbar:['edit', 'download', '-', 'search'],
                 params: {inspection: cfg.values.inspection_id},
                doubleClickHandler: function() {},
            });
            this.getExistingRegistersGrid().setFilterProperty('inspection', cfg.values.inspection_id, 100);
        }
        return this._existingRegistersGrid;
    },

    getRegistrationSystemForm: function(cfg) {
        if(!this._registrationSystemForm) {
            this._registrationSystemForm = Ext._create('Ext.form.FieldSet', {
                title: '3.3. Sistema de Registro/Controle',
                collapsible: true,
                collapsed: false,
                autoHeight:true,
                labelWidth: 1,
                items:[
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
                                columnWidth: 0.30,
                                items: [
                                    {
                                        xtype:'radiogroup',
                                        fieldLabel: 'Tipo',
                                        columns: 1,
                                        items: [
                                            {
                                                xtype:'radio',
                                                inputValue: 1,
                                                boxLabel: 'Manual',
                                                checked: 1 == cfg.values.var_registration_type ? true : false,
                                                name: 'ao_registration_type'
                                            },
                                            {
                                                xtype:'radio',
                                                inputValue: 2,
                                                boxLabel: 'Informatizado',
                                                checked: 2 == cfg.values.var_registration_type ? true : false,
                                                name: 'ao_registration_type'
                                            },
                                            {
                                                xtype:'radio',
                                                inputValue: 3,
                                                boxLabel: 'Manual/Informatizado',
                                                checked: 3 == cfg.values.var_registration_type ? true : false,
                                                name: 'ao_registration_type'
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
                                                name: 'aors_observation',
                                                hideLabel: false,
                                                allowBlank: true,
                                                width: 245,
                                                height: 150,
                                            },
                                        ]
                                    },
                                ]
                            },
                            {
                                xtype:'panel',
                                autoHeight:true,
                                layout: 'form',
                                hideLabel: true,
                                labelWidth: 90,
                                columnWidth: 0.70,
                                items: [
                                    this.getExistingRegistersGrid(cfg),
                                ]
                            },
                        ]
                    }
                ]
            });
        }
        return this._registrationSystemForm;
    },

    getProceduresInProgressGrid: function(cfg) {
        if(!this._proceduresInProgress) {
            this._proceduresInProgress = Ext._create('corregedoria.inspection.inspection.filling.administrativeorganization.proceduresinprogress.Grid', {
                 region: 'center',
                 layout: 'form',
                 border: true,
                 height: 200,
                //  fieldLabel: 'Livros/Sistemas',
                 gridAutoLoad: true,
                 columnAction: false,
                 hideItemsToolbar:['edit', 'download', '-', 'search'],
                 params: {inspection: cfg.values.inspection_id},
                // doubleClickHandler: function() {},
            });
            this.getProceduresInProgressGrid().setFilterProperty('inspection', cfg.values.inspection_id, 100);
        }
        return this._proceduresInProgress;
    },

    getProceduresInProgressForm: function(cfg) {
        if(!this._proceduresInProgressForm) {
            this._proceduresInProgressForm = Ext._create('Ext.form.FieldSet', {
                title: '3.4. Relação de Procedimentos em Trâmite',
                collapsible: true,
                collapsed: false,
                autoHeight:true,
                labelWidth: 1,
                items:[
                    this.getProceduresInProgressGrid(cfg),
                ]
            });
        }
        return this._proceduresInProgressForm;
    },

    getArchivedProceduresGrid: function(cfg) {
        if(!this._archivedProcedures) {
            this._archivedProcedures = Ext._create('corregedoria.inspection.inspection.filling.administrativeorganization.archivedprocedures.Grid', {
                 region: 'center',
                 layout: 'form',
                 border: true,
                 height: 200,
                //  fieldLabel: 'Livros/Sistemas',
                 gridAutoLoad: true,
                 columnAction: false,
                 hideItemsToolbar:['edit', 'download', '-', 'search'],
                 params: {inspection: cfg.values.inspection_id},
                // doubleClickHandler: function() {},
            });
            this.getArchivedProceduresGrid().setFilterProperty('inspection', cfg.values.inspection_id, 100);
        }
        return this._archivedProcedures;
    },

    getArchivedProceduresForm: function(cfg) {
        if(!this._archivedProceduresForm) {
            this._archivedProceduresForm = Ext._create('Ext.form.FieldSet', {
                title: '3.5. Relação de Procedimentos Arquivados (nos últimos 06 meses)',
                collapsible: true,
                collapsed: false,
                autoHeight:true,
                labelWidth: 1,
                items:[
                    this.getArchivedProceduresGrid(cfg),
                ]
            });
        }
        return this._archivedProceduresForm;
    },

    getGeneralStatusForm: function(cfg) {
        if(!this._generalStatusForm) {
            this._generalStatusForm = Ext._create('Ext.form.FieldSet', {
                title: '3.6. Estado Geral da Organização do Órgão',
                collapsible: true,
                collapsed: false,
                autoHeight:true,
                labelWidth: 1,
                items:[
                    {
                        xtype:'radiogroup',
                        fieldLabel: '',
                        columns: 5,
                        items: [
                            {
                                xtype:'radio',
                                inputValue: 1,
                                boxLabel: 'Insuficiente',
                                checked: 1 == cfg.values.var_administrativeorganizationgeneralstatus ? true : false,
                                name: 'ao_administrativeorganizationgeneralstatus'
                            },
                            {
                                xtype:'radio',
                                inputValue: 2,
                                boxLabel: 'Regular',
                                checked: 2 == cfg.values.var_administrativeorganizationgeneralstatus ? true : false,
                                name: 'ao_administrativeorganizationgeneralstatus'
                            },
                            {
                                xtype:'radio',
                                inputValue: 3,
                                boxLabel: 'Bom',
                                checked: 3 == cfg.values.var_administrativeorganizationgeneralstatus ? true : false,
                                name: 'ao_administrativeorganizationgeneralstatus'
                            },
                            {
                                xtype:'radio',
                                inputValue: 4,
                                boxLabel: 'Muito Bom',
                                checked: 4 == cfg.values.var_administrativeorganizationgeneralstatus ? true : false,
                                name: 'ao_administrativeorganizationgeneralstatus'
                            },
                            {
                                xtype:'radio',
                                inputValue: 5,
                                boxLabel: 'Ótimo',
                                checked: 5 == cfg.values.var_administrativeorganizationgeneralstatus ? true : false,
                                name: 'ao_administrativeorganizationgeneralstatus'
                            },
                        ]
                    },
                ]
            });
        }
        return this._generalStatusForm;
    },

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});

        Ext.applyIf(cfg, {
            title: 'ORGANIZAÇÃO ADMINISTRATIVA',
            layout: 'form',
            frame: true,
            height: 535,
            border: false,
            autoScroll: true,
            overflow: 'auto',
            bodyStyle: 'padding: 5px',
            labelWidth: 1,
            items: [
                this.getOperatingHoursForm(cfg),
                this.getPublicAttendanceForm(cfg),
                this.getRegistrationSystemForm(cfg),
                this.getProceduresInProgressForm(cfg),
                this.getArchivedProceduresForm(cfg),
                this.getGeneralStatusForm(cfg),
            ],
        });

        Ext.apply(cfg, {

        });

        corregedoria.inspection.inspection.filling.administrativeorganization.Launcher.superclass.constructor.call(this, cfg);

    }
});
