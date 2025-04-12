
Ext._define('corregedoria.inspection.inspection.filling.structure.Launcher', {
    extend: 'Ext.Panel',

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

    getStaffStructureForm: function(cfg) {
        if(!this._staffStructureForm) {
            this._staffStructureForm = Ext._create('Ext.form.FieldSet', {
                title: '1. Estrutura de Pessoal',
                collapsible: true,
                collapsed: false,
                autoHeight:true,
                labelWidth: 950,
                items:[
                    {
                        xtype:'fieldset',
                        title: '1.1 Servidores Efetivos',
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
                        title: '1.2 Servidores Terceirizado/Cedido/Comissionado',
                        collapsible: false,
                        collapsed: false,
                        autoHeight:true,
                        width: 1115,
                        items:[
                            {
                                xtype:'fieldset',
                                title: '1.2.1 Servidores Comissionados',
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
                                title: '1.2.2 Servidores Cedidos/Terceirizados/Estagiários',
                                collapsible: false,
                                collapsed: false,
                                autoHeight:true,
                                width: 1090,
                                items:[
                                  this.getStructureExternalPeoplesGrid(cfg),
                                ]
                            },
                        ]
                    },
                ]
            });
        }
        return this._staffStructureForm;
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
                title: '2. Espaço reservado para relatar as deficiências (físicas, estruturais e de pessoal) da Procuradoria/Promotoria de Justiça',
                collapsible: true,
                collapsed: false,
                autoHeight:true,
                labelWidth: 1,
                items:[
                    this.getEditor({
                        name: 'est_deficiency',
                        width: 1100,
                        height: 500
                    })
                ]
            });
        }
        return this._deficiencyForm;
    },

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});
        Ext.applyIf(cfg, {
            title: 'DA ESTRUTURA',
            layout: 'form',
            frame: true,
            height: 575,
            border: false,
            autoScroll: true,
            overflow: 'auto',
            bodyStyle: 'padding: 5px',
            items: [
                this.getStaffStructureForm(cfg),
                this.getDeficiencyForm(cfg),
            ],
        });
        Ext.apply(cfg, {

        });
        corregedoria.inspection.inspection.filling.structure.Launcher.superclass.constructor.call(this, cfg);
    }
});
