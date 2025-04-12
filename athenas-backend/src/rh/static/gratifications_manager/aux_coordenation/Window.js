Ext._define('rh.gratifications_manager.aux_coordenation.Window', {
    extend: 'rh.movimentacao.pessoal.Window',

    rest: 'rh.gratifications_manager.aux_coordenation.Restful',

    width: 550,
    height: 470,

    constructor: function(cfg) {
        this.servidor_id = null;
        this.lotacao_id = null;
        if (cfg.values){
            this.servidor_id = cfg.values.servidor;
        }
        rh.gratifications_manager.aux_coordenation.Window.superclass.constructor.call(this, cfg);
    },

    getPanelInformationItems: function(cfg_window){
        var items = rh.gratifications_manager.aux_coordenation.Window.superclass.getPanelInformationItems.call(this, cfg_window);
        items.push(this.getDesignationField());
        items.push({
            xtype: 'choicefield',
            fieldLabel: 'Núcleo',
            allowBlank: true,
            hiddenName: 'nucleo',
            choiceId: 'rh.NUCLEO_CHOICES',
            disabled: true,
        });
        items.push(Ext._create('core.fields.AutocompleteField', {
            fieldLabel: "Substituto",
            allowBlank: true,
            rest: "rh.employee.Restful",
            name: "substituto"
        }));
        items.push(Ext._create('core.fields.AutocompleteField', {
            fieldLabel: "Publicação",
            allowBlank: false,
            rest: "rh.publicacao.Restful",
            name: "publicacao",
        }));
        items.push({
            allowBlank: true,
            fieldLabel: "Data Inicio *",
            name: "data_inicio",
            xtype: "datefield"
        });
        items.push({
            allowBlank: true,
            fieldLabel: "Data Fim",
            name: "data_fim",
            xtype: "datefield"
        });
        items.push({
            fieldLabel: "GEDOC",
            name: "gedoc",
            xtype: "textfield",
            allowBlank: true,
        });
        return items;
    },

    getTabPanel: function(cfg_window, cfg) {
        cfg = core.nullValue(cfg, {});
        Ext.applyIf(
            cfg,
            {
                height: 400,
            }
        );
        return rh.gratifications_manager.aux_coordenation.Window.superclass.getTabPanel.call(this, {}, cfg);
    },

    getEmployeeField: function(cfg_window, cfg){
        if(!this._employeeField){
            cfg = core.nullValue(cfg, {});
            Ext.applyIf(
                cfg,
                {
                    fieldLabel: 'Servidor *',
                    allowBlank: false,
                    rest: 'rh.employee.Restful',
                    name: 'servidor',
                    readOnly: false,
                    comboListeners: {
                        scope: this,
                        select: function(combo, record, index){
                            this._observe();
                        },
                        changevalid: function(combo, value, oldvalue, valid) {
                            this._observeEmployeeField(value);
                            try{
                                this.changeValidEmployeeField(combo, value, oldvalue, valid);
                            }catch(err){}
                        }
                    }
                }
            );
            Ext.apply(
                cfg,
                {
                    name: 'servidor',
                }
            );
            this._employeeField = Ext._create('rh.raw.AutocompleteField', cfg);
        }
        return this._employeeField;
    },

    _observeEmployeeField: function(value) {
        if(value){
            this.getDesignationField().setPreFilter([
                {property: 'ativo', value: true, stage: 1},
                {property: 'servidor', value: value, stage: 2},
                {property: 'designacao', value: true, stage: 3},
            ]);
        }
    },

    getDesignationField: function (cfg) {
        if (!this._designationField) {
            this._designationField = Ext._create('core.fields.AutocompleteField', {
                name: 'servidor_designacao',
                fieldLabel: 'Designação para gratificação *',
                allowBlank: false,
                rest: 'rh.gratifications_manager.aux_coordenation.workassignment.Restful',
                // preFilter: [
                //     {property: 'servidor', value: this.servidor_id, stage: 1},
                //     {property: 'servidores_lotacao__ativo', value: true, stage: 2},
                //     {property: 'servidores_lotacao__designacao', value: true, stage: 3},                    
                // ],
            });
        }

        return this._designationField;
    },

    getJobPosition: function(cfg_window, cfg) {
        if(!this._jobPositionField){
            cfg = core.nullValue(cfg, {});
            Ext.applyIf(
                cfg, 
            );
            this._jobPositionField = Ext._create('core.fields.AutocompleteField', cfg);
        }
        return this._jobPositionField;
    },
});