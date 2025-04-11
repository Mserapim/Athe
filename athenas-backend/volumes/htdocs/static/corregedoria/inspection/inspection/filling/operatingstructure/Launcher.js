
Ext._define('corregedoria.inspection.inspection.filling.operatingstructure.Launcher', {
    extend: 'Ext.Panel',

    getOperatingLocationForm: function(cfg) {
        if(!this._operatingLocationForm) {
            this._operatingLocationForm = Ext._create('Ext.form.FieldSet', {
                title: '2.1. Local de Funcionamento',
                collapsible: true,
                collapsed: false,
                autoHeight:true,
                labelWidth: 1,
                items:[
                    {
                        xtype: 'textfield',
                        fieldLabel: 'Local de Funcionamento',
                        name: 'os_location',
                        hideLabel: true,
                        width: 1115,
                    },
                ]
            });
        }
        return this._operatingLocationForm;
    },

    getStructureEffetiveEmployeesGrid: function(cfg) {
        if(!this._structureEffetiveEmployeesGrid) {
            this._structureEffetiveEmployeesGrid = Ext._create('corregedoria.inspection.inspection.filling.structure.structureeffectiveemployees.Grid', {
                 region: 'center',
                 layout: 'form',
                 border: true,
                 height: 200,
                 gridAutoLoad: true,
                 columnAction: false,
                 hideItemsToolbar:['edit', 'download', '-', 'search'],
                 params: {inspection: cfg.values.inspection_id},
                doubleClickHandler: function() {},
            });
            this.getStructureEffetiveEmployeesGrid().setFilterProperty('inspection', cfg.values.inspection_id, 100);
        }
        return this._structureEffetiveEmployeesGrid;
    },

    getStructureCommissionedEmployeesGrid: function(cfg) {
        if(!this._structureCommissionedEmployeesGrid) {
            this._structureCommissionedEmployeesGrid = Ext._create('corregedoria.inspection.inspection.filling.structure.structurecommissionedemployees.Grid', {
                 region: 'center',
                 layout: 'form',
                 border: true,
                 height: 200,
                 gridAutoLoad: true,
                 columnAction: false,
                 hideItemsToolbar:['edit', 'download', '-', 'search'],
                 params: {inspection: cfg.values.inspection_id},
                 doubleClickHandler: function() {},
            });
            this.getStructureCommissionedEmployeesGrid().setFilterProperty('inspection', cfg.values.inspection_id, 100);
        }
        return this._structureCommissionedEmployeesGrid;
    },

    getStructureExternalPeoplesGrid: function(cfg) {
        if(!this._structureExternalPeoplesGrid) {
            this._structureExternalPeoplesGrid = Ext._create('corregedoria.inspection.inspection.filling.structure.structureexternalpeoples.Grid', {
                 region: 'center',
                 layout: 'form',
                 border: true,
                 height: 200,
                 gridAutoLoad: true,
                 columnAction: false,
                 hideItemsToolbar:['download', '-', 'search'],
                 // hideItemsToolbar:['edit', 'download', '-', 'search'],
                 params: {inspection: cfg.values.inspection_id},
                 doubleClickHandler: function() {},
            });
            this.getStructureExternalPeoplesGrid().setFilterProperty('inspection', cfg.values.inspection_id, 100);
        }
        return this._structureExternalPeoplesGrid;
    },
    // getStructureExternalEmployeesGrid: function(cfg) {
    //     if(!this._structureExternalEmployeesGrid) {
    //         this._structureExternalEmployeesGrid = Ext._create('corregedoria.inspection.inspection.filling.structure.structureexternalemployees.Grid', {
    //              region: 'center',
    //              layout: 'form',
    //              border: true,
    //              height: 200,
    //              gridAutoLoad: true,
    //              columnAction: false,
    //              hideItemsToolbar:['edit', 'download', '-', 'search'],
    //              params: {inspection: cfg.values.inspection_id},
    //              doubleClickHandler: function() {},
    //         });
    //         this.getStructureExternalEmployeesGrid().setFilterProperty('inspection', cfg.values.inspection_id, 100);
    //     }
    //     return this._structureExternalEmployeesGrid;
    // },

    getStaffStructureForm: function(cfg) {
        if(!this._staffStructureForm) {
            this._staffStructureForm = Ext._create('Ext.form.FieldSet', {
                title: '2.2. Pessoal de Apoio',
                collapsible: true,
                collapsed: false,
                autoHeight:true,
                labelWidth: 950,
                items:[
                    {
                        xtype:'fieldset',
                        title: 'Servidores Efetivos',
                        collapsible: false,
                        collapsed: false,
                        autoHeight:true,
                        width: 1115,
                        items:[
                            this.getStructureEffetiveEmployeesGrid(cfg),
                        ]
                    },
                    {
                        xtype:'fieldset',
                        title: 'Servidores Terceirizado/Cedido/Comissionado',
                        collapsible: false,
                        collapsed: false,
                        autoHeight:true,
                        width: 1115,
                        items:[
                            {
                                xtype:'fieldset',
                                title: 'Servidores Comissionados',
                                collapsible: false,
                                collapsed: false,
                                autoHeight:true,
                                width: 1090,
                                items:[
                                    this.getStructureCommissionedEmployeesGrid(cfg),
                                ]
                            },
                            {
                                xtype:'fieldset',
                                title: 'Servidores Cedidos/Terceirizados/Estagiários',
                                collapsible: false,
                                collapsed: false,
                                autoHeight:true,
                                width: 1090,
                                items:[
                                    this.getStructureExternalPeoplesGrid(cfg),
                                    // this.getStructureExternalEmployeesGrid(cfg),
                                ]
                            },
                        ]
                    },
                ]
            });
        }
        return this._staffStructureForm;
    },

    getStructureEquipmentGrid: function(cfg) {
        if(!this._structureEquipment) {
            this._structureEquipment = Ext._create('corregedoria.inspection.inspection.filling.operatingstructure.structureequipment.Grid', {
                region: 'center',
                layout: 'form',
                border: true,
                height: 200,
                gridAutoLoad: true,
                columnAction: false,
                hideItemsToolbar:['edit', 'download', '-', 'search'],
                params: {inspection: cfg.values.inspection_id},
            });
            this.getStructureEquipmentGrid().setFilterProperty('inspection', cfg.values.inspection_id, 100);
        }
        return this._structureEquipment;
    },

    getEquipmentForm: function(cfg) {
        if(!this._equipmentForm) {
            this._equipmentForm = Ext._create('Ext.form.FieldSet', {
                title: '2.3. Equipamentos Disponíveis',
                collapsible: true,
                collapsed: false,
                autoHeight:true,
                labelWidth: 1,
                items:[
                    this.getStructureEquipmentGrid(cfg),
                ]
            });
        }
        return this._equipmentForm;
    },

    getEditor: function (cfg) {
        if (!this._ckeditoField) {
            cfg = core.nullValue(cfg, {});
            Ext.apply(cfg, {
                allowBlank: true,
                startupFocus: false,
                editorConfig: {
                    forcePasteAsPlainText: true
                },
            });
            this._ckeditoField = Ext._create('toolkit.fields.CKEditor', cfg);
        }
        return this._ckeditoField;
    },

    getDeficiencyForm: function(cfg) {
        if(!this._deficiencyForm) {
            this._deficiencyForm = Ext._create('Ext.form.FieldSet', {
                title: '2.4. Relatar as Deficiências do Órgão (físicas, estruturais e de pessoal)',
                collapsible: true,
                collapsed: false,
                autoHeight:true,
                labelWidth: 1,
                items:[
                    this.getEditor({
                        name: 'os_deficiency',
                        width: 1100,
                        height: 250
                    })
                ]
            });
        }
        return this._deficiencyForm;
    },

    getGeneralStatusForm: function(cfg) {
        if(!this._generalStatusForm) {
            this._generalStatusForm = Ext._create('Ext.form.FieldSet', {
                title: '2.5. Estado Geral da Estrutura Física do Órgão',
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
                                checked: 1 == cfg.values.var_structuregeneralstatus ? true : false,
                                name: 'os_structuregeneralstatus'
                            },
                            {
                                xtype:'radio',
                                inputValue: 2,
                                boxLabel: 'Regular',
                                checked: 2 == cfg.values.var_structuregeneralstatus ? true : false,
                                name: 'os_structuregeneralstatus'
                            },
                            {
                                xtype:'radio',
                                inputValue: 3,
                                boxLabel: 'Bom',
                                checked: 3 == cfg.values.var_structuregeneralstatus ? true : false,
                                name: 'os_structuregeneralstatus'
                            },
                            {
                                xtype:'radio',
                                inputValue: 4,
                                boxLabel: 'Muito Bom',
                                checked: 4 == cfg.values.var_structuregeneralstatus ? true : false,
                                name: 'os_structuregeneralstatus'
                            },
                            {
                                xtype:'radio',
                                inputValue: 5,
                                boxLabel: 'Ótimo',
                                checked: 5 == cfg.values.var_structuregeneralstatus ? true : false,
                                name: 'os_structuregeneralstatus'
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
            title: 'ESTRUTURA DE FUNCIONAMENTO',
            layout: 'form',
            frame: true,
            height: 535,
            border: false,
            autoScroll: true,
            overflow: 'auto',
            bodyStyle: 'padding: 5px',
            labelWidth: 1,
            items: [
                this.getOperatingLocationForm(cfg),
                this.getStaffStructureForm(cfg),
                this.getEquipmentForm(cfg),
                this.getDeficiencyForm(cfg),
                this.getGeneralStatusForm(cfg),
            ],
        });

        Ext.apply(cfg, {

        });

        corregedoria.inspection.inspection.filling.operatingstructure.Launcher.superclass.constructor.call(this, cfg);

    }
});
