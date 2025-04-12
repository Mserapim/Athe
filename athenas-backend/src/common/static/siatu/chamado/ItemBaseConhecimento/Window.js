/**
 *
 **/
Ext._define('common.siatu.chamado.ItemBaseConhecimento.Window', {
    extend: 'core.RestfulWindow',

    rest: 'common.siatu.chamado.ItemBaseConhecimento.Restful',

    width: 450,

    getComboFilter: function() {
        if(!this._comboFilter) {
            this._comboFilter = Ext._create('core.fields.ComboField', {
                rest: 'common.siatu.BaseConhecimento.objeto.Restful',
                fieldLabel: 'Objeto',
                hiddenName: 'objeto',
                triggerAction: 'all',
                lazyRender: true,
                lazyInit: true,
                displayField: 'descricao',
                width: 325,
            });

            this._comboFilter.on({
                scope: this,
                changevalid:function(combo, id, start, valid) {
                    if (valid == true){
                        this.getComboFilterModelo().setPreFilter([
                            {property:'objetos',value: combo.getValue(), stage: 0},
                        ])
                        this.getComboFilterModelo().reset()
                        this.getComboFilterModelo().getStore().load({});
                        this.getBaseConhecimentoField().setPreFilter([
                            {property:'objeto',value: combo.getValue(), stage: 0},
                        ])
                        this.getBaseConhecimentoField().getComboField().getStore().load({});
                    }
                }
            });
        }
        return this._comboFilter;
    },

    getComboFilterModelo: function() {
        if(!this._comboFilterModelo) {
            this._comboFilterModelo = Ext._create('core.fields.ComboField', {
                rest: 'common.siatu.BaseConhecimento.modelo.Restful',
                fieldLabel: 'Modelo',
                hiddenName: 'modelo',
                triggerAction: 'all',
                lazyRender: true,
                lazyInit: true,
                displayField: 'descricao',
                width: 325,
            });

            this._comboFilterModelo.on({
                scope: this,
                change: function(combo, newValue, oldValue) {
                    this.getBaseConhecimentoField().setPreFilter([
                        {property:'objeto',value: this.getComboFilter().getValue(), stage: 0},
                        {property:'modelo',value:newValue, stage: 1},
                    ])
                    this.getBaseConhecimentoField().getComboField().getStore().load({})
                }
            });
        }
        return this._comboFilterModelo;
    },

    getBaseConhecimentoField: function(){
        if(!this._baseConhecimento){
            this._baseConhecimento = Ext._create('core.fields.AutocompleteField', {
                rest: 'common.siatu.BaseConhecimento.Restful',
                name: 'base_conhecimento',
                fieldLabel: 'Item',
                displayField: 'problema',
                allowBlank: true,
                width: 325,
                gridConfig: {
                    allowUpdate: false,
                    allowRemove: false,
                    hideItemsToolbar: ['edit', 'remove', 'download'],
                }
            });
        }

        return this._baseConhecimento;
    },

    getFormPanel: function(cfg) {
        if(!this._formPanel){
            var items;
            if (cfg.action == 'create') {
                items = [
                    this.getComboFilter(),
                    this.getComboFilterModelo(),
                    this.getBaseConhecimentoField()
                ]
            }
            else {
                items = [
                    {
                        xtype: 'textfield',
                        name: 'objeto_string',
                        fieldLabel: 'Objeto',
                        width: 475,
                        readOnly: true,
                    },
                    {
                        xtype: 'textfield',
                        name: 'modelo_string',
                        fieldLabel: 'Modelo',
                        width: 475,
                        readOnly: true,
                    },
                    {
                        xtype: 'textarea',
                        name: 'problema',
                        fieldLabel: 'Problema',
                        width: 476,
                        readOnly: true,
                    },
                    {
                        xtype: 'ckeditor',
                        name: 'solucao',
                        fieldLabel: 'Solução',
                        width: 476,
                        toolbar: [],
                        height: 140,
                    },
                ]
            }
            items = items.concat([{
                xtype: 'textfield',
                name: 'info',
                fieldLabel: 'Quantidade',
                width: (cfg.action == 'create') ? 325 : 475,
            }])

            this._formPanel = Ext._create('Ext.form.FormPanel', {
                border: false,
                frame: true,
                labelWidth: 80,
                items: items,
            });
        }

        return this._formPanel;
    },

    getButtons: function(cfg) {
        if(!this._buttons) {
            this._buttons = [
                {
                    text: 'Fechar',
                    scope: this,
                    handler: this.destroy
                }
            ];

            if(!cfg.disableSave)
                this._buttons = [{
                    text: 'Salvar',
                    scope: this,
                    handler: this.save,
                    handler: function() { this.save(true) }
                }].concat(this._buttons);

            if(cfg.action == 'create' && !cfg.disableSaveAndNew)
                this._buttons = [{
                    text: 'Salvar e novo',
                    scope: this,
                    handler: function() { this.save(false) }
                }].concat(this._buttons);
        }

        return this._buttons;
    },

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});
        if (cfg.action == 'update')
            this.width = 590

        if (Ext.util.Cookies.get('siatu-area-informatica') != null)
            this.filtroInformatica = Ext.decode(Ext.util.Cookies.get('siatu-area-informatica'));
        else
            this.filtroInformatica = false;

        common.siatu.chamado.ItemBaseConhecimento.Window.superclass.constructor.call(this, cfg);

        this.getComboFilter().setPreFilter([
            {property: 'informatica',value: this.filtroInformatica, stage: 1000}
        ])

        this.getComboFilterModelo().setPreFilter([
            {property: 'objetos',value: null, stage: 0}
        ])
    }
});
