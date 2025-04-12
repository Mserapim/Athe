/**
 *
 **/
Ext._define('common.siatu.chamado.transferencia.Window', {
    extend: 'core.RestfulWindow',

    rest: 'common.siatu.chamado.transferencia.Restful',

    width: 800,

    getPanelGerentes: function(){
        if(!this._panelGerentes) {
            this._panelGerentes = Ext._create('common.siatu.chamado.transferencia.PanelGerentes', {});
        }
        return this._panelGerentes
    },

    getAtendenteField: function(){
        if(!this._atendenteField) {
            this._atendenteField = Ext._create('core.fields.AutocompleteField', {
                rest: 'common.siatu.atendente.Restful',
                name: 'atendente_posterior',
                fieldLabel: 'Atendente',
                displayField: 'username',
                gridConfig: {
                    columnAction: false,
                    listeners: {
                        render: function(grid){
                            tbar = grid.getToolbar()
                            tbar.remove(tbar.getComponent(0))//Adicionar
                            tbar.remove(tbar.getComponent(0))//Remover
                        }
                    }
                }
            });
        }
        return this._atendenteField
    },

    getPanelAtendentes: function(){
        if(!this._panelAtendentes) {
            this._panelAtendentes = Ext._create('Ext.Panel', {
                layout: 'form',
                labelWidth: 70,
                border: false,
                items: [
                    this.getAtendenteField(),
                    {
                        xtype: 'textarea',
                        name: 'motivo',
                        fieldLabel: 'Motivo',
                        width: 300,
                        allowBlank: false,
                    }
                ]
            });
            this.width=410
        }    
        return this._panelAtendentes
    },

    getPanel: function(){
        if (this.super_user){
            return this.getPanelGerentes()
        }
        else{
            return this.getPanelAtendentes()
        }
    },

    getFormPanel: function() {
        if(!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                border: true,
                frame: true,
                items: [
                this.getPanel(),
                ],
            });

        return this._formPanel;
    },

    setParam: function(key, value) {
        this.params = core.nullValue(this.params, {});
        this.params[key] = value;
    },

    getParams: function() {
        if(this.getPanelGerentes().getParams().atendente_posterior=='old'){
            if (this.params!=undefined){
                delete this.params['atendente_posterior']
            }
            return core.nullValue(this.params, {})
        }
        return core.nullValue(Ext.apply(this.params,this.getPanelGerentes().getParams()), {});
    },

    constructor: function(cfg) {

        cfg = core.nullValue(cfg, {});
        this.super_user=cfg.super_user;

        common.siatu.chamado.transferencia.Window.superclass.constructor.call(this, cfg);
        
        if(this.getParams().chamado != undefined && this.super_user){
            this.getPanelGerentes().getListaAtendenteGrid().setFilterProperty('chamados', this.getParams().chamado);
            this.getPanelGerentes().setStoreAtendenteGrid(this.getParams().chamado)
        }

        if( (this.getParams().chamado != undefined) && (!this.super_user) ){
            var rest = Ext._create('common.siatu.atendente.Restful');
            this.getAtendenteField().setStore(
                Ext._create('Ext.data.Store', {
                    proxy: Ext._create('Ext.data.HttpProxy', {
                        api: {
                            read: core.callAction("SiatuAtendente", "action_atendentes_not_in_chamado", this.getParams().chamado)
                        },
                        disableCaching: false,
                        defaultHeaders: rest.defaultHeaders,
                    }),
                    reader: Ext._create('Ext.data.JsonReader', {
                        idProperty: 'pk',
                        root: 'collection',
                        totalProperty: 'count',
                        successProperty: 'success',
                        messageProperty: 'message',
                        fields: rest.getFields()
                    }),
                    autoLoad: true
                })
            )
        }
        

        if(this.action=='create')
            this.setParam('insert', true)
        else
            delete this.params['insert']

    }
});